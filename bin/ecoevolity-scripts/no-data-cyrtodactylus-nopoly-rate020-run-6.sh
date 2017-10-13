#! /bin/sh
#PBS -l nodes=1:ppn=1
#PBS -l walltime=0:10:00
#PBS -j oe

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../../data/genomes/msg/ecoevolity-output/no-data-run-6

ecoevolity --seed 363631181 --prefix ../../data/genomes/msg/ecoevolity-output/no-data-run-6 --ignore-data --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../data/genomes/msg/ecoevolity-configs/cyrtodactylus-nopoly-rate020.yml 1>../../data/genomes/msg/ecoevolity-output/no-data-run-6-cyrtodactylus-nopoly-rate020.out 2>&1