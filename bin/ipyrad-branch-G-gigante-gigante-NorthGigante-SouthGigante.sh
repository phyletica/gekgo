#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-plates123.txt" -b "G-gigante-gigante-NorthGigante-SouthGigante" "samples-Gekko-gigante-gigante-NorthGigante-SouthGigante.txt" 1>"ipyrad-branch-G-gigante-gigante-NorthGigante-SouthGigante.sh.out" 2>&1
