#! /bin/sh
#PBS -l nodes=1:ppn=10
#PBS -l walltime=50:00:00
#PBS -j oe
#PBS -l jobflags=ADVRES:jro0014_lab.56281

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -p "params-G-mindorensis-mindorensis-MaestreDeCampo-Masbate.txt" -s 67 -c 10 1>"ipyrad-steps67-G-mindorensis-mindorensis-MaestreDeCampo-Masbate.sh.out" 2>&1
