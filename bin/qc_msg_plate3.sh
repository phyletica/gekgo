#!/bin/bash

. ./project_paths.sh

seq_dir=$MSG_PLATE3_DIR/raw
out_dir=$seq_dir/qc-output

if [ ! -d "$out_dir" ]
then
    mkdir "$out_dir"
fi

for gz_file in "$seq_dir"/*.fastq.gz
do
    fq_file=${gz_file/\.gz/}
    gzip -d "$gz_file"
    IlluQC.pl -se "$fq_file" N A -p 2 -onlyStat -t 2 -o "$out_dir"
    gzip "$fq_file"
done

