#! /bin/bash

# This script requires Version 0.2.7 or later of pycoevolity to convert the
# .loci files produced by iPyrad into nexus alignments.

scriptname="$(basename "$0")"
stderrout="${scriptname}.stderr.out"

alignment_dir="nexus-alignments"

if [ ! -d "$alignment_dir" ]
then
    mkdir -p "$alignment_dir"
fi

loci_paths=( \
    Cyrtodactylus-reduced3_n80.loci.gz \
    Cyrtodactylus-reduced5_n27.loci.gz \
    Gekko-reduced2_n81.loci.gz \
    Gekko-reduced4_n26.loci.gz
)
cyrt_label_csv_path="cyrtodactylus-id-changes.csv"
gekko_label_csv_path="gekko-id-changes.csv"

for loci_path in ${loci_paths[@]}
do
    loci_file_name="$(basename "$loci_path")"
    prefix="${loci_file_name%.*}"
    prefix="${prefix%.*}"
    nex_path="${alignment_dir}/${prefix}.nex"
    biallelic_nex_path="${alignment_dir}/${prefix}-polyallelic-sites-removed.nex"

    csv_path=""
    if [[ "$loci_path" == [Cc]yrt* ]]
    then
        csv_path="$cyrt_label_csv_path"
    elif [[ "$loci_path" == [Gg]ekko* ]]
    then
        csv_path="$gekko_label_csv_path"
    else
        echo "ERROR: Unexpected loci_path \"$loci_path\""
        exit 1
    fi


    loci2nex --charsets \
        -m "$csv_path" \
        "$loci_path" 1>"$nex_path" 2>>"$stderrout"
    loci2nex --charsets \
        --remove-triallelic-sites \
        -m "$csv_path" \
        "$loci_path" 1>"$biallelic_nex_path" 2>>"$stderrout"
done
