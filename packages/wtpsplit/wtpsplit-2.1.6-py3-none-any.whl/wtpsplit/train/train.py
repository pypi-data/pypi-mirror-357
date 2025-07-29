import logging
import math
import os
import random
import shutil
import sys

# import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import partial
from glob import glob
from typing import List, Optional

import datasets
import numpy as np
import torch
import transformers
from datasets import load_dataset

# from datasets.download import DownloadConfig
from tokenizers import AddedToken
from torchinfo import summary
from tqdm.auto import tqdm
from transformers import AutoTokenizer, HfArgumentParser, TrainingArguments, set_seed
from transformers.trainer import is_torch_tpu_available

import wandb
from wtpsplit.models import (
    BertCharConfig,
    BertCharForTokenClassification,
    LACanineConfig,
    LACanineForTokenClassification,
    SubwordXLMConfig,
    SubwordXLMForTokenClassification,
)
from wtpsplit.train.evaluate import evaluate_sentence
from wtpsplit.train.trainer import Trainer
from wtpsplit.train.utils import Model

# from wtpsplit.train.utils import cleanup_cache_files
from wtpsplit.utils import Constants, LabelArgs, corrupt_training, get_label_dict, get_subword_label_dict

logger = logging.getLogger(__name__)


def setup_logging(training_args: transformers.TrainingArguments) -> None:
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    log_level = training_args.get_process_log_level()
    logger.setLevel(log_level)
    datasets.utils.logging.set_verbosity_warning()
    transformers.utils.logging.set_verbosity_warning()
    transformers.utils.logging.enable_default_handler()
    transformers.utils.logging.enable_explicit_format()
    # Log on each process the small summary:
    logger.warning(
        (
            f"Process rank: {training_args.local_rank}, device: {training_args.device}, n_gpu: {training_args.n_gpu}"
            + f"distributed training: {training_args.local_rank != -1}, 16-bits training: {training_args.fp16}"
        )
    )


@dataclass
class Args:
    model_name_or_path: str
    shuffle: bool = False
    use_logits: bool = False
    is_decoder: bool = False
    use_bert: bool = False
    train_text_path: str = "data/train.parquet"
    valid_text_path: str = "data/valid.parquet"
    include_languages: List[str] = None
    eval_data_path: str = "data/all_data.pth"
    num_hidden_layers: int = 3
    preprocessing_num_workers: int = 6
    block_size: int = 512
    overflow_size: int = 16
    eval_stride: int = 256
    loss_margin: float = 0.5
    from_scratch: bool = False
    pack_samples: bool = False
    one_sample_per_line: bool = False
    use_loss_weights: bool = False
    do_sentence_training: bool = True
    do_auxiliary_training: bool = True
    aux_training_weight: float = 1.0
    ignore_non_hyphen: bool = False
    non_punctuation_sample_ratio: float = None
    text_column: str = "text"
    threshold: float = 0.01  # just for eval
    # WtP-related args
    ngram_order: int = 1
    language_adapter: str = "on"
    adapter_warmup_steps: int = 0
    adapter_lr_multiplier: float = 1.0
    # SaT-related args
    use_subwords: bool = False  # uses XLM-R
    lookahead: int = None
    lookahead_split_layers: Optional[int] = None
    sample_non_whitespace: int = 1


