#! /bin/sh
#PBS -l nodes=1:ppn=20
#PBS -l walltime=1:00:00
#PBS -j oe
#PBS -l jobflags=ADVRES:jro0014_lab.56281

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -p params-plate3.txt -s 12 -c 20 1>ipyrad-plate3-steps12.sh.out 2>&1
