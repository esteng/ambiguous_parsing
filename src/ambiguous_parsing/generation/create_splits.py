import argparse
import json 
import pdb 
import pathlib 

import numpy as np 
np.random.seed(12)

from ambiguous_parsing.generation.generate_pairs import generate_pp_pairs, generate_conjunction_pairs, generate_scope_pairs, generate_unambiguous

def process_split_ratio(split_ratio):
    split_ratio = split_ratio.split(":")
    split_ratio = [float(x) for x in split_ratio]
    return split_ratio

class RandomSampler:
    def __init__(self, train_n, split_ratios, perc_ambig):
        self.train_n = train_n
        self.split_ratios = process_split_ratio(split_ratios)
        self.dev_num = int(self.train_n/self.split_ratios[0] * self.split_ratios[1])
        self.test_num = int(self.train_n/self.split_ratios[0] * self.split_ratios[2])

        self.perc_ambig = perc_ambig

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
        np.random.shuffle(train)
        np.random.shuffle(dev)
        np.random.shuffle(test)
        return train, dev, test

class PairedSampler(RandomSampler):
    def __init__(self, train_n, split_ratios):
        super().__init__(train_n, split_ratios)

    def sample(self, data): 
        # make sure that for each ambiguous example, the pair is in the same split 
        pass 

def main(args):
    all_pp_pairs = generate_pp_pairs()
    all_conj_pairs = generate_conjunction_pairs()
    all_scope_pairs = generate_scope_pairs()
    all_unambiguous = generate_unambiguous()

    ambiguous_data = all_pp_pairs + all_conj_pairs + all_scope_pairs

    if args.sampler == "random":
        sampler = RandomSampler(args.train_n, args.split_ratios, args.perc_ambig)    
    else:
        raise NotImplementedError(f"Sampler: {args.sampler} is not implemented")

    train, dev, test = sampler.sample(ambiguous_data, all_unambiguous)

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=pathlib.Path, required=True, help="directory to write splits to")
    parser.add_argument("--sampler", type=str, required=True, help="which sampler to use", choices=["random"])
    parser.add_argument("--train_n", type=int, required=True, default=10000)
    parser.add_argument("--split_ratios", type=str, default="0.7:0.1:0.2", help="train:dev:test split ratios")
    parser.add_argument("--perc_ambig", type=float, required=True, help="percentage of ambiguous sentences to include in the train set")
    args = parser.parse_args()

    main(args)