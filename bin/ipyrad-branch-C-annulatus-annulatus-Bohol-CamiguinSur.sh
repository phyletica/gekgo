#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-plates123.txt" -b "C-annulatus-annulatus-Bohol-CamiguinSur" "samples-Cyrtodactylus-annulatus-annulatus-Bohol-CamiguinSur.txt" 1>"ipyrad-branch-C-annulatus-annulatus-Bohol-CamiguinSur.sh.out" 2>&1
