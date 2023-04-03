import hydra
import re
from omegaconf import DictConfig, OmegaConf
import json 
import pdb 
from pathlib import Path
from collections import defaultdict 
from typing import List, Dict, Any

from ambiguous_parsing.generation import TYPE_KEYS
import numpy as np 
np.random.seed(12)

from ambiguous_parsing.generation.generate_pairs import (generate_pp_pairs, 
                                                        generate_unambiguous_pp,
                                                        generate_scope_pairs,
                                                        generate_reverse_scope_pairs,
                                                        generate_unambiguous_scope,
                                                        generate_conjunction_pairs,
                                                        generate_unambiguous_conj,
                                                        generate_bound_pronoun_pairs,
                                                        generate_unambigous_bound_pronoun,
                                                        generate_unambiguous_basic)

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

class RatioSampler:
    def __init__(self, 
                 cfg: DictConfig):
        self.cfg = cfg 

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
        samples_for_template_0_indices, samples_for_template_1_indices = [], []
        prob_zero = n_template_0 / (n_template_0 + n_template_1)
        prob_one = 1 - prob_zero
        for cidx in cand_indicies:
            coinflip = np.random.choice([0, 1], p=[prob_zero, prob_one])
            if coinflip == 0:
                samples_for_template_0_indices.append(cidx)
            else:
                samples_for_template_1_indices.append(cidx)
        # instead of this, model as a coinflip so that idxs are exclusive and one index doesn't get to choose first
        # samples_for_template_0_indices = np.random.choice(cand_indicies, n_template_0, replace=False)
        # samples_for_template_1_indices = np.random.choice(cand_indicies, n_template_1, replace=False)

        final_samples = []
        for temp_0_idx in samples_for_template_0_indices:
            ex = sampled_ex_by_template[temp_0_idx][0]
            final_samples.append(ex[0])
        for temp_1_idx in samples_for_template_1_indices:
            ex = sampled_ex_by_template[temp_1_idx][1]
            final_samples.append(ex[0])

        assert(len(final_samples) == n_template_0 + n_template_1)
        return final_samples

    def sample(self, 
              ambig_data: Dict[str, List],
              unambig_data: Dict[str, List],
              ambig_nums_per_type: Dict[str, int],
              unambig_nums_per_type: Dict[str, int],
              ratio_dict: Dict[str, float]):

        all_samples = []
        # make sure that for each ambiguous example, the pair is in the same split 
        for type_key in TYPE_KEYS: 
            if type_key == "unambig":
                # unambig data isn't paired 
                continue

            n_unambig = unambig_nums_per_type[type_key]
            # for unambiguous 
            unambig_pairs = unambig_data[type_key]
            # just sample normally, since there's only 1 interpretation per example
            unambig_indices = [i for i in range(len(unambig_pairs))]
            unambig_sampled_indices = np.random.choice(unambig_indices, n_unambig, replace=False)
            unambig_sampled_pairs = [unambig_pairs[i] for i in unambig_sampled_indices]

            all_samples += unambig_sampled_pairs
            # for ambiguous
            n_ambig = ambig_nums_per_type[type_key]
            ratio = ratio_dict[type_key]
            ambig_pairs = ambig_data[type_key]
            ambig_sampled_pairs = self.get_interpretations_by_ratio(ambig_pairs, n_ambig, ratio)
            all_samples += ambig_sampled_pairs

        return all_samples

def split_random(all_examples, n_train, n_dev, n_test):
    indices = [i for i in range(len(all_examples))]
    train_idxs = np.random.choice(indices, n_train, replace=False)
    indices = [i for i in indices if i not in train_idxs]

    dev_idxs = np.random.choice(indices, n_dev, replace=False)
    indices = [i for i in indices if i not in dev_idxs]

    test_idxs = np.random.choice(indices, n_test, replace=False)
    test_idxs = [i for i in indices if i not in test_idxs]

    train = [all_examples[i] for i in train_idxs]
    dev = [all_examples[i] for i in dev_idxs]
    test = [all_examples[i] for i in test_idxs]
    return train, dev, test

def split_keep_paired(all_pairs, n_train, n_dev, n_test):
    exs_by_surface = defaultdict(list)
    for ex in all_pairs:
        exs_by_surface[ex["surface"]].append(ex)
    exs_by_surface = list(exs_by_surface.values())
    train, dev, test = [], [], []
    train_idxs, dev_idxs, test_idxs = [], [], []
    idxs = [i for i in range(len(exs_by_surface))]

    train_idxs = np.random.choice(idxs, n_train, replace=False)
    idxs = [i for i in idxs if i not in train_idxs]

    dev_idxs = np.random.choice(idxs, n_dev, replace=False)
    idxs = [i for i in idxs if i not in dev_idxs]

    test_idxs = np.random.choice(idxs, n_test, replace=False)
    test_idxs = idxs

    for idx in train_idxs:
        train += exs_by_surface[idx]
    for idx in dev_idxs:
        dev += exs_by_surface[idx]
    for idx in test_idxs:
        test += exs_by_surface[idx]

    return train, dev, test

