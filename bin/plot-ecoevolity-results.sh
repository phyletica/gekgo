#!/bin/bash

set -e -x

if [ -n "$PBS_JOBNAME" ]
then
    source ${PBS_O_HOME}/.bash_profile
    cd $PBS_O_WORKDIR
fi

label_array=()
convert_labels_to_array() {
    local concat=""
    local t=""
    label_array=()

    for word in $@
    do
        local len=`expr "$word" : '.*"'`

        [ "$len" -eq 1 ] && concat="true"

        if [ "$concat" ]
        then
            t+=" $word"
        else
            word=${word#\"}
            word=${word%\"}
            label_array+=("$word")
        fi

        if [ "$concat" -a "$len" -gt 1 ]
        then
            t=${t# }
            t=${t#\"}
            t=${t%\"}
            label_array+=("$t")
            t=""
            concat=""
        fi
    done
}

burnin=101

current_dir="$(pwd)"

project_dir="$(python gekgo_util.py)"
ecoevolity_output_dir="${project_dir}/data/genomes/msg/ecoevolity-output"
cd "$ecoevolity_output_dir"

plot_dir="../ecoevolity-results"
mkdir -p "$plot_dir"

labels='-l "Bohol0" "Bohol"
-l "CamiguinSur0" "Camiguin Sur"
-l "root-Bohol0" "Bohol-Camiguin Sur Root"
-l "Palawan1" "Palawan"
-l "Kinabalu1" "Borneo"
-l "root-Palawan1" "Palawan-Borneo Root"
-l "Samar2" "Samar"
-l "Leyte2" "Leyte"
-l "root-Samar2" "Samar-Leyte Root"
-l "Luzon3" "Luzon 1"
-l "BabuyanClaro3" "Babuyan Claro"
-l "root-Luzon3" "Luzon-Babuyan Claro Root"
-l "Luzon4" "Luzon 2"
-l "CamiguinNorte4" "Camiguin Norte"
-l "root-Luzon4" "Luzon-Camiguin Norte Root"
-l "Polillo5" "Polillo"
-l "Luzon5" "Luzon 3"
-l "root-Polillo5" "Polillo-Luzon Root"
-l "Panay6" "Panay"
-l "Negros6" "Negros"
-l "root-Panay6" "Panay-Negros Root"
-l "Sibuyan7" "Sibuyan"
-l "Tablas7" "Tablas"
-l "root-Sibuyan7" "Sibuyan-Tablas Root"
-l "BabuyanClaro8" "Babuyan Claro"
-l "Calayan8" "Calayan"
-l "root-BabuyanClaro8" "Babuyan Claro-Calayan Root"
-l "SouthGigante9" "S. Gigante"
-l "NorthGigante9" "N. Gigante"
-l "root-SouthGigante9" "S. Gigante-N. Gigante Root"
-l "Lubang11" "Lubang"
-l "Luzon11" "Luzon"
-l "root-Lubang11" "Lubang-Luzon Root"
-l "MaestreDeCampo12" "Maestre De Campo"
-l "Masbate12" "Masbate"
-l "root-MaestreDeCampo12" "Maestre De Campo-Masbate Root"
-l "Panay13" "Panay 1"
-l "Masbate13" "Masbate"
-l "root-Panay13" "Panay-Masbate Root"
-l "Negros14" "Negros"
-l "Panay14" "Panay 2"
-l "root-Negros14" "Negros-Panay Root"
-l "Sabtang15" "Sabtang"
-l "Batan15" "Batan"
-l "root-Sabtang15" "Sabtang-Batan Root"
-l "Romblon16" "Romblon"
-l "Tablas16" "Tablas"
-l "root-Romblon16" "Romblon-Tablas Root"
-l "CamiguinNorte17" "Camiguin Norte"
-l "Dalupiri17" "Dalupiri"
-l "root-CamiguinNorte17" "Camiguin Norte-Dalupiri Root"'

convert_labels_to_array $labels

for rate in "020" "200"
do
    for suffix in "-" "-nopoly-"
    do
        pyco-sumtimes -f --x-limits 0.0 0.011 -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumtimes-cyrtodactylus${suffix}rate${rate}-" run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log
        pyco-sumsizes -f --x-limits 0.0 0.0025 -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumsizes-cyrtodactylus${suffix}rate${rate}-" run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log
        sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/sumcoevolity-cyrtodactylus${suffix}rate${rate}-" -c "../ecoevolity-configs/cyrtodactylus${suffix}rate${rate}.yml" run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log
        pyco-sumevents -x "" -y "" -p "${plot_dir}/pyco-sumevents-cyrtodactylus${suffix}rate${rate}-" -f --no-legend "${plot_dir}/sumcoevolity-cyrtodactylus${suffix}rate${rate}-sumcoevolity-results-nevents.txt"
    done
done

for rate in "020" "200" "2000"
do
    for suffix in "-" "-nopoly-"
    do
        pyco-sumtimes -f -z --x-limits 0.0 0.0011 -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumtimes-gekko${suffix}rate${rate}-" run-?-gekko${suffix}rate${rate}-state-run-1.log
        pyco-sumsizes -f --x-limits 0.0 0.001 -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumsizes-gekko${suffix}rate${rate}-" run-?-gekko${suffix}rate${rate}-state-run-1.log
        sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/sumcoevolity-gekko${suffix}rate${rate}-" -c "../ecoevolity-configs/gekko${suffix}rate${rate}.yml" run-?-gekko${suffix}rate${rate}-state-run-1.log
        pyco-sumevents -x "" -y "" -p "${plot_dir}/pyco-sumevents-gekko${suffix}rate${rate}-" -f --no-legend "${plot_dir}/sumcoevolity-gekko${suffix}rate${rate}-sumcoevolity-results-nevents.txt"
    done
done

for taxon in "cyrtodactylus" "gekko"
do
    for suffix in "-conc-" "-conc5-"
    do
        rate="200"
        time_upper="0.011"
        size_upper="0.0025"
        if [ "$taxon" = "gekko" ]
        then
            rate="2000"
            time_upper="0.0011"
            size_upper="0.001"
        fi
        pyco-sumtimes -f -z --x-limits 0.0 "$time_upper" -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumtimes-${taxon}${suffix}rate${rate}-" run-?-${taxon}${suffix}rate${rate}-state-run-1.log
        pyco-sumsizes -f --x-limits 0.0 "$size_upper"  -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumsizes-${taxon}${suffix}rate${rate}-" run-?-${taxon}${suffix}rate${rate}-state-run-1.log
        sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/sumcoevolity-${taxon}${suffix}rate${rate}-" -c "../ecoevolity-configs/${taxon}${suffix}rate${rate}.yml" run-?-${taxon}${suffix}rate${rate}-state-run-1.log
        pyco-sumevents -x "" -y "" -p "${plot_dir}/pyco-sumevents-${taxon}${suffix}rate${rate}-" -f --no-legend "${plot_dir}/sumcoevolity-${taxon}${suffix}rate${rate}-sumcoevolity-results-nevents.txt"
    done
done


# no data analyses
for rate in "020" "200"
do
    for suffix in "-" "-nopoly-"
    do
        pyco-sumtimes -f -z -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/no-data-pyco-sumtimes-cyrtodactylus${suffix}rate${rate}-" no-data-run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log
        pyco-sumsizes -f -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/no-data-pyco-sumsizes-cyrtodactylus${suffix}rate${rate}-" no-data-run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log
        sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/no-data-sumcoevolity-cyrtodactylus${suffix}rate${rate}-" -c "../ecoevolity-configs/cyrtodactylus${suffix}rate${rate}.yml" no-data-run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log
        pyco-sumevents -x "" -y "" -p "${plot_dir}/no-data-pyco-sumevents-cyrtodactylus${suffix}rate${rate}-" -f --no-legend "${plot_dir}/no-data-sumcoevolity-cyrtodactylus${suffix}rate${rate}-sumcoevolity-results-nevents.txt"
    done
done

for rate in "020" "200" "2000"
do
    for suffix in "-" "-nopoly-"
    do
        pyco-sumtimes -f -z -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/no-data-pyco-sumtimes-gekko${suffix}rate${rate}-" no-data-run-?-gekko${suffix}rate${rate}-state-run-1.log
        pyco-sumsizes -f -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/no-data-pyco-sumsizes-gekko${suffix}rate${rate}-" no-data-run-?-gekko${suffix}rate${rate}-state-run-1.log
        sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/no-data-sumcoevolity-gekko${suffix}rate${rate}-" -c "../ecoevolity-configs/gekko${suffix}rate${rate}.yml" no-data-run-?-gekko${suffix}rate${rate}-state-run-1.log
        pyco-sumevents -x "" -y "" -p "${plot_dir}/no-data-pyco-sumevents-gekko${suffix}rate${rate}-" -f --no-legend "${plot_dir}/no-data-sumcoevolity-gekko${suffix}rate${rate}-sumcoevolity-results-nevents.txt"
    done
done

for taxon in "cyrtodactylus" "gekko"
do
    for suffix in "-conc-" "-conc5-"
    do
        rate="200"
        if [ "$taxon" = "gekko" ]
        then
            rate="2000"
        fi
        pyco-sumtimes -f -z -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/no-data-pyco-sumtimes-${taxon}${suffix}rate${rate}-" no-data-run-?-${taxon}${suffix}rate${rate}-state-run-1.log
        pyco-sumsizes -f -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/no-data-pyco-sumsizes-${taxon}${suffix}rate${rate}-" no-data-run-?-${taxon}${suffix}rate${rate}-state-run-1.log
        sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/no-data-sumcoevolity-${taxon}${suffix}rate${rate}-" -c "../ecoevolity-configs/${taxon}${suffix}rate${rate}.yml" no-data-run-?-${taxon}${suffix}rate${rate}-state-run-1.log
        pyco-sumevents -x "" -y "" -p "${plot_dir}/no-data-pyco-sumevents-${taxon}${suffix}rate${rate}-" -f --no-legend "${plot_dir}/no-data-sumcoevolity-${taxon}${suffix}rate${rate}-sumcoevolity-results-nevents.txt"
    done
done


# make pretty single plots
# How I got these colors from matplotlib:
# import matplotlib
# v = matplotlib.cm.get_cmap("viridis")
# matplotlib.colors.rgb2hex(v(0.0))
connected_color="#440154"
# matplotlib.colors.rgb2hex(v(0.5))
maybe_color="#21918c"
# matplotlib.colors.rgb2hex(v(1.0))
not_color="#fde725"

cyrt_colors="$maybe_color $maybe_color $connected_color $not_color $not_color $connected_color $connected_color $maybe_color"
cyrt_drop_colors="$maybe_color $connected_color $not_color $not_color $connected_color $connected_color $maybe_color"
gekko_colors="$not_color $connected_color $not_color $connected_color $connected_color $maybe_color $connected_color $not_color"

for taxon in "cyrtodactylus" "gekko"
do
    for suffix in "-"
    do
        rate="200"
        time_ylabel=""
        size_ylabel="Cyrtodactylus population"
        comparison_colors="$cyrt_colors"
        ignore_arg="-i Palawan1"
        if [ "$taxon" = "gekko" ]
        then
            rate="2000"
            size_ylabel="Gekko population"
            comparison_colors="$gekko_colors"
            ignore_arg=""
        fi
        pyco-sumtimes -f -z -x "" -y "$time_ylabel" -b $burnin --colors $comparison_colors "${label_array[@]}" -p "${plot_dir}/pyco-sumtimes-${taxon}${suffix}rate${rate}-pretty-" run-?-${taxon}${suffix}rate${rate}-state-run-1.log
        if [ -n "$ignore_arg" ]
        then
            pyco-sumtimes -f -z -x "" -y "$time_ylabel" -b $burnin $ignore_arg --colors $cyrt_drop_colors "${label_array[@]}" -p "${plot_dir}/pyco-sumtimes-${taxon}${suffix}rate${rate}-pretty-dropped-" run-?-${taxon}${suffix}rate${rate}-state-run-1.log
        fi
        pyco-sumsizes -f -y "$size_ylabel" -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumsizes-${taxon}${suffix}rate${rate}-pretty-" run-?-${taxon}${suffix}rate${rate}-state-run-1.log
        pyco-sumevents -p "${plot_dir}/pyco-sumevents-${taxon}${suffix}rate${rate}-pretty-" -f "${plot_dir}/sumcoevolity-${taxon}${suffix}rate${rate}-sumcoevolity-results-nevents.txt"
    done
done

cd "$plot_dir"

for p in pyco-*.pdf
do
    pdfcrop "$p" "$p"
done

for p in grid-*.tex
do
    latexmk -pdf "$p"
done

for p in grid-*.pdf
do
    pdfcrop "$p" "$p"
done

cd "$current_dir"
