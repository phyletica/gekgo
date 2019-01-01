#!/bin/bash

burnin=101

current_dir="$(pwd)"

project_dir="$(python gekgo_util.py)"
ecoevolity_output_dir="${project_dir}/data/genomes/msg/ecoevolity-output"

cd "$ecoevolity_output_dir"

plot_dir="../ecoevolity-results"
mkdir -p "$plot_dir"


gzip -k -d run-?-cyrtodactylus-rate200-split-comparison-state-run-1.log.gz
gzip -k -d run-?-cyrtodactylus-conc5-rate200-split-comparison-state-run-1.log.gz
sumcoevolity -f -b $burnin -n 1000000 --comparisons "Sibuyanset1 Sibuyanset2" -p "${plot_dir}/sumcoevolity-cyrtodactylus-rate200-split-comparison-" -c "../ecoevolity-configs/cyrtodactylus-rate200-split-comparison.yml" run-?-cyrtodactylus-rate200-split-comparison-state-run-1.log 1>"${plot_dir}/sumcoevolity-cyrtodactylus-rate200-split-comparison-stderr.txt" 2>&1
pyco-sumtimes -f -z -x "" -y "" -b $burnin -p "${plot_dir}/pyco-sumtimes-cyrtodactylus-rate200-split-comparison-" run-?-cyrtodactylus-rate200-split-comparison-state-run-1.log
pyco-sumevents -x "" -y "" -p "${plot_dir}/pyco-sumevents-cyrtodactylus-rate200-split-comparison-" -f --no-legend "${plot_dir}/sumcoevolity-cyrtodactylus-rate200-split-comparison-sumcoevolity-results-nevents.txt"
sumcoevolity -f -b $burnin -n 1000000 --comparisons "Sibuyanset1 Sibuyanset2" -p "${plot_dir}/sumcoevolity-cyrtodactylus-conc5-rate200-split-comparison-" -c "../ecoevolity-configs/cyrtodactylus-conc5-rate200-split-comparison.yml" run-?-cyrtodactylus-conc5-rate200-split-comparison-state-run-1.log 1>"${plot_dir}/sumcoevolity-cyrtodactylus-conc5-rate200-split-comparison-stderr.txt" 2>&1
pyco-sumtimes -f -z -x "" -y "" -b $burnin -p "${plot_dir}/pyco-sumtimes-cyrtodactylus-conc5-rate200-split-comparison-" run-?-cyrtodactylus-conc5-rate200-split-comparison-state-run-1.log
pyco-sumevents -x "" -y "" -p "${plot_dir}/pyco-sumevents-cyrtodactylus-conc5-rate200-split-comparison-" -f --no-legend "${plot_dir}/sumcoevolity-cyrtodactylus-conc5-rate200-split-comparison-sumcoevolity-results-nevents.txt"
rm run-?-cyrtodactylus-rate200-split-comparison-state-run-1.log
rm run-?-cyrtodactylus-conc5-rate200-split-comparison-state-run-1.log

gzip -k -d no-data-run-?-cyrtodactylus-rate200-split-comparison-state-run-1.log.gz
gzip -k -d no-data-run-?-cyrtodactylus-conc5-rate200-split-comparison-state-run-1.log.gz
sumcoevolity -f -b $burnin -n 1000000 --comparisons "Sibuyanset1 Sibuyanset2" -p "${plot_dir}/no-data-sumcoevolity-cyrtodactylus-rate200-split-comparison-" -c "../ecoevolity-configs/cyrtodactylus-rate200-split-comparison.yml" no-data-run-?-cyrtodactylus-rate200-split-comparison-state-run-1.log 1>"${plot_dir}/no-data-sumcoevolity-cyrtodactylus-rate200-split-comparison-stderr.txt" 2>&1
sumcoevolity -f -b $burnin -n 1000000 --comparisons "Sibuyanset1 Sibuyanset2" -p "${plot_dir}/no-data-sumcoevolity-cyrtodactylus-conc5-rate200-split-comparison-" -c "../ecoevolity-configs/cyrtodactylus-conc5-rate200-split-comparison.yml" no-data-run-?-cyrtodactylus-conc5-rate200-split-comparison-state-run-1.log 1>"${plot_dir}/no-data-sumcoevolity-cyrtodactylus-conc5-rate200-split-comparison-stderr.txt" 2>&1
rm no-data-run-?-cyrtodactylus-rate200-split-comparison-state-run-1.log
rm no-data-run-?-cyrtodactylus-conc5-rate200-split-comparison-state-run-1.log

cd "$current_dir"
