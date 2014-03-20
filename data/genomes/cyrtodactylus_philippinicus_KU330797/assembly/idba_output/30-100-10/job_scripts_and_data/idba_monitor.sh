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

proc_num=42285
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

