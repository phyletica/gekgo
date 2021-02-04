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

cyrt_loci_paths=( \
    Cyrtodactylus-reduced3_n80.loci.gz \
)
cyrt_label_csv_path="cyrtodactylus-id-changes.csv"

for loci_path in ${cyrt_loci_paths[@]}
do
    loci_file_name="$(basename "$loci_path")"
    prefix="${loci_file_name%.*}"
    prefix="${prefix%.*}"
    nex_path="${alignment_dir}/${prefix}.nex"
    biallelic_nex_path="${alignment_dir}/${prefix}-polyallelic-sites-removed.nex"

    loci2nex --charsets \
        -m "$cyrt_label_csv_path" \
        "$loci_path" 1>"$nex_path" 2>>"$stderrout"
    loci2nex --charsets \
        --remove-triallelic-sites \
        -m "$cyrt_label_csv_path" \
        "$loci_path" 1>"$biallelic_nex_path" 2>>"$stderrout"
done
