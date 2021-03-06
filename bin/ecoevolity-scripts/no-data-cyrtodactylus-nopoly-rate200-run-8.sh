#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../../data/genomes/msg/ecoevolity-output/no-data-run-8-

ecoevolity --seed 877248348 --prefix "$prefix" --ignore-data --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../data/genomes/msg/ecoevolity-configs/cyrtodactylus-nopoly-rate200.yml 1>../../data/genomes/msg/ecoevolity-output/no-data-run-8-cyrtodactylus-nopoly-rate200.out 2>&1
