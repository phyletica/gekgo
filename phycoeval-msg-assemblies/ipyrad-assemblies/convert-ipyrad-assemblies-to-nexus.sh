#! /bin/bash

# This script requires Version 0.2.7 or later of pycoevolity to convert the
# .loci files produced by iPyrad into nexus alignments.

scriptname="$(basename "$0")"
stderrout="${scriptname}.stderr.out"

if [ -e "$stderrout" ]
then
    rm "$stderrout"
fi

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


# Create small dataset for phycoeval tutorial
nex_path="${alignment_dir}/Cyrtodactylus-tutorial-data.nex"
loci2nex --charsets \
    --seed 123 \
    -m "$cyrt_label_csv_path" \
    --subsample 50 \
    -d CDS_2844_Cyrtodactylus_sumuroi_Samar \
    -d CDS_3932_Cyrtodactylus_philippinicus_Lubang \
    -d CDS_4485_Cyrtodactylus_annulatus_Bohol \
    -d CDS_5823_Cyrtodactylus_philippinicus_Luzon \
    -d CWL_89_Cyrtodactylus_annulatus_Cebu \
    -d RMB_11670_Cyrtodactylus_jambangan_Mindanao \
    -d RMB_12836_Cyrtodactylus_philippinicus_Luzon \
    -d RMB_13366_Cyrtodactylus_philippinicus_Luzon \
    -d RMB_13669_Cyrtodactylus_philippinicus_Luzon \
    -d RMB_13964_Cyrtodactylus_philippinicus_Luzon \
    -d RMB_14453_Cyrtodactylus_philippinicus_Luzon \
    -d RMB_15119_Cyrtodactylus_philippinicus_Luzon \
    -d RMB_5754_Cyrtodactylus_philippinicus_CamiguinNorte \
    -d RMB_5905_Cyrtodactylus_philippinicus_BabuyanClaro \
    -d RMB_6259_Cyrtodactylus_philippinicus_Polillo \
    -d RMB_7647_Cyrtodactylus_tautbatorum_Palawan \
    -d RMB_7859_Cyrtodactylus_redimiculus_Palawan \
    -d RMB_8043_Cyrtodactylus_annulatus_CamiguinSur \
    -d RMB_8444_Cyrtodactylus_mamanwa_Dinagat \
    -d RMB_8933_Cyrtodactylus_gubaot_Leyte \
    "Cyrtodactylus-reduced5_n27.loci.gz" 1>"$nex_path"
