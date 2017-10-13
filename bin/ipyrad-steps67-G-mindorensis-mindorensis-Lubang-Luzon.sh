#! /bin/sh
#PBS -l nodes=1:ppn=10
#PBS -l walltime=1:00:00
#PBS -j oe

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-G-mindorensis-mindorensis-Lubang-Luzon.txt" -s 67 -c 10 1>"ipyrad-steps67-G-mindorensis-mindorensis-Lubang-Luzon.sh.out" 2>&1