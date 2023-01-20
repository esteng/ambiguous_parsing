from jsonargparse import ArgumentParser, ActionConfigFile
import json 
import pdb 
import pathlib 
from collections import defaultdict 
from typing import List, Dict

import numpy as np 
np.random.seed(12)

from ambiguous_parsing.generation.generate_pairs import generate_pp_pairs, generate_conjunction_pairs, generate_scope_pairs, generate_unambiguous

def process_split_ratio(split_ratio):
    split_ratio = split_ratio.split(":")
    split_ratio = [float(x) for x in split_ratio]
    return split_ratio

class RandomSampler:
    def __init__(self, train_n, split_ratios, perc_ambig, shuffle=True):
        self.train_n = train_n
        self.split_ratios = process_split_ratio(split_ratios)
        self.dev_num = int(self.train_n/self.split_ratios[0] * self.split_ratios[1])
        self.test_num = int(self.train_n/self.split_ratios[0] * self.split_ratios[2])

        self.perc_ambig = perc_ambig
        self.shuffle = shuffle

    def sample(self, ambiguous_data, unambiguous_data):
        # sample train_n examples from ambiguous_data
        # sample dev_num examples from ambiguous_data
        # sample test_num examples from ambiguous_data
        n_ambig_train = int(self.train_n * self.perc_ambig)
        n_nonambig_train = self.train_n - n_ambig_train
        n_ambig_dev = int(self.dev_num * self.perc_ambig)
        n_nonambig_dev = self.dev_num - n_ambig_dev
        n_ambig_test = int(self.test_num * self.perc_ambig)
        n_nonambig_test = self.test_num - n_ambig_test

        ambig_indices = [i for i in range(len(ambiguous_data))]
        ambig_index_sample = np.random.choice(ambig_indices, n_ambig_train + n_ambig_dev + n_ambig_test, replace=False)
        ambig_data = [ambiguous_data[i] for i in ambig_index_sample]
        np.random.shuffle(ambig_data)
        ambig_train = ambig_data[:n_ambig_train]
        ambig_dev = ambig_data[n_ambig_train:n_ambig_train+n_ambig_dev]
        ambig_test = ambig_data[n_ambig_train+n_ambig_dev:]

        nonambig_indices = [i for i in range(len(unambiguous_data))]
        nonambig_index_sample = np.random.choice(nonambig_indices, n_nonambig_train + n_nonambig_dev + n_nonambig_test, replace=False)
        nonambig_data = [unambiguous_data[i] for i in nonambig_index_sample]
        np.random.shuffle(nonambig_data)
        nonambig_train = nonambig_data[:n_nonambig_train]
        nonambig_dev = nonambig_data[n_nonambig_train:n_nonambig_train+n_nonambig_dev]
        nonambig_test = nonambig_data[n_nonambig_train+n_nonambig_dev:]

        train = ambig_train + nonambig_train
        dev = ambig_dev + nonambig_dev
        test = ambig_test + nonambig_test
        if self.shuffle:
            np.random.shuffle(train)
            np.random.shuffle(dev)
            np.random.shuffle(test)
        return train, dev, test

class PairedSampler(RandomSampler):
    def __init__(self, 
                 train_n, 
                 split_ratios, 
                 perc_ambig):
        super().__init__(train_n, split_ratios, perc_ambig)

    def get_interpretations_by_ratio(self, pairs, total_n, ratio):
        equiv_interpretations = defaultdict(list)
        # index by surface form 
        for ex in pairs:
            equiv_interpretations[ex['surface']].append(ex)

        all_ex_by_template = []
        # index by template
        for surface, exs in equiv_interpretations.items():
            exs_by_template = defaultdict(list)
            for ex in exs:
                exs_by_template[ex['template_idx']].append(ex)
            all_ex_by_template.append(exs_by_template)

        # sample from each template 
        all_ex_by_template_indices = [i for i in range(len(all_ex_by_template))]
        sample_ex_by_template_indices = np.random.choice(all_ex_by_template_indices, total_n, replace=False)
        sampled_ex_by_template = [all_ex_by_template[i] for i in sample_ex_by_template_indices]
        n_template_0 = int(total_n * ratio)
        n_template_1 = total_n - n_template_0

        if len(sampled_ex_by_template) == 0:
            return None

        cand_indicies = [i for i in range(len(sampled_ex_by_template))]
        samples_for_template_0_indices = np.random.choice(cand_indicies, n_template_0, replace=False)
        samples_for_template_1_indices = np.random.choice(cand_indicies, n_template_1, replace=False)

        final_samples = []
        for temp_0_idx in samples_for_template_0_indices:
            ex = sampled_ex_by_template[temp_0_idx][0]
            final_samples.append(ex[0])
        for temp_1_idx in samples_for_template_1_indices:
            ex = sampled_ex_by_template[temp_1_idx][0]
            final_samples.append(ex[0])
        assert(len(final_samples) == n_template_0 + n_template_1)
        return final_samples

    def sample(self, 
              pairs_per_type: Dict[str, List[Dict]],
              numbers_per_type: Dict[str, int],
              ratios_per_type: Dict[str, float]):
        all_samples = []
        # make sure that for each ambiguous example, the pair is in the same split 
        for type_key, pairs in pairs_per_type.items():
            n = numbers_per_type[type_key]
            if type_key == "unambiguous":
                # just sample normally, since there's only 1 interpretation per example
                indices = [i for i in range(len(pairs))]
                sample_indices = np.random.choice(indices, n, replace=False)
                sampled_pairs = [pairs[i] for i in sample_indices]
            else:
                ratio = ratios_per_type[type_key]
                sampled_pairs = self.get_interpretations_by_ratio(pairs, n, ratio)

            if sampled_pairs is None:
                continue

            all_samples += sampled_pairs
        return all_samples

