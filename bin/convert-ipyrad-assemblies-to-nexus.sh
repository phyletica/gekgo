#! /bin/bash

scriptname="$(basename "$0")"
stderrout="${scriptname}.stderr.out"

source ./project_paths.sh

if [ ! -d "$MSG_ALIGNMENTS_DIR" ]
then
    mkdir -p "$MSG_ALIGNMENTS_DIR"
fi

for loci_path in ${MSG_IPYRAD_DIR}/*_outfiles/*.loci
do
    loci_file_name="$(basename "$loci_path")"
    prefix="${loci_file_name%.*}"
    nex_path="${MSG_ALIGNMENTS_DIR}/${prefix}.nex"
    biallelic_nex_path="${MSG_ALIGNMENTS_DIR}/${prefix}-polyallelic-sites-removed.nex"

    loci2nex "$loci_path" 1>"$nex_path" 2>>"$stderrout"
done
