#!/bin/bash
#SBATCH --time=2:00:00   # walltime
#SBATCH --nodes=1
#SBATCH --ntasks=10
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=10G   # memory per CPU
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

#PARAMS=$1
#STEP=$2

ipyrad -p params-Gekko-reduced_n88.txt -s 67 -c 10 -f 1>ipyrad-Gekko-reduced_n88-steps67.sh.out 2>&1
#java -version >java.log


## run R
cd $SLURM_SUBMIT_DIR

##Rscrip $INPUT

exit 0
