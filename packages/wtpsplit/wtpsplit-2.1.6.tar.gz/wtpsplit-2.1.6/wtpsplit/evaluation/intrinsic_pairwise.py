import copy
import json
from dataclasses import dataclass
from typing import List, Tuple
import os
import time
import random
import sys
import logging

import h5py
import torch
from datasets import load_dataset
from tqdm.auto import tqdm
from transformers import AutoModelForTokenClassification, HfArgumentParser
import numpy as np
import adapters

import wtpsplit.models  # noqa: F401
from wtpsplit.evaluation import evaluate_mixture, get_labels, train_mixture
from wtpsplit.evaluation.intrinsic_baselines import split_language_data
from wtpsplit.extract import PyTorchWrapper
from wtpsplit.extract_batched import extract_batched
from wtpsplit.utils import Constants, token_to_char_probs
from wtpsplit.evaluation.adapt import compute_statistics

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class Args:
    model_path: str
    adapter_path: str = None
    # eval data in the format:
    # {
    #    "<lang_code>": {
    #        "sentence": {
    #            "<dataset_name>": {
    #                 "meta": {
    #                     "train_data": ["train sentence 1", "train sentence 2"]
    #                 },
    #                 "data": ["test sentence 1", "test sentence 2"]
    #            }
    #        }
    #    }
    # }
    eval_data_path: str = "data/all_data.pth"
    valid_text_path: str = None  # "data/sentence/valid.parquet"
    device: str = "cpu"
    block_size: int = 512
    batch_size: int = 128
    include_langs: List[str] = None
    threshold: float = 0.01
    max_n_train_sentences: int = 1_000
    max_n_test_sentences: int = sys.maxsize
    save_suffix: str = ""
    skip_adaptation: bool = False
    keep_logits: bool = True
    skip_corrupted: bool = True
    skip_punct: bool = True
    return_indices: bool = True
    clf_from_scratch: bool = False

    # k_mer-specific args
    # k=2 means pairwise, k=3 triplets, ...
    k: int = 2
    max_n_samples: int = sys.maxsize
    sample_pct: float = 0.5
    min_k_mer_length: int = 0


def process_logits_k_mers(pairs, model, lang_code, block_size, batch_size, verbose=True) -> List[np.ndarray]:
    logits_list = []
    n_tokens_list = []
    # create batches of sentence pairs
    batched_k_mers = [pairs[i : i + batch_size] for i in range(0, len(pairs), batch_size)]
    for batch in tqdm(batched_k_mers, disable=not verbose):
        k_mer_texts = [Constants.SEPARATORS[lang_code].join(pair) for pair in batch]
        all_logits, offsets_mapping, tokenizer = extract_batched(
            k_mer_texts,
            model,
            lang_code=lang_code,
            block_size=block_size,
            batch_size=batch_size,
            pad_last_batch=True,
        )

        special_tokens = [tokenizer.cls_token, tokenizer.sep_token, tokenizer.pad_token]

        for k_mer, logit, offset_mapping in zip(k_mer_texts, all_logits, offsets_mapping):
            if "xlm" in model.config.model_type:
                tokens = tokenizer.tokenize(k_mer, verbose=False)

                # padding is also removed here (via offset_mapping)
                logits = token_to_char_probs(k_mer, tokens, logit, special_tokens, offset_mapping)
                logits_list.append(logits)
                n_tokens_list.append(len(tokens))
            else:
                if len(logit) < offset_mapping:
                    # truncated input --> pad back
                    logit = np.pad(
                        logit, ((0, offset_mapping - len(logit)), (0, 0)), "constant", constant_values=np.min(logit)
                    )
                # since we pad to equal length, we need to remove the padding
                logits_list.append(logit[:offset_mapping])

    return logits_list, n_tokens_list


def generate_k_mers(
    sentences: List[str],
    k: int,
    sample_pct: float = 1,
    max_n_samples: int = sys.maxsize,
    min_k_mer_length: int = 0,
) -> List[Tuple[str, ...]]:
    """Generate k-mers from a list of sentences.

    Args:
        sentences (List[str]): Input list of sentences.
        k (int): The number of sentences to include in each k-mer.
        sample_pct (float): Percentage of k-mers to sample.
        max_n_samples (int): Maximum number of k-mers to sample.
        min_k_mer_length (int): Minimum length of a k-mer.

    Returns:
        List[Tuple[str, ...]]: List of k-mers.
    """
    random.seed(42)
    n_k_mers = len(sentences) // k
    sample_size = min(round(n_k_mers * sample_pct), max_n_samples)

    # sample if needed
    if sample_size < n_k_mers:
        sampled_indices = set(random.sample(range(n_k_mers), sample_size))
        all_k_mers = [
            tuple(sentences[i * k + j] for j in range(k))
            for i in sampled_indices
            if sum(len(sentences[i * k + j]) for j in range(k)) > min_k_mer_length
        ]
    else:
        # all
        all_k_mers = [
            tuple(sentences[i + j] for j in range(k))
            for i in range(0, len(sentences) - k + 1, k)
            if sum(len(sentences[i + j]) for j in range(k)) > min_k_mer_length
        ]

    return all_k_mers


