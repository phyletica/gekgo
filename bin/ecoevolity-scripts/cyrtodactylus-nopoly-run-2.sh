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

prefix=../../data/genomes/msg/ecoevolity-output/run-2

ecoevolity --seed 958477397 --prefix ../../data/genomes/msg/ecoevolity-output/run-2 --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../data/genomes/msg/ecoevolity-configs/cyrtodactylus-nopoly.yml 1>../../data/genomes/msg/ecoevolity-output/run-2-cyrtodactylus-nopoly.out 2>&1
