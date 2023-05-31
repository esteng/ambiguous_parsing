#!/bin/bash

for dirn in data/fewshot/*; do
    echo "d: ${dirn}"
    dirname=$(basename $dirn)
    echo $dirname
    cwd=$(pwd)
    cd $dirn
    tar -xzvf data.tar.gz
    cd $cwd
done
for dirn in data/zeroshot/*; do
    echo "d: ${dirn}"
    dirname=$(basename $dirn)
    echo $dirname
    cwd=$(pwd)
    cd $dirn
    tar -xzvf data.tar.gz
    cd $cwd
done