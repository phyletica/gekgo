#PBS -N idba_monitor
#PBS -l nodes=1:ppn=1,mem=256m,walltime=350:00:00
#PBS -S /bin/sh
#PBS -q long
#PBS -M joaks1@ku.edu

source ${HOME}/.bash_profile

cd $PBS_O_WORKDIR

kmin=30
kmax=100
kinc=10
output_dir=${PBS_O_WORKDIR}/idba_output
qsub_file=${PBS_O_WORKDIR}/idba.sh
log_file=${output_dir}/log

cmd="${HOME}/Environment/bin/idba_ud -r KU328820-15_A_L003_R1-R2_all.trimmed.fasta -o ${output_dir} --num_threads 16 --mink ${kmin} --maxk ${kmax} --step ${kinc}"
echo "#PBS -N idba" > $qsub_file
echo "#PBS -l nodes=1:ppn=16,mem=256g,walltime=300:00:00" >> $qsub_file
echo "#PBS -S /bin/sh" >> $qsub_file
echo "#PBS -q bigm" >> $qsub_file
echo "#PBS -M joaks1@ku.edu" >> $qsub_file
echo "" >> $qsub_file
echo "source ${HOME}/.bash_profile" >> $qsub_file
echo "cd $PBS_O_WORKDIR" >> $qsub_file
echo "" >> $qsub_file
echo "$cmd" >> $qsub_file

qsub_so=$(qsub $qsub_file)

proc_num=${qsub_so/\.*/}
proc_id="${proc_num}.${PBS_O_SERVER}@${PBS_O_SERVER}"
qstat_file=${PBS_O_WORKDIR}/qstat.${proc_num}.txt
mem_file=${PBS_O_WORKDIR}/idba.${proc_num}.mem_usage.txt

kmer_current=$kmin
while :
do
    qstat -f $proc_id > $qstat_file 
    if [ -z "$(cat $qstat_file)" ]
    then
        rm $qstat_file
        if [ -e ${output_dir}/*-${kmax}* ]
        then
            gzip ${output_dir}/*-${kmax}*
        fi
        break
    fi
    cat $qstat_file | grep -E "used.+mem" > $mem_file 
    if [ -e $log_file ]
    then
        kline=$(grep -E "kmer [0-9]+" $log_file | tail -n 1)
        k=${kline/kmer /}
        if [ $k -eq $[ $kmer_current + $kinc ] ]
        then
            gzip ${output_dir}/*-${kmer_current}*
            kmer_current=$[ $kmer_current + $kinc ]
        fi
    fi
    sleep 300
done

