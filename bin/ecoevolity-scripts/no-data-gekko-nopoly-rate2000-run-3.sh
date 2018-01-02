#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../../data/genomes/msg/ecoevolity-output/no-data-run-3-

ecoevolity --seed 631188014 --prefix "$prefix" --ignore-data --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../data/genomes/msg/ecoevolity-configs/gekko-nopoly-rate2000.yml 1>../../data/genomes/msg/ecoevolity-output/no-data-run-3-gekko-nopoly-rate2000.out 2>&1
