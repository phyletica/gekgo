#!/bin/bash

. ./project_paths.sh

seq_dir="$MSG_PLATE1_DIR/demultiplexed-raw/fastq"
out_dir="$MSG_PLATE1_DIR/demultiplexed-trimmed"

if [ ! -d "$out_dir" ]
then
    mkdir "$out_dir"
fi

for gz_file in "$seq_dir"/*.fq.gz
do
    fq_file=${gz_file/\.gz/}
    gzip -d "$gz_file"
    DynamicTrim.pl "$fq_file" -p 0.05 -d "$out_dir"
    gzip "$fq_file"
done

