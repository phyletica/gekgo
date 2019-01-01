#!/bin/bash
#PBS -l nodes=1:ppn=1
#PBS -l walltime=1:00:00
#PBS -j oe 

if [ -n "$PBS_JOBNAME" ]
then
    source ${PBS_O_HOME}/.bash_profile
    cd $PBS_O_WORKDIR
fi

current_dir="$(pwd)"

project_dir="$(python gekgo_util.py)"
ecoevolity_output_dir="${project_dir}/data/genomes/msg/ecoevolity-output"
cd "$ecoevolity_output_dir"


# split comparison analyses
pyco-sumchains run-?-cyrtodactylus-rate200-split-comparison-state-run-1.log.gz 1>pyco-sumchains-cyrtodactylus-rate200-split-comparison-table.txt 2>pyco-sumchains-cyrtodactylus-rate200-split-comparison-stderr.txt
pyco-sumchains run-?-cyrtodactylus-conc5-rate200-split-comparison-state-run-1.log.gz 1>pyco-sumchains-cyrtodactylus-conc5-rate200-split-comparison-table.txt 2>pyco-sumchains-cyrtodactylus-conc5-rate200-split-comparison-stderr.txt
pyco-sumchains no-data-run-?-cyrtodactylus-rate200-split-comparison-state-run-1.log.gz 1>no-data-pyco-sumchains-cyrtodactylus-rate200-split-comparison-table.txt 2>no-data-pyco-sumchains-cyrtodactylus-rate200-split-comparison-stderr.txt
pyco-sumchains no-data-run-?-cyrtodactylus-conc5-rate200-split-comparison-state-run-1.log.gz 1>no-data-pyco-sumchains-cyrtodactylus-conc5-rate200-split-comparison-table.txt 2>no-data-pyco-sumchains-cyrtodactylus-conc5-rate200-split-comparison-stderr.txt


# for rate in "020" "200"
# do
#     for suffix in "-" "-nopoly-"
#     do
#         echo "pyco-sumchains run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log"
#         pyco-sumchains run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log 1>pyco-sumchains-cyrtodactylus${suffix}rate${rate}-table.txt 2>pyco-sumchains-cyrtodactylus${suffix}rate${rate}-stderr.txt
#     done
# done

# for rate in "020" "200" "2000"
# do
#     for suffix in "-" "-nopoly-"
#     do
#         echo "pyco-sumchains run-?-gekko${suffix}rate${rate}-state-run-1.log"
#         pyco-sumchains run-?-gekko${suffix}rate${rate}-state-run-1.log 1>pyco-sumchains-gekko${suffix}rate${rate}-table.txt 2>pyco-sumchains-gekko${suffix}rate${rate}-stderr.txt
#     done
# done


# # no data analyses
# for rate in "020" "200"
# do
#     for suffix in "-" "-nopoly-"
#     do
#         echo "pyco-sumchains no-data-run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log"
#         pyco-sumchains no-data-run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log 1>no-data-pyco-sumchains-cyrtodactylus${suffix}rate${rate}-table.txt 2>no-data-pyco-sumchains-cyrtodactylus${suffix}rate${rate}-stderr.txt
#     done
# done

# for rate in "020" "200" "2000"
# do
#     for suffix in "-" "-nopoly-"
#     do
#         echo "pyco-sumchains no-data-run-?-gekko${suffix}rate${rate}-state-run-1.log"
#         pyco-sumchains no-data-run-?-gekko${suffix}rate${rate}-state-run-1.log 1>no-data-pyco-sumchains-gekko${suffix}rate${rate}-table.txt 2>no-data-pyco-sumchains-gekko${suffix}rate${rate}-stderr.txt
#     done
# done

cd "$current_dir"
