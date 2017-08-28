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

ipyrad -p "params-plates123.txt" -b "G-porosus-porosus-Batan-Sabtang" "samples-Gekko-porosus-porosus-Batan-Sabtang.txt" 1>"ipyrad-branch-G-porosus-porosus-Batan-Sabtang.sh.out" 2>&1
