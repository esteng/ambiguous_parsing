#!/bin/bash

for t in conj; do
#for t in conj bound scope revscope pp; do
    python ambiguous_parsing/generation/create_fewshot_splits.py --config-path $(pwd)/ambiguous_parsing/generation/data_configs/fewshot/generalization/ --config-name ${t}_fol.yaml out_dir=/brtx/602-nvme1/estengel/ambiguous_parsing/data/raw/generalization/${t}_fol
done 
