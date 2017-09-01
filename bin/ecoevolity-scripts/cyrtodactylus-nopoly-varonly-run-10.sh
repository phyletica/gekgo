#! /bin/sh
#PBS -l nodes=1:ppn=1
#PBS -l walltime=10:00:00
#PBS -j oe
#PBS -l jobflags=ADVRES:jro0014_lab.56281

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../../data/genomes/msg/ecoevolity-output/run-10

ecoevolity --seed 615294402 --prefix ../../data/genomes/msg/ecoevolity-output/run-10 --relax-missing-sites --relax-constant-sites ../../data/genomes/msg/ecoevolity-configs/cyrtodactylus-nopoly-varonly.yml 1>../../data/genomes/msg/ecoevolity-output/run-10-cyrtodactylus-nopoly-varonly.out 2>&1
