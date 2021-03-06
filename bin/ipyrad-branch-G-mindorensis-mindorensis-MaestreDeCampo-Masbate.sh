#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    condaenv on
    condaenv
fi

ipyrad -f -p "params-plates123.txt" -b "G-mindorensis-mindorensis-MaestreDeCampo-Masbate" "samples-Gekko-mindorensis-mindorensis-MaestreDeCampo-Masbate.txt" 1>"ipyrad-branch-G-mindorensis-mindorensis-MaestreDeCampo-Masbate.sh.out" 2>&1
