#!/bin/bash

. ./project_paths.sh

seq_dir="$MSG_PLATE1_DIR"/demultiplexed-raw/fastq

seqsummary.py "$seq_dir"/*.fq.gz > "$seq_dir"/seqsummary-output.txt

