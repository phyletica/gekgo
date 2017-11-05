#!/bin/bash
#PBS -l nodes=1:ppn=1
#PBS -l walltime=1:00:00
#PBS -j oe 

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
-l "Kinabalu1" "Kinabalu"
-l "root-Palawan1" "Palawan-Kinabalu Root"
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
-l "Mindoro9" "Mindoro"
-l "Caluya9" "Caluya"
-l "root-Mindoro9" "Mindoro-Caluya Root"
-l "Lubang10" "Lubang"
-l "Luzon10" "Luzon"
-l "root-Lubang10" "Lubang-Luzon Root"
-l "MaestreDeCampo11" "Maestre De Campo"
-l "Masbate11" "Masbate"
-l "root-MaestreDeCampo11" "Maestre De Campo-Masbate Root"
-l "Negros12" "Negros"
-l "Panay12" "Panay"
-l "root-Negros12" "Negros-Panay Root"
-l "Sabtang13" "Sabtang"
-l "Batan13" "Batan"
-l "root-Sabtang13" "Sabtang-Batan Root"
-l "Romblon14" "Romblon"
-l "Tablas14" "Tablas"
-l "root-Romblon14" "Romblon-Tablas Root"
-l "CamiguinNorte15" "Camiguin Norte"
-l "Dalupiri15" "Dalupiri"
-l "root-CamiguinNorte15" "Camiguin Norte-Dalupiri Root"'

convert_labels_to_array $labels

for rate in "020" "200"
do
    for suffix in "-" "-nopoly-"
    do
        pyco-sumtimes -f -z -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumtimes-cyrtodactylus${suffix}rate${rate}-" run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log
        pyco-sumsizes -f -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumsizes-cyrtodactylus${suffix}rate${rate}-" run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log
        sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/sumcoevolity-cyrtodactylus${suffix}rate${rate}-" -c "../ecoevolity-configs/cyrtodactylus${suffix}rate${rate}.yml" run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log
        pyco-sumevents -p "${plot_dir}/pyco-sumevents-cyrtodactylus${suffix}rate${rate}-" -f --no-legend "${plot_dir}/sumcoevolity-cyrtodactylus${suffix}rate${rate}-sumcoevolity-results-nevents.txt"
    done
done

for rate in "020" "200" "2000"
do
    for suffix in "-" "-nopoly-"
    do
        pyco-sumtimes -f -z -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumtimes-gekko${suffix}rate${rate}-" run-?-gekko${suffix}rate${rate}-state-run-1.log
        pyco-sumsizes -f -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumsizes-gekko${suffix}rate${rate}-" run-?-gekko${suffix}rate${rate}-state-run-1.log
        sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/sumcoevolity-gekko${suffix}rate${rate}-" -c "../ecoevolity-configs/gekko${suffix}rate${rate}.yml" run-?-gekko${suffix}rate${rate}-state-run-1.log
        pyco-sumevents -p "${plot_dir}/pyco-sumevents-gekko${suffix}rate${rate}-" -f --no-legend "${plot_dir}/sumcoevolity-gekko${suffix}rate${rate}-sumcoevolity-results-nevents.txt"
    done
done


# no data analyses
for rate in "020" "200"
do
    for suffix in "-" "-nopoly-"
    do
        pyco-sumtimes -f -z -b $burnin "${label_array[@]}" -p "${plot_dir}/no-data-pyco-sumtimes-cyrtodactylus${suffix}rate${rate}-" no-data-run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log
        pyco-sumsizes -f -b $burnin "${label_array[@]}" -p "${plot_dir}/no-data-pyco-sumsizes-cyrtodactylus${suffix}rate${rate}-" no-data-run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log
        sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/no-data-sumcoevolity-cyrtodactylus${suffix}rate${rate}-" -c "../ecoevolity-configs/cyrtodactylus${suffix}rate${rate}.yml" no-data-run-?-cyrtodactylus${suffix}rate${rate}-state-run-1.log
        pyco-sumevents -p "${plot_dir}/no-data-pyco-sumevents-cyrtodactylus${suffix}rate${rate}-" -f --no-legend "${plot_dir}/no-data-sumcoevolity-cyrtodactylus${suffix}rate${rate}-sumcoevolity-results-nevents.txt"
    done
done

for rate in "020" "200" "2000"
do
    for suffix in "-" "-nopoly-"
    do
        pyco-sumtimes -f -z -b $burnin "${label_array[@]}" -p "${plot_dir}/no-data-pyco-sumtimes-gekko${suffix}rate${rate}-" no-data-run-?-gekko${suffix}rate${rate}-state-run-1.log
        pyco-sumsizes -f -b $burnin "${label_array[@]}" -p "${plot_dir}/no-data-pyco-sumsizes-gekko${suffix}rate${rate}-" no-data-run-?-gekko${suffix}rate${rate}-state-run-1.log
        sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/no-data-sumcoevolity-gekko${suffix}rate${rate}-" -c "../ecoevolity-configs/gekko${suffix}rate${rate}.yml" no-data-run-?-gekko${suffix}rate${rate}-state-run-1.log
        pyco-sumevents -p "${plot_dir}/no-data-pyco-sumevents-gekko${suffix}rate${rate}-" -f --no-legend "${plot_dir}/no-data-sumcoevolity-gekko${suffix}rate${rate}-sumcoevolity-results-nevents.txt"
    done
done

cd "$current_dir"
