#! /bin/sh

username="$USER"
if [ "$username" == "aubjro" ]
then
    module load gcc/6.1.0
fi

if [ -n "$PBS_JOBNAME" ]
then
    source ${PBS_O_HOME}/.bash_profile
    cd $PBS_O_WORKDIR

    module load gcc/5.3.0
fi

simname="cyrtodactylus-conc5-rate200"
cfgpath="../../data/genomes/msg/ecoevolity-configs/${simname}.yml"
outputdir="../../data/genomes/msg/ecoevolity-simulations/${simname}-unlinked-snps/batch003"
rngseed=879649790
nreps=100

mkdir -p "$outputdir"

simcoevolity --seed="$rngseed" -n "$nreps" -o "$outputdir" --relax-missing-sites --relax-constant-sites --relax-triallelic-sites --charsets --max-one-variable-site-per-locus "$cfgpath"
