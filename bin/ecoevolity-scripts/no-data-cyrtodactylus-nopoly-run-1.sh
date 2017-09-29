#! /bin/sh
#PBS -l nodes=1:ppn=1
#PBS -l walltime=20:00:00
#PBS -j oe

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../../data/genomes/msg/ecoevolity-output/no-data-run-1

ecoevolity --seed 580961243 --prefix ../../data/genomes/msg/ecoevolity-output/no-data-run-1 --ignore-data --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../data/genomes/msg/ecoevolity-configs/cyrtodactylus-nopoly.yml 1>../../data/genomes/msg/ecoevolity-output/no-data-run-1-cyrtodactylus-nopoly.out 2>&1
