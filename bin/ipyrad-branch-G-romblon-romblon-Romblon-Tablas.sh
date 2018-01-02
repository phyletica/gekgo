#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-plates123.txt" -b "G-romblon-romblon-Romblon-Tablas" "samples-Gekko-romblon-romblon-Romblon-Tablas.txt" 1>"ipyrad-branch-G-romblon-romblon-Romblon-Tablas.sh.out" 2>&1