def split_data_for_key(ambig, unambig, key, cfg):
    # first split ambig and unambig into train/dev/test
    num_train_ambig = int(cfg.train.total * cfg.train[f"perc_{key}_ambig"] * cfg.train[f'perc_{key}'])
    num_dev_ambig = int(cfg.dev.total * cfg.dev[f"perc_{key}_ambig"] * cfg.dev[f'perc_{key}'])
    num_test_ambig = int(cfg.test.total * cfg.test[f"perc_{key}_ambig"] * cfg.test[f'perc_{key}'])
    num_train_unambig = int(cfg.train.total * (1 - cfg.train[f"perc_{key}_ambig"]) * cfg.train[f'perc_{key}'])
    num_dev_unambig = int(cfg.dev.total * (1 - cfg.dev[f"perc_{key}_ambig"]) * cfg.dev[f'perc_{key}'])
    num_test_unambig = int(cfg.test.total * (1 - cfg.test[f"perc_{key}_ambig"]) * cfg.test[f'perc_{key}'])

    try: 
        ambig_train, ambig_dev, ambig_test = split_keep_paired(ambig, 
                                                    num_train_ambig,
                                                    num_dev_ambig,
                                                    num_test_ambig)

        unambig_train, unambig_dev, unambig_test = split_keep_paired(unambig,
                                                        num_train_unambig,
                                                        num_dev_unambig,
                                                        num_test_unambig)
    except:
        pdb.set_trace()
    return ambig_train, ambig_dev, ambig_test, unambig_train, unambig_dev, unambig_test


def check_and_fill_config(cfg):
    for split in ['train', 'dev', 'test']:
        percs = [cfg[split][f"perc_{key}"] for key in TYPE_KEYS]
        if any([perc is None for perc in percs]):
            if not all([perc is None for perc in percs]):
                raise ValueError("If you specify any of the perc_*_ambig or perc_*_unambig, you must specify all of them.")
            # if none are specified, distribute evenly 
            for key in TYPE_KEYS:
                cfg[split][f"perc_{key}"] = 1/len(TYPE_KEYS)
        else:
            if not all([perc is not None for perc in percs]):
                raise ValueError("If you specify any of the perc_*_ambig or perc_*_unambig, you must specify all of them.")

            if not sum([perc for perc in percs]) == 1:
                raise ValueError("The perc_*_ambig and perc_*_unambig must sum to 1.")
    return cfg         


