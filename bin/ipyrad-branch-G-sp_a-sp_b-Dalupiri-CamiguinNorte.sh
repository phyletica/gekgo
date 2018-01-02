#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-plates123.txt" -b "G-sp_a-sp_b-Dalupiri-CamiguinNorte" "samples-Gekko-sp.a-sp.b-Dalupiri-CamiguinNorte.txt" 1>"ipyrad-branch-G-sp_a-sp_b-Dalupiri-CamiguinNorte.sh.out" 2>&1
