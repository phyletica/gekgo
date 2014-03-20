#!/bin/bash

. ./project_paths.sh

seq_dir=$CYRT_GENOME_DIR/raw
out_dir=$CYRT_GENOME_DIR/trimmed

if [ ! -d "$out_dir" ]
then
    mkdir "$out_dir"
fi

for gz_file in "$seq_dir"/*.fastq.gz
do
    fq_file=${gz_file/\.gz/}
    gzip -d "$gz_file"
    DynamicTrim.pl "fq_file" -p 0.1 -d "$out_dir"
    gzip "$fq_file"
done

