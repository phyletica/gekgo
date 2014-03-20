#!/bin/sh
k=20

jellyfish count -m $k -s 1G -t 8 -c 4 -o mer_counts_k${k} --quality-start=33 --min-quality=13 --both-strands *.fastq
jellyfish merge -o mer_counts_k${k}.jf mer_counts_k${k}*
jellyfish stats -v -o jfish_stats_k${k}.txt mer_counts_k${k}.jf
jellyfish histo -o jfish_histo_k${k}.txt mer_counts_k${k}.jf 
jfish_plot.r --fit-min=3 --fit-max=60 --plot-max=40 jfish_histo_k20.txt