def load_or_compute_logits(args, model, eval_data, valid_data=None, save_str: str = None):
    logits_path = Constants.CACHE_DIR / "intrinsic_pairwise" / f"{save_str}.h5"

    if not os.path.exists(Constants.CACHE_DIR / "intrinsic_pairwise"):
        os.makedirs(Constants.CACHE_DIR / "intrinsic_pairwise")

    total_test_time = 0

    start_time = time.time()
    with h5py.File(logits_path, "a") as f, torch.no_grad():
        for lang_code in Constants.LANGINFO.index:
            if args.include_langs is not None and lang_code not in args.include_langs:
                continue
            print(f"Processing {lang_code}...")
            if lang_code not in f:
                lang_group = f.create_group(lang_code)
            else:
                lang_group = f[lang_code]

            # eval data
            for dataset_name, dataset in eval_data[lang_code]["sentence"].items():
                if args.skip_corrupted and "corrupted" in dataset_name and "ted2020" not in dataset_name:
                    continue
                if "-" in lang_code and "canine" in args.model_path and "no-adapters" not in args.model_path:
                    # code-switched data: eval 2x
                    lang_code = lang_code.split("_")[1].lower()
                try:
                    if args.adapter_path:
                        if args.clf_from_scratch:
                            model.model.classifier = torch.nn.Linear(model.model.classifier.in_features, 1)
                        elif args.model_path == "xlm-roberta-base" or args.model_path == "xlm-roberta-large":
                            # we train XLM-R using our wrapper, needs to be adapted for adapters to be loaded
                            model.model.classifier = torch.nn.Linear(
                                model.model.classifier.in_features,
                                1,
                            )
                            model.model.__class__.__name__ = "SubwordXLMForTokenClassification"
                        dataset_load_name = dataset_name
                        model.model.load_adapter(
                            args.adapter_path + "/" + dataset_load_name + "/" + lang_code,
                            set_active=True,
                            with_head=True,
                            load_as="text",
                        )
                except Exception as e:
                    print(f"Error loading adapter for {dataset_name} in {lang_code}: {e}")
                    continue
                print(dataset_name)
                if dataset_name not in lang_group:
                    dset_group = lang_group.create_group(dataset_name)
                else:
                    dset_group = lang_group[dataset_name]

                if "test_logits" not in dset_group:
                    test_sentences = dataset["data"][: args.max_n_test_sentences]
                    if not test_sentences:
                        continue
                    if isinstance(test_sentences[0], list):
                        continue
                    all_pairs_test = generate_k_mers(
                        test_sentences,
                        k=args.k,
                        sample_pct=args.sample_pct,
                        max_n_samples=args.max_n_samples,
                        min_k_mer_length=args.min_k_mer_length,
                    )

                    start_time = time.time()
                    test_logits, test_n_logits = process_logits_k_mers(
                        all_pairs_test,
                        model,
                        lang_code,
                        args.block_size,
                        args.batch_size,
                    )
                    end_time = time.time()

                    test_logit_lengths = []
                    # store start and end indices for each pair, used later to slice the logits
                    all_logit_lengths = np.append(0, np.cumsum([len(logits) for logits in test_logits]))
                    # append tuple of start and end indices for each pair
                    for i in range(len(test_logits)):
                        test_logit_lengths.append((all_logit_lengths[i], all_logit_lengths[i + 1] - 1))

                    test_logits = np.concatenate(test_logits)
                    total_test_time += end_time - start_time

                    # get_labels returns 2nd label at end of seq, which we do not want.
                    # label is at position -2 --> remove and add back 0 to end of sequence
                    test_labels = [
                        np.append(get_labels(lang_code, pair, after_space=False)[:-2], 0) for pair in all_pairs_test
                    ]

                    # flatten; append 0 eos to account for later indexing/slicing
                    test_labels = np.append(np.concatenate(test_labels), 0)
                    assert len(test_labels) == len(test_logits) + 1

                    dset_group.create_dataset("test_logits", data=test_logits)
                    dset_group.create_dataset("test_labels", data=test_labels)
                    dset_group.create_dataset("test_logit_lengths", data=test_logit_lengths)
                    dset_group.create_dataset("test_n_logits", data=test_n_logits)

                train_sentences = dataset["meta"].get("train_data")
                if train_sentences is not None and "train_logits" not in dset_group and not args.skip_adaptation:
                    train_sentences = train_sentences[: args.max_n_train_sentences]
                    all_pairs_train = generate_k_mers(
                        train_sentences,
                        k=args.k,
                        sample_pct=args.sample_pct,
                        max_n_samples=args.max_n_samples,
                        min_k_mer_length=args.min_k_mer_length,
                    )

                    train_logits, train_n_logits = process_logits_k_mers(
                        all_pairs_train, model, lang_code, args.block_size, args.batch_size
                    )
                    train_logits = np.concatenate(train_logits)

                    train_labels = [
                        np.append(get_labels(lang_code, pair, after_space=False)[:-2], 0) for pair in all_pairs_train
                    ]
                    train_labels = np.append(np.concatenate(train_labels), 0)
                    assert len(train_labels) == len(train_logits) + 1

                    dset_group.create_dataset("train_logits", data=train_logits)
                    dset_group.create_dataset("train_labels", data=train_labels)
                    dset_group.create_dataset("train_n_logits", data=train_n_logits)

    end_time = time.time()
    return h5py.File(logits_path, "r"), total_test_time / 60  # to minutes


