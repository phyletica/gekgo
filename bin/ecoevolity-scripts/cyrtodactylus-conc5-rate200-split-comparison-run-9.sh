#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../../data/genomes/msg/ecoevolity-output/run-9-

ecoevolity --seed 268762900 --prefix "$prefix" --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../data/genomes/msg/ecoevolity-configs/cyrtodactylus-conc5-rate200-split-comparison.yml 1>../../data/genomes/msg/ecoevolity-output/run-9-cyrtodactylus-conc5-rate200-split-comparison.out 2>&1
