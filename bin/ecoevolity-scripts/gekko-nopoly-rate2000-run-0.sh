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

prefix=../../data/genomes/msg/ecoevolity-output/run-0

ecoevolity --seed 593464665 --prefix ../../data/genomes/msg/ecoevolity-output/run-0 --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../data/genomes/msg/ecoevolity-configs/gekko-nopoly-rate2000.yml 1>../../data/genomes/msg/ecoevolity-output/run-0-gekko-nopoly-rate2000.out 2>&1