def split_keep_paired(all_pairs):
    exs_by_surface = defaultdict(list)
    for ex in all_pairs:
        exs_by_surface[ex["surface"]].append(ex)
    exs_by_surface = list(exs_by_surface.values())
    train, dev, test = [], [], []
    train_idxs, dev_idxs, test_idxs = [], [], []
    idxs = [i for i in range(len(exs_by_surface))]
    n_lfs = len(exs_by_surface[0])
    n_to_sample = int((len(idxs) * 0.7) / n_lfs)
    train_idxs = np.random.choice(idxs, n_to_sample, replace=False)
    idxs = [i for i in idxs if i not in train_idxs]
    n_to_sample = int((len(idxs) * 0.1) / n_lfs)
    dev_idxs = np.random.choice(idxs, n_to_sample, replace=False)
    idxs = [i for i in idxs if i not in dev_idxs]
    test_idxs = idxs
    for idx in train_idxs:
        train += exs_by_surface[idx]
    for idx in dev_idxs:
        dev += exs_by_surface[idx]
    for idx in test_idxs:
        test += exs_by_surface[idx]
    return train, dev, test

def main(args):
    all_pp_pairs = generate_pp_pairs()
    all_conj_pairs = generate_conjunction_pairs()
    all_scope_pairs = generate_scope_pairs()
    all_unambiguous = generate_unambiguous()

    ambiguous_data = all_pp_pairs + all_conj_pairs + all_scope_pairs

    if args.sampler == "random":
        sampler = RandomSampler(args.train_n, args.split_ratios, args.perc_ambig)    
        train, dev, test = sampler.sample(ambiguous_data, all_unambiguous)

    elif args.sampler == "paired":
        # first split into train/dev/test possibilities for each type 
        # need to make sure that ambiguous pairs are in the same split 
        pp_train, pp_dev, pp_test = split_keep_paired(all_pp_pairs) 
        conj_train, conj_dev, conj_test = split_keep_paired(all_conj_pairs)
        scope_train, scope_dev, scope_test = split_keep_paired(all_scope_pairs)
        unambiguous_train, unambiguous_dev, unambiguous_test = split_keep_paired(all_unambiguous)

        # then organize data 
        train_dict = {"pp": pp_train, "conj": conj_train, "scope": scope_train, "unambiguous": unambiguous_train}
        dev_dict = {"pp": pp_dev, "conj": conj_dev, "scope": scope_dev, "unambiguous": unambiguous_dev}
        test_dict = {"pp": pp_test, "conj": conj_test, "scope": scope_test, "unambiguous": unambiguous_test}
        # organize args 
        train_nums_per_type = {"pp": args.train_num_pp, "conj": args.train_num_conj, "scope": args.train_num_scope, "unambiguous": args.train_num_unambiguous}
        dev_nums_per_type = {"pp": args.dev_num_pp, "conj": args.dev_num_conj, "scope": args.dev_num_scope, "unambiguous": args.dev_num_unambiguous}
        test_nums_per_type = {"pp": args.test_num_pp, "conj": args.test_num_conj, "scope": args.test_num_scope, "unambiguous": args.test_num_unambiguous}
        train_ratios_per_type = {"pp": args.train_pp_ratio, "conj": args.train_conj_ratio, "scope": args.train_scope_ratio, "unambiguous": 1.0}
        dev_ratios_per_type = {"pp": args.dev_pp_ratio, "conj": args.dev_conj_ratio, "scope": args.dev_scope_ratio, "unambiguous": 1.0}
        test_ratios_per_type = {"pp": args.test_pp_ratio, "conj": args.test_conj_ratio, "scope": args.test_scope_ratio, "unambiguous": 1.0}

        sampler = PairedSampler(args.train_n, args.split_ratios, args.perc_ambig)

        train = sampler.sample(train_dict, train_nums_per_type, train_ratios_per_type)
        dev = sampler.sample(dev_dict, dev_nums_per_type, dev_ratios_per_type)
        test = sampler.sample(test_dict, test_nums_per_type, test_ratios_per_type)


    else:
        raise NotImplementedError(f"Sampler: {args.sampler} is not implemented")


    if not args.out_dir.exists():
        args.out_dir.mkdir(parents=True)

    with open(args.out_dir.joinpath("train.jsonl"), "w") as f1:
        for line in train:
            f1.write(json.dumps(line) + "\n")

    with open(args.out_dir.joinpath("dev.jsonl"), "w") as f1:
        for line in dev:
            f1.write(json.dumps(line) + "\n")

    with open(args.out_dir.joinpath("test.jsonl"), "w") as f1:
        for line in test:
            f1.write(json.dumps(line) + "\n")


