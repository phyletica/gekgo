#! /bin/bash

scriptname="$(basename "$0")"
stderrout="${scriptname}.stderr.out"

source ./project_paths.sh

if [ ! -d "$MSG_ALIGNMENTS_DIR" ]
then
    mkdir -p "$MSG_ALIGNMENTS_DIR"
fi

i=0
for loci_path in ${MSG_IPYRAD_DIR}/[CG]-*_outfiles/*.loci.gz
do
    loci_file_name="$(basename "$loci_path")"
    prefix="${loci_file_name%.*}"
    prefix="${prefix%.*}"
    nex_path="${MSG_ALIGNMENTS_DIR}/${prefix}.nex"
    biallelic_nex_path="${MSG_ALIGNMENTS_DIR}/${prefix}-polyallelic-sites-removed.nex"

    loci2nex --suffix "$i" "$loci_path" 1>"$nex_path" 2>>"$stderrout"
    loci2nex --suffix "$i" --remove-triallelic-sites "$loci_path" 1>"$biallelic_nex_path" 2>>"$stderrout"
    i=$(expr $i + 1)
done

for loci_path in ${MSG_IPYRAD_DIR}/Cyrtodactylus_outfiles/Cyrtodactylus.loci.gz ${MSG_IPYRAD_DIR}/Gekko_outfiles/Gekko.loci.gz
do
    loci_file_name="$(basename "$loci_path")"
    prefix="${loci_file_name%.*}"
    prefix="${prefix%.*}"
    nex_path="${MSG_ALIGNMENTS_DIR}/${prefix}.phy"

    loci2phy "$loci_path" 1>"$nex_path" 2>>"$stderrout"
done
