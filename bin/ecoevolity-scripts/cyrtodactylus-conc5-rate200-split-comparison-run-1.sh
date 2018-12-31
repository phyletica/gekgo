#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../../data/genomes/msg/ecoevolity-output/run-1-

ecoevolity --seed 824324562 --prefix "$prefix" --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../data/genomes/msg/ecoevolity-configs/cyrtodactylus-conc5-rate200-split-comparison.yml 1>../../data/genomes/msg/ecoevolity-output/run-1-cyrtodactylus-conc5-rate200-split-comparison.out 2>&1