if __name__ == "__main__":
    parser = ArgumentParser()
    # configure as config
    parser.add_argument("--config", action = ActionConfigFile)
    # add random args 
    parser.add_argument("--sampler", type=str, required=True, help="which sampler to use", choices=["random", "paired"])
    parser.add_argument("--out_dir", type=pathlib.Path, required=True, help="directory to write splits to")
    parser.add_argument("--train_n", type=int, default=10000, help="number of sentences to include in the train set")
    parser.add_argument("--split_ratios", type=str, default="0.7:0.1:0.2", help="train:dev:test split ratios")
    parser.add_argument("--perc_ambig", type=float, default=0.5, help="percentage of ambiguous sentences to include in the train set")
    # add paired sampler args 
    parser.add_argument("--train_num_pp", type=int, default=1000, help="number of pp pairs to include in the train set")
    parser.add_argument("--train_num_conj", type=int, default=1000, help="number of conj pairs to include in the train set")
    parser.add_argument("--train_num_scope", type=int, default=1000, help="number of scope pairs to include in the train set")
    parser.add_argument("--train_num_unambiguous", type=int, default=1000, help="number of unambiguous sentences to include in the train set")
    parser.add_argument("--dev_num_pp", type=int, default=1000, help="number of pp pairs to include in the dev set")
    parser.add_argument("--dev_num_conj", type=int, default=1000, help="number of conj pairs to include in the dev set")
    parser.add_argument("--dev_num_scope", type=int, default=1000, help="number of scope pairs to include in the dev set")
    parser.add_argument("--dev_num_unambiguous", type=int, default=1000, help="number of unambiguous sentences to include in the dev set")
    parser.add_argument("--test_num_pp", type=int, default=1000, help="number of pp pairs to include in the test set")
    parser.add_argument("--test_num_conj", type=int, default=1000, help="number of conj pairs to include in the test set")
    parser.add_argument("--test_num_scope", type=int, default=1000, help="number of scope pairs to include in the test set")
    parser.add_argument("--test_num_unambiguous", type=int, default=1000, help="number of unambiguous sentences to include in the test set")
    parser.add_argument("--train_pp_ratio", type=float, default=0.5, help="ratio of meanings for pp pairs to include in the train set")
    parser.add_argument("--train_conj_ratio", type=float, default=0.5, help="ratio of meanings for conj pairs to include in the train set")
    parser.add_argument("--train_scope_ratio", type=float, default=0.5, help="ratio of meanings for scope pairs to include in the train set")
    parser.add_argument("--dev_pp_ratio", type=float, default=0.5, help="ratio of meanings for pp pairs to include in the dev set")
    parser.add_argument("--dev_conj_ratio", type=float, default=0.5, help="ratio of meanings conj pairs to include in the dev set")
    parser.add_argument("--dev_scope_ratio", type=float, default=0.5, help="ratio of meanings scope pairs to include in the dev set")
    parser.add_argument("--test_pp_ratio", type=float, default=0.5, help="ratio of meanings pp pairs to include in the test set")
    parser.add_argument("--test_conj_ratio", type=float, default=0.5, help="ratio of meanings conj pairs to include in the test set")
    parser.add_argument("--test_scope_ratio", type=float, default=0.5, help="ratio of meanings scope pairs to include in the test set")

    args = parser.parse_args()

    main(args)