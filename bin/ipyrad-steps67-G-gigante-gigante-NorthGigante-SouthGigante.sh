#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-G-gigante-gigante-NorthGigante-SouthGigante.txt" -s 67 -c 10 1>"ipyrad-steps67-G-gigante-gigante-NorthGigante-SouthGigante.sh.out" 2>&1