def collate_fn(batch, args, label_args, label_dict, tokenizer, add_lang_ids: bool = False):
    all_input_ids = []
    all_labels = []
    all_language_ids = []

    all_attention_masks = []
    all_position_ids = []
    all_label_weights = []

    for sample in batch:
        # subword-level
        if args.use_subwords:
            # already tokenized!
            input_ids = sample["input_ids"]
        # char-level
        else:
            input_ids = [ord(c) for c in sample["input_ids"]]
        lang = sample["lang"]

        while len(input_ids) < args.block_size + args.overflow_size:
            if tokenizer:
                input_ids.append(tokenizer.pad_token_id)
            else:
                input_ids.append(0)

        block_ids = [0] * len(input_ids)

        input_ids, _, labels = corrupt_training(
            input_ids,
            block_ids,
            lang,
            label_args,
            label_dict=label_dict,
            pack_samples=args.pack_samples,
            # min_length=args.block_size,
            tokenizer=tokenizer if args.use_subwords else None,
        )

        actual_block_size = args.block_size - 2 if args.use_subwords else args.block_size

        if len(input_ids) > args.block_size:
            start = np.random.randint(0, len(input_ids) - actual_block_size)
            input_ids = input_ids[start : start + actual_block_size]
            labels = labels[start : start + actual_block_size]
        elif len(input_ids) < actual_block_size:
            padding = actual_block_size - len(input_ids)
            input_ids += [tokenizer.pad_token_id] * padding if tokenizer else [0] * padding
            labels += [0] * padding

        if tokenizer:
            input_ids = [tokenizer.cls_token_id] + input_ids[:actual_block_size] + [tokenizer.sep_token_id]
            # labels for CLS and SEP tokens are 0 (none)
            labels = [0] + labels[:actual_block_size] + [0]
        else:
            input_ids = input_ids[:actual_block_size]
            labels = labels[:actual_block_size]

        input_ids = torch.tensor(input_ids, dtype=torch.long)
        labels = torch.tensor(labels, dtype=torch.long)
        position_ids = torch.arange(len(input_ids), dtype=torch.long)
        label_weights = torch.ones(args.block_size, dtype=torch.float32)
        if tokenizer:
            attention_mask = (input_ids != tokenizer.pad_token_id).to(torch.float32)
        else:
            attention_mask = (input_ids != 0).to(torch.float32)

        all_input_ids.append(input_ids)
        all_label_weights.append(label_weights)
        all_labels.append(labels)
        all_language_ids.append(Constants.LANG_CODE_TO_INDEX[lang] if add_lang_ids else 0)

        all_attention_masks.append(attention_mask)
        all_position_ids.append(position_ids)

    out = {
        "input_ids": torch.stack(all_input_ids, 0),
        "attention_mask": torch.stack(all_attention_masks, 0),
        "position_ids": torch.stack(all_position_ids, 0),
        "language_ids": torch.tensor(all_language_ids, dtype=torch.long),
        "label_weights": torch.stack(all_label_weights, 0),
        "labels": torch.stack(all_labels, 0),
    }

    return out


