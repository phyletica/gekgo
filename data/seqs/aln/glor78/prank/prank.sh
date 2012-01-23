#!/bin/bash
wd=`pwd`
cd `dirname $0`
prank_dir=`pwd`
locus_dir=`dirname $prank_dir`
locus_name=`basename $locus_dir`
datafile=`ls ${locus_dir}/${locus_name}.fasta`
treefile=`ls ${locus_dir}/raxml/RAxML_bestTree*`
outfile=${locus_dir}/prank/${locus_name}.prank.fasta

prank -d=${datafile} -t=${treefile} -o=${outfile}

cd $wd
