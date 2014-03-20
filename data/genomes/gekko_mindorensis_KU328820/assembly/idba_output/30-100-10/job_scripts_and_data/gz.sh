#PBS -N gzip
#PBS -l nodes=1:ppn=1,mem=1g,walltime=20:00:00
#PBS -S /bin/sh
#PBS -q default

source ${HOME}/.bash_profile

cd $PBS_O_WORKDIR

gzip kmer

