#! /bin/sh
#PBS -l nodes=1:ppn=20
#PBS -l walltime=1:00:00
#PBS -j oe

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -m plates123 params-plate1.txt params-plate2.txt params-plate3.txt 1>ipyrad-merge-msg-plates.sh.out 2>&1
