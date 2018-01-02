#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-G-mindorensis-mindorensis-Negros-Panay.txt" -s 67 -c 10 1>"ipyrad-steps67-G-mindorensis-mindorensis-Negros-Panay.sh.out" 2>&1
