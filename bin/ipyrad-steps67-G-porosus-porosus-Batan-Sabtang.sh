#! /bin/sh
#PBS -l nodes=1:ppn=10
#PBS -l walltime=2:00:00
#PBS -j oe
#PBS -l jobflags=ADVRES:jro0014_lab.56281

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-G-porosus-porosus-Batan-Sabtang.txt" -s 67 -c 10 1>"ipyrad-steps67-G-porosus-porosus-Batan-Sabtang.sh.out" 2>&1
