#!/bin/bash

for split in 0_100 10_90 20_80 30_70 40_60 50_50 60_40 70_30 80_20 90_10 100_0; do
    for dtype in lisp fol; do
        split_out_name=$(sed 's/_/-/g' <<< $split)
        cfg_path="$(pwd)/ambiguous_parsing/generation/data_configs/vary_ambiguity_global/${split}_split"
        cfg_name="5k_train_100_perc_ambig_${dtype}.yaml"
        out_dir="/brtx/602-nvme1/estengel/ambiguous_parsing/data/raw/${split_out_name}-5k-train-100-perc-ambig_${dtype}"
        python ambiguous_parsing/generation/create_splits.py \
            --config-path ${cfg_path} \
            --config-name ${cfg_name} \
            out_dir=${out_dir}
    done
done 