@hydra.main(config_path="", config_name="")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))
    cfg = check_and_fill_config(cfg)

    pp_pairs = generate_pp_pairs()
    unambig_pp = generate_unambiguous_pp()

    scope_pairs = generate_scope_pairs()
    reverse_scope_pairs = generate_reverse_scope_pairs()
    unambig_scope = generate_unambiguous_scope()

    conj_pairs = generate_conjunction_pairs()
    unambig_conj = generate_unambiguous_conj()

    bound_pairs = generate_bound_pronoun_pairs(is_female=True)+\
                generate_bound_pronoun_pairs(is_female=False)
    unambig_bound = generate_unambigous_bound_pronoun(is_female=True) + \
                    generate_unambigous_bound_pronoun(is_female=False)

    unambiguous = generate_unambiguous_basic()

    if cfg.sampler == "random":
        ambiguous_data = (pp_pairs + scope_pairs + reverse_scope_pairs + conj_pairs + bound_pairs)
        unambiguous_data = (unambig_pp + unambig_scope + unambig_conj + unambig_bound + unambiguous)
        sampler = RandomSampler(cfg.train_n, cfg.split_ratios, cfg.perc_ambig)    
        train, dev, test = sampler.sample(ambiguous_data, unambiguous_data)

    elif cfg.sampler == "paired":

        amb_unamb_data_by_key = {"pp": (pp_pairs, unambig_pp), 
                        "scope": (scope_pairs, unambig_scope),
                        "revscope": (reverse_scope_pairs, unambig_scope),
                        "conj": (conj_pairs, unambig_conj),
                        "bound": (bound_pairs, unambig_bound)}

        # need to make sure that ambiguous pairs are in the same split
        # split into potential train/dev/test supersets
        ambig_data = {"train": {}, "dev": {}, "test": {}}
        unambig_data = {"train": {}, "dev": {}, "test": {}}
        ambig_nums_per_type = {"train": {}, "dev": {}, "test": {}}
        unambig_nums_per_type = {"train": {}, "dev": {}, "test": {}}
        for k, (ambig, unambig) in amb_unamb_data_by_key.items():
            (ambig_train, ambig_dev, ambig_test, 
            unambig_train, unambig_dev, unambig_test) = split_data_for_key(ambig, unambig, k, cfg)

            ambig_data['train'][k] = ambig_train
            ambig_data['dev'][k] = ambig_dev
            ambig_data['test'][k] = ambig_test
            unambig_data['train'][k] = unambig_train
            unambig_data['dev'][k] = unambig_dev
            unambig_data['test'][k] = unambig_test

            ambig_nums_per_type['train'][k] = int(cfg.train[f"perc_{k}"] * cfg.train[f"perc_{k}_ambig"] * cfg.train.total)
            ambig_nums_per_type['dev'][k] = int(cfg.dev[f"perc_{k}"] * cfg.dev[f"perc_{k}_ambig"] * cfg.dev.total)
            ambig_nums_per_type['test'][k] = int(cfg.test[f"perc_{k}"] * cfg.test[f"perc_{k}_ambig"] * cfg.test.total)

            unambig_nums_per_type['train'][k] = int(cfg.train[f"perc_{k}"] * cfg.train[f"perc_{k}_unambig"] * cfg.train.total)
            unambig_nums_per_type['dev'][k] = int(cfg.dev[f"perc_{k}"] * cfg.dev[f"perc_{k}_unambig"] * cfg.dev.total)
            unambig_nums_per_type['test'][k] = int(cfg.test[f"perc_{k}"] * cfg.test[f"perc_{k}_unambig"] * cfg.test.total)


        unambiguous_train, unambiguous_dev, unambiguous_test = split_random(unambiguous, 
                                                                        n_train = int(cfg.train.total * cfg.train.perc_unambig),
                                                                        n_dev = int(cfg.dev.total * cfg.dev.perc_unambig),
                                                                        n_test = int(cfg.test.total * cfg.test.perc_unambig))
        unambig_data['train']['unambiguous'] = unambiguous_train
        unambig_data['dev']['unambiguous'] = unambiguous_dev
        unambig_data['test']['unambiguous'] = unambiguous_test
        
        unambig_nums_per_type['train']['unambiguous'] = int(cfg.train.perc_unambig * cfg.train.total)
        unambig_nums_per_type['dev']['unambiguous'] = int(cfg.dev.perc_unambig * cfg.dev.total)
        unambig_nums_per_type['test']['unambiguous'] = int(cfg.test.perc_unambig * cfg.test.total)

        # then organize data 
        ratio_dict = {"train": {}, "dev": {}, "test": {}}
        for split in ['train', 'dev', 'test']:
            for key in TYPE_KEYS:
                if key == "unambig": 
                    continue
                ratio_dict[split][key] = cfg[split][f"{key}_ratio"]

        sampler = RatioSampler(cfg) 

        # TODO: elias: pick up here 
        # right now the code is pretty ugly and repetitive and i think we're doing a lot of uncessary sampling 
        train = sampler.sample(ambig_data['train'], 
                                unambig_data['train'], 
                                ambig_nums_per_type['train'], 
                                unambig_nums_per_type['train'], 
                                ratio_dict['train'])

        dev = sampler.sample(ambig_data['dev'], 
                                unambig_data['dev'], 
                                ambig_nums_per_type['dev'], 
                                unambig_nums_per_type['dev'], 
                                ratio_dict['dev'])

        test = sampler.sample(ambig_data['test'], 
                                unambig_data['test'], 
                                ambig_nums_per_type['test'], 
                                unambig_nums_per_type['test'], 
                                ratio_dict['test'])
        # dev = sampler.sample(dev_dict, dev_nums_per_type, dev_ratios_per_type)
        # test = sampler.sample(test_dict, test_nums_per_type, test_ratios_per_type)


    else:
        raise NotImplementedError(f"Sampler: {cfg.sampler} is not implemented")

    cfg.out_dir = Path(cfg.out_dir)    

    if not cfg.out_dir.exists():
        cfg.out_dir.mkdir(parents=True)

    with open(cfg.out_dir.joinpath("train.jsonl"), "w") as f1:
        for line in train:
            f1.write(json.dumps(line) + "\n")

    with open(cfg.out_dir.joinpath("dev.jsonl"), "w") as f1:
        for line in dev:
            f1.write(json.dumps(line) + "\n")

    with open(cfg.out_dir.joinpath("test.jsonl"), "w") as f1:
        for line in test:
            f1.write(json.dumps(line) + "\n")






if __name__ == "__main__":
    main()