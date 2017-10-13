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

prefix=../../data/genomes/msg/ecoevolity-output/run-3

ecoevolity --seed 631188014 --prefix ../../data/genomes/msg/ecoevolity-output/run-3 --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../data/genomes/msg/ecoevolity-configs/cyrtodactylus-nopoly-rate200.yml 1>../../data/genomes/msg/ecoevolity-output/run-3-cyrtodactylus-nopoly-rate200.out 2>&1
