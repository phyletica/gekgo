#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-plates123.txt" -b "Cyrtodactylus" "samples-Cyrtodactylus.txt" 1>"ipyrad-branch-Cyrtodactylus.sh.out" 2>&1