def main():
    parser = HfArgumentParser([Args, TrainingArguments, LabelArgs])

    if sys.argv[1].endswith(".json"):
        (args, training_args, label_args) = parser.parse_json_file(sys.argv[1])
        wandb_name = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    else:
        (args, training_args, label_args) = parser.parse_args_into_dataclasses()
        wandb_name = None

    if is_torch_tpu_available():
        import torch_xla.core.xla_model as xm

        world_size = xm.xrt_world_size()
        if world_size == 4:
            # ensure same batch size on TPUv3 and TPUv4 using same config.json
            training_args.per_device_train_batch_size *= 2
    elif torch.cuda.is_available():
        world_size = torch.cuda.device_count()
    else:
        world_size = 1

    logger.warning(f"Per device train batch size: {training_args.per_device_train_batch_size}")
    logger.warning(
        f"Total train batch size: {training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps * world_size}"
    )

    setup_logging(training_args)
    set_seed(training_args.seed)
    training_args.hub_strategy = "end"
    training_args.save_total_limit = 1

    num_labels = Constants.AUX_OFFSET + ((1 + len(Constants.PUNCTUATION_CHARS)) if args.do_auxiliary_training else 0)
    if args.use_subwords:
        # SaT models
        if args.from_scratch:
            config = SubwordXLMConfig(
                args.model_name_or_path,
                num_hidden_layers=args.num_hidden_layers,
                num_labels=num_labels,
                lookahead=args.lookahead,
                lookahead_split_layers=args.lookahead_split_layers,
            )
            backbone = SubwordXLMForTokenClassification(config)

        else:
            config = SubwordXLMConfig.from_pretrained(
                args.model_name_or_path,
                num_hidden_layers=args.num_hidden_layers,
                num_labels=num_labels,
                lookahead=args.lookahead,
                lookahead_split_layers=args.lookahead_split_layers,
            )
            backbone = SubwordXLMForTokenClassification.from_pretrained(
                args.model_name_or_path,
                config=config,
            )

        backbone.config.base_model = args.model_name_or_path
        tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path)
        # needed since we create labels in collate_fn based on tokens
        tokenizer.add_special_tokens({"additional_special_tokens": [AddedToken("\n")]})
        custom_token_id = tokenizer.convert_tokens_to_ids("\n")
        # used later to filter out special tokens
        special_tokens_ids = set(tokenizer.all_special_ids)
        special_tokens_ids.discard(custom_token_id)
        if args.lookahead:
            # we split lookahead evenly into N layers
            assert args.lookahead % args.num_hidden_layers == 0

    else:
        # WtP models (char-based)
        tokenizer = None
        config = LACanineConfig.from_pretrained(
            args.model_name_or_path,
            raw_lookahead=args.lookahead,
            num_hidden_layers=args.num_hidden_layers,
            num_labels=num_labels,
            n_languages=len(Constants.LANG_CODE_TO_INDEX),
            ngram_order=args.ngram_order,
            language_adapter=args.language_adapter,
            # upsampling kernel size > 1 is problematic for packing
            # using ks=1 doesn't allow reusing the pretrained weights
            # but if we warm it up alongside the adapters
            # there is almost no difference.
            upsampling_kernel_size=1,
        )
        if args.use_bert:
            config = BertCharConfig.from_pretrained(
                args.model_name_or_path,
                num_labels=num_labels,
            )
            backbone = BertCharForTokenClassification(config)
        elif args.from_scratch:
            backbone = LACanineForTokenClassification(config)
        else:
            backbone = LACanineForTokenClassification.from_pretrained(
                args.model_name_or_path, ignore_mismatched_sizes=True, config=config
            )

    model = Model(
        backbone,
        loss_margin=args.loss_margin,
        use_loss_weights=args.use_loss_weights,
        do_sentence_training=args.do_sentence_training,
        do_auxiliary_training=args.do_auxiliary_training,
        aux_training_weight=args.aux_training_weight,
    )

    if training_args.local_rank == 0:
        logger.warning(summary(model, depth=4))

    def prepare_dataset(
        num_workers=1,
        include_languages=None,
        shuffle=False,
        split="train",
    ):
        with training_args.main_process_first():
            # this can be used if space issues arise
            # dlconf = DownloadConfig(cache_dir="/home/Markus/.cache/huggingface/datasets")
            # dataset = load_dataset("markus583/mC4-TEST", split=split, download_config=dlconf)
            dataset = load_dataset("markus583/mC4-TEST", split=split)
        logger.warning(f"Loaded {split} dataset.")
        # optional: delete downloaded dataset, it is stored in cache_dir now (but we delete it later)
        # ~40GB on disk
        # os.system("rm -rf /home/Markus/.cache/huggingface/datasets")

        if include_languages is not None:
            include_languages = set(include_languages)

            dataset = dataset.filter(
                lambda example: example["lang"] in include_languages,
                num_proc=args.preprocessing_num_workers,
            )
            logger.warning(f"Filtered to {len(dataset)} examples.")

        if shuffle:
            dataset = dataset.shuffle(seed=42)
            logger.warning("Shuffled dataset.")

        # not used for sentence segmentation, ignore.
        if args.ignore_non_hyphen:
            with training_args.main_process_first():
                dataset = dataset.filter(
                    lambda sample: any(c in sample[args.text_column] for c in label_args.hyphen_chars),
                    num_proc=args.preprocessing_num_workers,
                )
                logger.info(f"Filtered to {len(dataset)} examples.")

        # "punctuation-specific sampling" in the WtP paper
        if args.non_punctuation_sample_ratio is not None:
            languages_without_punctuation = {
                lang_code
                for lang_code in Constants.LANGINFO.index
                if Constants.LANGINFO.loc[lang_code, "no_punctuation"]
            }

            def drop_some_non_punctuation_samples(examples):
                include_indices = set(
                    np.where([lang_code not in languages_without_punctuation for lang_code in examples["lang"]])[0]
                )
                punctuation_indices = {
                    i for i in np.where(examples["ends_with_punctuation"])[0] if i in include_indices
                }

                target_n_non_punct = int(
                    (len(punctuation_indices) * args.non_punctuation_sample_ratio)
                    / (1 - args.non_punctuation_sample_ratio)
                )
                n_drop = (len(include_indices) - len(punctuation_indices)) - target_n_non_punct

                out = [True for _ in range(len(examples["ends_with_punctuation"]))]

                if n_drop <= 0:
                    return out
                drop_indices = np.random.choice(
                    list(include_indices - punctuation_indices),
                    n_drop,
                    replace=False,
                )

                for i in drop_indices:
                    out[i] = False

                return out

            with training_args.main_process_first():
                dataset = dataset.filter(
                    drop_some_non_punctuation_samples,
                    batched=True,
                    batch_size=1_000_000,
                    num_proc=num_workers,
                )

        def tokenize_texts(examples):
            # do not return CLS and SEP token here
            # there should only be 1 of these per block later, not multiple
            # we still can't use return_special_tokens=False since we need the \n token later for the labels
            tokenized = tokenizer(examples[args.text_column], verbose=False)
            return {"input_ids": [example[1:-1] for example in tokenized["input_ids"]]}

        # similar to group_texts in huggingface's run_clm.py / run_mlm.py: https://github.com/huggingface/transformers/blob/main/examples/pytorch/language-modeling/run_mlm.py
        def group_texts(examples):
            all_input_blocks = []
            all_input_block_lengths = []
            all_langs = []

            def maybe_pad(text):
                if args.pack_samples:
                    padding = config.downsampling_rate - (len(text) % config.downsampling_rate)
                    if padding == config.downsampling_rate:
                        padding = 0

                    text += chr(0) * padding

                return text

            for current_lang in set(examples["lang"]):
                if not args.use_subwords:
                    lang_texts = [
                        maybe_pad(text)
                        for text, lang in zip(examples["input_ids"], examples["lang"])
                        if lang == current_lang
                    ]
                else:
                    # only retain current_lang examples (all columns)
                    lang_subwords = [
                        subwords
                        for subwords, lang in zip(examples["input_ids"], examples["lang"])
                        if lang == current_lang
                    ]
                    # filter out some special tokens
                    # from html tags, mostly in Latin, Thai & Korean
                    lang_subwords = [
                        [subword for subword in subwords if subword not in special_tokens_ids]
                        for subwords in lang_subwords
                    ]
                # pack_samples used for the compound part, so irrelevant
                if args.pack_samples:
                    if args.use_subwords:
                        raise NotImplementedError
                    blocks = []
                    block_ids = []

                    current_block = ["", []]

                    for i, text in enumerate(lang_texts):
                        if len(text) > args.block_size:
                            continue

                        current_block[0] += text
                        current_block[1] += [i] * len(text)

                        if i + 1 < len(lang_texts) and len(current_block[0]) + len(lang_texts[i + 1]) > args.block_size:
                            padding = args.block_size - len(current_block[0])

                            current_block[0] += chr(0) * padding
                            current_block[1] += [i] * padding
                            blocks.append(current_block[0])
                            block_ids.append(current_block[1])

                            current_block = ["", []]

                    if len(current_block[0]) > 0:
                        padding = args.block_size - len(current_block[0])

                        current_block[0] += chr(0) * padding
                        current_block[1] += [i] * padding
                        blocks.append(current_block[0])
                        block_ids.append(current_block[1])
                else:
                    if not args.use_subwords:
                        concatenated_texts = "".join(lang_texts)
                        concatenated_ids = [i for i, text in enumerate(lang_texts) for _ in text]
                    else:
                        # concatenate token lists
                        concatenated_texts = [item for sublist in lang_subwords for item in sublist]
                        concatenated_ids = [i for i, subwords in enumerate(lang_subwords) for _ in subwords]

                    total_length = len(concatenated_texts)

                    best_length = math.ceil(total_length / args.block_size) * args.block_size + args.overflow_size
                    while best_length > total_length:
                        best_length -= args.block_size

                    if best_length < 0:
                        continue

                    concatenated_texts = concatenated_texts[:best_length]
                    concatenated_ids = concatenated_ids[:best_length]

                    blocks = [
                        concatenated_texts[i : i + args.block_size + args.overflow_size]
                        for i in range(0, best_length - args.block_size, args.block_size)
                    ]
                    block_ids = [
                        concatenated_ids[i : i + args.block_size + args.overflow_size]
                        for i in range(0, best_length - args.block_size, args.block_size)
                    ]

                block_langs = [current_lang] * len(blocks)

                all_input_blocks.extend(blocks)
                all_input_block_lengths.extend([list(Counter(ids).values()) for ids in block_ids])
                all_langs.extend(block_langs)

                if args.sample_non_whitespace > 1:
                    separator = Constants.SEPARATORS.get(current_lang, " ")
                    if separator == "":
                        for i in range(args.sample_non_whitespace - 1):
                            all_input_blocks.extend(blocks)
                            all_input_block_lengths.extend([list(Counter(ids).values()) for ids in block_ids])
                            all_langs.extend(block_langs)

            return {
                "input_ids": all_input_blocks,
                "block_lengths": all_input_block_lengths,
                "lang": all_langs,
            }

        if args.do_auxiliary_training:
            assert label_args.use_auxiliary

        if args.pack_samples:
            assert not args.one_sample_per_line

        if args.use_subwords:
            with training_args.main_process_first():
                dataset = dataset.map(
                    tokenize_texts,
                    batched=True,
                    num_proc=num_workers,
                    remove_columns=[args.text_column],
                )
        else:
            # this column is no longer used and would cause an error otherwise
            with training_args.main_process_first():
                dataset = dataset.rename_column(args.text_column, "input_ids")
        logger.warning(f"Tokenized {split} dataset.")

        # uncomment if space issues arise (e.g., on TPU VMs):
        # if split == "train" and args.use_subwords:
        #     with training_args.main_process_first():
        #         for root, dirs, files in os.walk(os.environ.get("HF_DATASETS_CACHE")):
        #             for file in files:
        #                 if file.startswith("m_c4-test-train"):
        #                     logger.warning(f"Removing {os.path.join(root, file)}")
        #                     os.remove(os.path.join(root, file))

        if not args.one_sample_per_line:
            with training_args.main_process_first():
                dataset = dataset.map(
                    group_texts,
                    batched=True,
                    num_proc=num_workers,
                    # a bit hacky but oh well, only drop if sentence
                    remove_columns=["ends_with_punctuation"] if args.text_column == "text" else [],
                )
        logger.warning(f"Grouped {split} dataset.")

        return dataset

    valid_dataset = prepare_dataset(
        num_workers=args.preprocessing_num_workers,
        include_languages=args.include_languages,
        shuffle=False,
        split="valid",
    )
    logger.warning(f"Valid dataset has {len(valid_dataset)} examples.")

    train_dataset = prepare_dataset(
        num_workers=args.preprocessing_num_workers,
        include_languages=args.include_languages,
        shuffle=args.shuffle,
        split="train",
    )
    logger.warning(f"Train dataset has {len(train_dataset)} examples.")

    # print some samples from the dataset
    count = 0
    while count < 5:
        index = random.choice(range(len(train_dataset)))
        sample = train_dataset[index]

        logger.warning(f"Sample {index} of the training set: {sample}.")
        if tokenizer:
            logger.warning(tokenizer.decode(sample["input_ids"]))
        count += 1

    eval_data = torch.load(
        args.eval_data_path,
    )

    def compute_metrics(trainer):
        metrics = {}
        avg_metrics = defaultdict(lambda: [])

        model = trainer._wrap_model(trainer.model, training=False)

        for lang_code, lang_data in tqdm(eval_data.items(), desc="Evaluate!"):
            if args.include_languages is not None and lang_code not in args.include_languages:
                continue

            if trainer.args.process_index == 0 and args.do_sentence_training:
                for dataset_name, dataset in lang_data["sentence"].items():
                    if not dataset["data"][0]:
                        continue

                    if isinstance(dataset["data"][0], list):
                        # too slow here
                        continue
                    score, info = evaluate_sentence(
                        lang_code,
                        dataset["data"],
                        model,
                        stride=args.eval_stride,
                        block_size=args.block_size,
                        batch_size=training_args.per_device_eval_batch_size,
                        threshold=args.threshold,
                    )
                    metrics[f"{lang_code}_{dataset_name}_pr_auc"] = score
                    metrics[f"{lang_code}_{dataset_name}_f1"] = info["f1"]
                    metrics[f"{lang_code}_{dataset_name}_f1_best"] = info["f1_best"]
                    metrics[f"{lang_code}_{dataset_name}_threshold_best"] = info["threshold_best"]
                    avg_metrics[f"average_{dataset_name}_pr_auc"].append(score)
                    avg_metrics[f"average_{dataset_name}_f1"].append(info["f1"])
                    avg_metrics[f"average_{dataset_name}_f1_best"].append(info["f1_best"])
                    avg_metrics[f"average_{dataset_name}_threshold_best"].append(info["threshold_best"])

                    if lang_code in ["zh", "ja", "my", "km"]:
                        avg_metrics[f"average_nonwhitespace_{dataset_name}_pr_auc"].append(score)
                        avg_metrics[f"average_nonwhitespace_{dataset_name}_f1"].append(info["f1"])
                        avg_metrics[f"average_nonwhitespace_{dataset_name}_f1_best"].append(info["f1_best"])
                        avg_metrics[f"average_nonwhitespace_{dataset_name}_threshold_best"].append(
                            info["threshold_best"]
                        )
                    else:
                        avg_metrics[f"average_whitespace_{dataset_name}_pr_auc"].append(score)
                        avg_metrics[f"average_whitespace_{dataset_name}_f1"].append(info["f1"])
                        avg_metrics[f"average_whitespace_{dataset_name}_f1_best"].append(info["f1_best"])
                        avg_metrics[f"average_whitespace_{dataset_name}_threshold_best"].append(info["threshold_best"])

        for name, values in avg_metrics.items():
            if len(values) > 1:
                metrics[name] = np.mean(values)

        return metrics

    if "wandb" in training_args.report_to and training_args.process_index == 0:
        wandb.init(name=wandb_name, project="sentence")
        wandb.config.update(args)
        wandb.config.update(training_args)
        wandb.config.update(label_args)

        model.config.wandb_run_id = wandb.run.id

        for file in glob(os.path.join(os.path.dirname(__file__), "*.py")):
            wandb.save(os.path.abspath(file), policy="now")
            # also 1 dir above
            wandb.save(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", file)), policy="now")

    label_dict = get_subword_label_dict(label_args, tokenizer) if args.use_subwords else get_label_dict(label_args)
    logger.info(f"Label dict has {len(label_dict)} entries.")

    # needed in the trainer
    training_args.adapter_warmup_steps = args.adapter_warmup_steps
    training_args.adapter_lr_multiplier = args.adapter_lr_multiplier

    # again: uncomment this if space issues arise.
    # give .map in multiprocessing enough of time to finish, to be safe
    # time.sleep(10)
    # if training_args.local_rank == 0:
    #     # since both share the *same* cache_dir, we cannot simply call dataset.cleanup_cache_files()
    #     # because that would remove the cache files of the other dataset!
    #     cleanup_cache_files([train_dataset, valid_dataset])
    #     logger.warning("Cleaned up cache files.")
    # time.sleep(10)

    trainer = Trainer(
        model,
        training_args,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        compute_metrics=compute_metrics,
        data_collator=partial(
            collate_fn,
            args=args,
            label_args=label_args,
            label_dict=label_dict,
            tokenizer=tokenizer if args.use_subwords else None,
            add_lang_ids=not args.use_subwords,
        ),
    )

    trainer.train(resume_from_checkpoint=training_args.resume_from_checkpoint)
    trainer.save_model()
    trainer.save_state()

    # remove old checkpoints to save space
    checkpoint_pattern = os.path.join(training_args.output_dir, "checkpoint-*")

    for checkpoint_dir in glob(checkpoint_pattern):
        if os.path.isdir(checkpoint_dir):
            shutil.rmtree(checkpoint_dir)


def _mp_fn(index):
    # For xla_spawn (TPUs)
    main()


if __name__ == "__main__":
    main()
