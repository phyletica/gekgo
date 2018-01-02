#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-plates123.txt" -b "C-gubaot-sumuroi-Leyte-Samar" "samples-Cyrtodactylus-gubaot-sumuroi-Leyte-Samar.txt" 1>"ipyrad-branch-C-gubaot-sumuroi-Leyte-Samar.sh.out" 2>&1
