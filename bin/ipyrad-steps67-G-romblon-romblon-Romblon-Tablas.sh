#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-G-romblon-romblon-Romblon-Tablas.txt" -s 67 -c 10 1>"ipyrad-steps67-G-romblon-romblon-Romblon-Tablas.sh.out" 2>&1
