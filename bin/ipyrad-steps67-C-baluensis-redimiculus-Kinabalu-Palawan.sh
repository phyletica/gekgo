#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-C-baluensis-redimiculus-Kinabalu-Palawan.txt" -s 67 -c 10 1>"ipyrad-steps67-C-baluensis-redimiculus-Kinabalu-Palawan.sh.out" 2>&1
