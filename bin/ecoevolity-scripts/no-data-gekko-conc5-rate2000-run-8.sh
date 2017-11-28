#! /bin/sh
#PBS -q gen28
#PBS -l nodes=1:ppn=1
#PBS -l walltime=0:10:00
#PBS -j oe
#PBS -W group_list=jro0014_lab
#PBS -W x=FLAGS:ADVRES:jro0014_s28.162459

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../../data/genomes/msg/ecoevolity-output/no-data-run-8-

ecoevolity --seed 762589180 --prefix ../../data/genomes/msg/ecoevolity-output/no-data-run-8- --ignore-data --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../data/genomes/msg/ecoevolity-configs/gekko-conc5-rate2000.yml 1>../../data/genomes/msg/ecoevolity-output/no-data-run-8-gekko-conc5-rate2000.out 2>&1
