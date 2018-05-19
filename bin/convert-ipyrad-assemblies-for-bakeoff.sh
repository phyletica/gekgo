#! /bin/bash

nloci=100
rngseed=125776774

scriptname="$(basename "$0")"
stderrout="${scriptname}.stderr.out"

source ./project_paths.sh

if [ ! -d "$BAKEOFF_ALIGNMENTS_DIR" ]
then
    mkdir -p "$BAKEOFF_ALIGNMENTS_DIR"
fi

paths="${MSG_IPYRAD_DIR}/G-crombota-rossi-BabuyanClaro-Calayan_outfiles/G-crombota-rossi-BabuyanClaro-Calayan.loci.gz
${MSG_IPYRAD_DIR}/G-mindorensis-mindorensis-Lubang-Luzon_outfiles/G-mindorensis-mindorensis-Lubang-Luzon.loci.gz
${MSG_IPYRAD_DIR}/G-mindorensis-mindorensis-MaestreDeCampo-Masbate_outfiles/G-mindorensis-mindorensis-MaestreDeCampo-Masbate.loci.gz
${MSG_IPYRAD_DIR}/G-sp_a-sp_b-Dalupiri-CamiguinNorte_outfiles/G-sp_a-sp_b-Dalupiri-CamiguinNorte.loci.gz"

loci2dppmsbayes --output-dir "$BAKEOFF_ALIGNMENTS_DIR" \
        -n "$nloci" \
        --population-name-delimiter "_" \
        --seed "$rngseed" \
        $paths