def main(args):
    save_model_path = args.model_path
    if args.adapter_path:
        save_model_path = args.adapter_path
    save_str = f"{save_model_path.replace('/','_')}_b{args.block_size}_k{args.k}{args.save_suffix}"

    print(save_str)
    eval_data = torch.load(args.eval_data_path)
    if "canine" in args.model_path and "no-adapters" not in args.model_path:
        eval_data = split_language_data(eval_data)
    if args.valid_text_path is not None:
        valid_data = load_dataset("parquet", data_files=args.valid_text_path, split="train")
    else:
        valid_data = None

    print("Loading model...")
    model = PyTorchWrapper(AutoModelForTokenClassification.from_pretrained(args.model_path).to(args.device))
    if args.adapter_path:
        model_type = model.model.config.model_type
        # adapters need xlm-roberta as model type.
        model.model.config.model_type = "xlm-roberta"
        adapters.init(model.model)
        # reset model type (used later)
        model.model.config.model_type = model_type

    # first, logits for everything.
    f, total_test_time = load_or_compute_logits(args, model, eval_data, valid_data, save_str)
    save_str += f"_u{args.threshold}"

    # now, compute the intrinsic scores.
    results = {}
    clfs = {}
    if args.return_indices:
        indices = {}
    # lists to store scores for each metric across *all* languages
    u_scores, t_scores, punct_scores = [], [], []
    u_accs, t_accs, punct_accs = [], [], []
    thresholds_t, thresholds_adj = [], []

    for lang_code, dsets in tqdm(eval_data.items()):
        if args.include_langs is not None and lang_code not in args.include_langs:
            continue

        print(f"Predicting {lang_code}...")
        results[lang_code] = {}
        clfs[lang_code] = {}
        if args.return_indices:
            indices[lang_code] = {}

        for dataset_name, dataset in dsets["sentence"].items():
            sentences = dataset["data"][: args.max_n_test_sentences]
            if not sentences:
                continue
            if isinstance(sentences[0], list):
                continue
            sent_k_mers = generate_k_mers(
                sentences,
                k=args.k,
                sample_pct=args.sample_pct,
                max_n_samples=args.max_n_samples,
                min_k_mer_length=args.min_k_mer_length,
            )
            if lang_code not in f or dataset_name not in f[lang_code]:
                continue

            if "train_logits" in f[lang_code][dataset_name] and not args.skip_adaptation:
                feature_indices = None
                # it is sufficient to feed in 1 long sequence of tokens here since we only use logits for LR
                clf = train_mixture(
                    [lang_code],
                    f[lang_code][dataset_name]["train_logits"][:],
                    f[lang_code][dataset_name]["train_labels"][:],
                    features=feature_indices,
                    skip_punct=args.skip_punct,
                )
                # XXX: clf thresholds are still fitted on max. F1 score, not accuracy!
                # (but still without a positive label at the end)
                if clf[0] is not None:
                    print(clf)

                score_t = []
                score_punct = []
                # acc: average of correct 100% pairwise (or: k-mer) segmentation
                acc_t = []
                acc_punct = []

                # evaluate each pair
                for i, k_mer in enumerate(sent_k_mers):
                    start, end = f[lang_code][dataset_name]["test_logit_lengths"][i]
                    single_score_t, single_score_punct, info, t_indices, punct_indices = evaluate_mixture(
                        lang_code,
                        f[lang_code][dataset_name]["test_logits"][:][start:end],
                        list(k_mer),
                        args.return_indices,
                        0,
                        *clf,
                    )
                    score_t.append(single_score_t)
                    score_punct.append(single_score_punct)
                    acc_t.append(info["info_newline"]["correct_pairwise"] if info["info_newline"] else None)
                    acc_punct.append(info["info_transformed"]["correct_pairwise"] if info["info_transformed"] else None)

                clfs[lang_code][dataset_name] = clf

                clf = list(copy.deepcopy(clf))
                threshold_t = float(clf[-1])
                clf[-1] = args.threshold
            else:
                threshold_t = 0
                clf = [None, None, None, args.threshold]
                score_t = score_punct = None
                acc_t = acc_punct = None

            score_u = []
            acc_u = []
            thresholds = []
            u_indices, true_indices = [], []
            length = []
            for i, k_mer in enumerate(sent_k_mers):
                start, end = f[lang_code][dataset_name]["test_logit_lengths"][i]
                thresholds.append(args.threshold)
                single_score_u, _, info, cur_u_indices, _ = evaluate_mixture(
                    lang_code,
                    f[lang_code][dataset_name]["test_logits"][:][start:end],
                    list(k_mer),
                    args.return_indices,
                    0,
                    *clf,
                )
                score_u.append(single_score_u)
                acc_u.append(info["info_newline"]["correct_pairwise"])
                u_indices.append(cur_u_indices["pred_indices"] if cur_u_indices["pred_indices"] else [])
                true_indices.append(cur_u_indices["true_indices"] if cur_u_indices["true_indices"] else [])
                length.append(cur_u_indices["length"])

            score_u = np.mean(score_u)
            score_t = np.mean(score_t) if score_t and not args.skip_adaptation else None
            score_punct = (
                np.mean(score_punct) if score_punct and not (args.skip_punct or args.skip_adaptation) else None
            )
            acc_u = np.mean(acc_u)
            acc_t = np.mean(acc_t) if score_t else None
            acc_punct = np.mean(acc_punct) if score_punct else None
            threshold = np.mean(thresholds)

            results[lang_code][dataset_name] = {
                "u": score_u,
                "t": score_t,
                "punct": score_punct,
                "u_acc": acc_u,
                "t_acc": acc_t,
                "punct_acc": acc_punct,
                "threshold_t": threshold_t,
                "threshold_adj": threshold,
            }

            if args.return_indices:
                indices[lang_code][dataset_name] = {
                    "u": {"predicted_indices": u_indices, "true_indices": true_indices, "length": length},
                }
            # just for printing
            score_t = score_t or 0.0
            score_punct = score_punct or 0.0
            acc_t = acc_t or 0.0
            acc_punct = acc_punct or 0.0

            u_scores.append((score_u, lang_code))
            u_accs.append((acc_u, lang_code))
            t_scores.append((score_t, lang_code))
            t_accs.append((acc_t, lang_code))
            punct_scores.append((score_punct, lang_code))
            punct_accs.append((acc_punct, lang_code))
            thresholds_t.append((threshold_t, lang_code))
            thresholds_adj.append((threshold, lang_code))

            print(f"{lang_code} {dataset_name} {score_u:.3f} {score_t:.3f} {score_punct:.3f}")
            print(f"ACC: {acc_u:.3f} {acc_t:.3f} {acc_punct:.3f}")
            print(f"Threshold_t: {threshold_t:.3f} Threshold_adj: {threshold:.3f}")

    # Compute statistics for each metric across all languages
    results_avg = {
        "u": compute_statistics(u_scores),
        "t": compute_statistics(t_scores),
        "punct": compute_statistics(punct_scores),
        "u_acc": compute_statistics(u_accs),
        "t_acc": compute_statistics(t_accs),
        "punct_acc": compute_statistics(punct_accs),
        "threshold_t": compute_statistics(thresholds_t),
        "threshold_adj": compute_statistics(thresholds_adj),
        "include_langs": args.include_langs,
    }

    json.dump(
        results,
        open(
            Constants.CACHE_DIR / "intrinsic_pairwise" / f"{save_str}.json",
            "w",
        ),
        indent=4,
    )

    json.dump(
        results_avg,
        open(
            Constants.CACHE_DIR / "intrinsic_pairwise" / f"{save_str}_AVG.json",
            "w",
        ),
        indent=4,
    )

    if args.return_indices:
        json.dump(
            indices,
            open(
                Constants.CACHE_DIR / "intrinsic_pairwise" / f"{save_str}_IDX.json",
                "w",
            ),
            default=int,
            indent=4,
        )
        print(Constants.CACHE_DIR / "intrinsic_pairwise" / f"{save_str}_IDX.json")
        print("Indices saved to file.")
    if not args.keep_logits:
        os.remove(f.filename)

    print(results_avg)
    print(save_str)
    return results, results_avg, total_test_time


if __name__ == "__main__":
    (args,) = HfArgumentParser([Args]).parse_args_into_dataclasses()
    results, results_avg, total_test_time = main(args)
    print(total_test_time)
