import hydra
import re
from omegaconf import DictConfig, OmegaConf
import json 
import pdb 
from pathlib import Path
from collections import defaultdict 
from typing import List, Dict, Any
import numpy as np 
np.random.seed(12)

from ambiguous_parsing.generation.create_splits import check_and_fill_config, rerender_data, RatioSampler, split_random, split_data_for_key
from ambiguous_parsing.generation import TYPE_KEYS


from ambiguous_parsing.generation.generate_pairs import (generate_pp_pairs, 
                                                        generate_unambiguous_basic,
                                                        generate_unambiguous_instr_pairs,
                                                        generate_unambiguous_possession_pairs
                                                        )



@hydra.main(config_path="", config_name="")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))
    # cfg = check_and_fill_config(cfg)

    pp_pairs = generate_pp_pairs()
    unambiguous = generate_unambiguous_basic()
    unambig_instr = generate_unambiguous_instr_pairs()
    unambig_poss = generate_unambiguous_possession_pairs() 

    if cfg.canonicalize:
        (pp_pairs, unambiguous, unambig_instr, unambig_poss) = rerender_data(cfg, (pp_pairs, unambiguous, unambig_instr, unambig_poss)) 


    amb_unamb_data_by_key = {"pp": (pp_pairs, [])}

    # need to make sure that ambiguous pairs are in the same split
    # split into potential train/dev/test supersets
    ambig_data = {"train": {}, "dev": {}, "test": {}}
    unambig_data = {"train": {}, "dev": {}, "test": {}}
    ambig_nums_per_type = {"train": {}, "dev": {}, "test": {}}
    unambig_nums_per_type = {"train": {}, "dev": {}, "test": {}}
    for k, (ambig, unambig) in amb_unamb_data_by_key.items():
        (ambig_train, ambig_dev, ambig_test, 
        unambig_train, unambig_dev, unambig_test) = split_data_for_key(ambig, unambig, k, cfg)

        # no data in train for the ambiguity we're testing, only dev and test 

        # ambig_data['train'][k] = ambig_train
        ambig_data['dev'][k] = ambig_dev
        ambig_data['test'][k] = ambig_test

        # unambig_data['train'][k] = unambig_train
        unambig_data['dev'][k] = unambig_dev
        unambig_data['test'][k] = unambig_test

        # ambig_nums_per_type['train'][k] = int(cfg.train[f"perc_{k}"] * cfg.train[f"perc_{k}_ambig"] * cfg.train.total)
        ambig_nums_per_type['dev'][k] = int(cfg.dev[f"perc_{k}"] * cfg.dev[f"perc_{k}_ambig"] * cfg.dev.total)
        ambig_nums_per_type['test'][k] = int(cfg.test[f"perc_{k}"] * cfg.test[f"perc_{k}_ambig"] * cfg.test.total)

        # unambig_nums_per_type['train'][k] = int(cfg.train[f"perc_{k}"] * cfg.train[f"perc_{k}_unambig"] * cfg.train.total)
        unambig_nums_per_type['dev'][k] = int(cfg.dev[f"perc_{k}"] * cfg.dev[f"perc_{k}_unambig"] * cfg.dev.total)
        unambig_nums_per_type['test'][k] = int(cfg.test[f"perc_{k}"] * cfg.test[f"perc_{k}_unambig"] * cfg.test.total)

    # combine everything together, no need to split since dev/test are pp only
    unambiguous_train = unambiguous + unambig_poss + unambig_instr
    # unambiguous_train, unambiguous_dev, unambiguous_test = split_random(unambiguous, 
    #                                                                 n_train = len(unambiguous)
    #                                                                 n_dev = 0
    #                                                                 n_test = 0) 

    unambig_data['train']['unambiguous'] = unambiguous_train
    # unambig_data['dev']['unambiguous'] = unambiguous_dev
    # unambig_data['test']['unambiguous'] = unambiguous_test
    
    unambig_nums_per_type['train']['unambiguous'] = int(cfg.train.perc_unambig * cfg.train.total)
    unambig_nums_per_type['dev']['unambiguous'] = int(cfg.dev.perc_unambig * cfg.dev.total)
    unambig_nums_per_type['test']['unambiguous'] = int(cfg.test.perc_unambig * cfg.test.total)

    # then organize data 
    ratio_dict = {"train": {}, "dev": {}, "test": {}}
    for split in ['train', 'dev', 'test']:
        for key in TYPE_KEYS:
            if key in ["unambig", "unambig_poss", "unambig_instr"]:
                continue
            try:
                ratio_dict[split][key] = cfg[split][f"{key}_ratio"]
            except:
                continue

    sampler = RatioSampler(cfg) 

    train = unambiguous_train 

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

    # write all the dev and test examples to separate files to use later for eval
    # these files contain both interpretations for ambiguous examples 
    with open(cfg.out_dir.joinpath("train_eval.jsonl"), "w") as f1:
        for type_key, __ in ambig_data['train'].items():
            data = ambig_data['train'][type_key] + unambig_data['train'][type_key]
            for line in data:
                f1.write(json.dumps(line) + "\n")

    with open(cfg.out_dir.joinpath("dev_eval.jsonl"), "w") as f1:
        for type_key, __ in ambig_data['dev'].items():
            data = ambig_data['dev'][type_key] + unambig_data['dev'][type_key]
            for line in data:
                f1.write(json.dumps(line) + "\n")

    with open(cfg.out_dir.joinpath("test_eval.jsonl"), "w") as f1:
        for type_key, __ in ambig_data['test'].items():
            data = ambig_data['test'][type_key] + unambig_data['test'][type_key]
            for line in data:
                f1.write(json.dumps(line) + "\n")





if __name__ == "__main__":
    main()