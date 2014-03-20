#!/bin/bash

. ./project_paths.sh

seq_dir=$GEKKO_GENOME_DIR/raw
out_dir=$seq_dir/qc-output

if [ ! -d "$out_dir" ]
then
    mkdir "$out_dir"
fi

for gz_file in "$seq_dir"/*_R1_*.fastq.gz
do
    gz_file_rev=${gz_file/R1/R2}
    fq_file=${gz_file/\.gz/}
    fq_file_rev=${gz_file_rev/\.gz/}
    gzip -d "$gz_file"
    gzip -d "$gz_file_rev"
    IlluQC_PRLL.pl -pe "$fq_file" "$fq_file_rev" 2 A -c 2 -onlyStat -t 2 -o "$out_dir"
    gzip "$fq_file"
    gzip "$fq_file_rev"
done

