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

prefix=../../data/genomes/msg/ecoevolity-output/no-data-run-8

ecoevolity --seed 828409691 --prefix ../../data/genomes/msg/ecoevolity-output/no-data-run-8 --ignore-data --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../data/genomes/msg/ecoevolity-configs/gekko-rate2000.yml 1>../../data/genomes/msg/ecoevolity-output/no-data-run-8-gekko-rate2000.out 2>&1
