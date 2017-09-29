#! /bin/sh
#PBS -l nodes=1:ppn=20
#PBS -l walltime=60:00:00
#PBS -j oe
#PBS -M jro0014@auburn.edu
#PBS -m abe

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -p params-plates123.txt -s 345 -c 20 1>ipyrad-plates123-steps345.sh.out 2>&1
