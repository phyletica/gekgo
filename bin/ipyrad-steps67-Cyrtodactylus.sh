#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-Cyrtodactylus.txt" -s 67 -c 10 1>"ipyrad-steps67-Cyrtodactylus.sh.out" 2>&1
