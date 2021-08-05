#!/bin/bash
#SBATCH --time=1:00:00   # walltime
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=100G   # memory per CPU
#SBATCH --mail-user=perryleewoodjr@gmail.com   # email address
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
# load the R module; change the version if needed

##module load compiler_gnu/4.9.2
##Module load gdb/7.9.1
##module load mpi/openmpi-1.8.4_gnu-4.9.2
##module load r/3/3
##module load python/3/2

module load mpi
#module load python/3.6

#PARAMS=$1
#STEP=$2
ipyrad -p params-Cyrtodactylus-reduced-n_80.txt -b params-Cyrtodactylus-reduced2 Cyrt-samples-reduced2.txt 1>ipyrad-branch-Cyrtodactylus-reduced2.sh.out 2>&1


## run R
cd $SLURM_SUBMIT_DIR

##Rscrip $INPUT

exit 0
