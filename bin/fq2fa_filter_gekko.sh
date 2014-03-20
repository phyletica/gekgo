#!/bin/bash

. ./project_paths.sh

seq_dir=$GEKKO_GENOME_DIR/trimmed
out_dir=$GEKKO_GENOME_DIR/fasta

if [ ! -d "$out_dir" ]
then
    mkdir "$out_dir"
fi

fname=$(basename "$seq_dir"/*R1_001.trimmed.fastq.gz)
masterfile="$out_dir"/${fname/R1*/R1-R2_all.trimmed.fasta}

if [ -e "$masterfile" ]
then
    echo "File $masterfile already exists! Good bye!"
    exit 1
fi

for gz_file in "$seq_dir"/*_R1_*.fastq;
do
    gz_file_rev=${gz_file/R1/R2}
    fq_file=${gz_file/\.gz/}
    fq_file_rev=${gz_file_rev/\.gz/}
    gzip -d "$gz_file"
    gzip -d "$gz_file_rev"
    filename=$(basename "$fq_file")
    outprefix=${filename/R1/R1-R2}
    outfile="$out_dir"/${outprefix/fastq/fasta}
    fq2fa --merge --filter "$fq_file" "$fq_file_rev" "$outfile"
    cat "$outfile" >> "$masterfile"
    rm "$outfile"
    gzip "$fq_file"
    gzip "$fq_file_rev"
done

gzip "$masterfile"

