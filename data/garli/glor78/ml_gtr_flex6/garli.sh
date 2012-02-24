#! /bin/sh
#$ -S /bin/bash
#$ -cwd
#$ -V
#$ -l h_vmem=2G
#$ -l vf=2G
#$ -q general.q

source ~/.bash_profile
cd /share/work1
cd $SGE_O_WORKDIR
Garli garli.conf
