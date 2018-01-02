#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../../data/genomes/msg/ecoevolity-output/run-1-

ecoevolity --seed 95244336 --prefix "$prefix" --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../data/genomes/msg/ecoevolity-configs/gekko-rate020.yml 1>../../data/genomes/msg/ecoevolity-output/run-1-gekko-rate020.out 2>&1
