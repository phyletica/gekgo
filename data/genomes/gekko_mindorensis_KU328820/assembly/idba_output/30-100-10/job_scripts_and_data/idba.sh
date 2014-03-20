#PBS -N idba
#PBS -l nodes=1:ppn=16,mem=256g,walltime=300:00:00
#PBS -S /bin/sh
#PBS -q bigm
#PBS -M joaks1@ku.edu

source /users/joaks1/.bash_profile
cd /nfs/work/joaks1/genome_assemblies/gekko_mindorensis

/users/joaks1/Environment/bin/idba_ud -r KU328820-15_A_L003_R1-R2_all.trimmed.fasta -o /nfs/work/joaks1/genome_assemblies/gekko_mindorensis/idba_output --num_threads 16 --mink 30 --maxk 100 --step 10
