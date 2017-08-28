#! /bin/sh
#PBS -l nodes=1:ppn=1
#PBS -l walltime=1:00:00
#PBS -j oe


if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -p "params-plates123.txt" -b "G-mindorensis-mindorensis-Negros-Panay" "samples-Gekko-mindorensis-mindorensis-Negros-Panay.txt" 1>"ipyrad-branch-G-mindorensis-mindorensis-Negros-Panay.sh.out" 2>&1
