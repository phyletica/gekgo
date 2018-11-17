#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source ${PBS_O_HOME}/.bash_profile
    cd $PBS_O_WORKDIR
fi

./generate-ecoevolity-qsubs.py --seed 859568562 --number-of-runs 4
