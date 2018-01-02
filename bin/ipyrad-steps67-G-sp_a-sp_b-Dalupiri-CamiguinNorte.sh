#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-G-sp_a-sp_b-Dalupiri-CamiguinNorte.txt" -s 67 -c 10 1>"ipyrad-steps67-G-sp_a-sp_b-Dalupiri-CamiguinNorte.sh.out" 2>&1
