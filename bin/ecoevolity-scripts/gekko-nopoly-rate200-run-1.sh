#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../../data/genomes/msg/ecoevolity-output/run-1-

ecoevolity --seed 633325300 --prefix "$prefix" --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../data/genomes/msg/ecoevolity-configs/gekko-nopoly-rate200.yml 1>../../data/genomes/msg/ecoevolity-output/run-1-gekko-nopoly-rate200.out 2>&1
