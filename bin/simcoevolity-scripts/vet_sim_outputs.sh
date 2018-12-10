#!/bin/bash

expected_nlines=1502

for qsub_path in ../../data/genomes/msg/ecoevolity-simulations/*/batch*/*simcoevolity-sim-*-config-run-*-qsub.sh
do
    to_run="${qsub_path/-qsub.sh/}"
    run_number="${to_run##*-}"
    qsub_file_name="$(basename "$qsub_path")"
    dir_path="$(dirname "$qsub_path")"
    base_prefix="${qsub_file_name%-run-*}"
    file_prefix="run-${run_number}-${base_prefix}"
    prefix="${dir_path}/${file_prefix}"
    out_file="${prefix}.yml.out"
    state_log="${prefix}-state-run-1.log"
    op_log="${prefix}-operator-run-1.log"

    # Consolidate state logs if run was restarted 
    extra_run_number=2
    while [ -e "${prefix}-state-run-${extra_run_number}.log" ]
    do
        mv "${prefix}-state-run-${extra_run_number}.log" "$state_log"
        ((++extra_run_number))
    done

    # Consolidate operator logs if run was restarted 
    extra_run_number=2
    while [ -e "${prefix}-operator-run-${extra_run_number}.log" ]
    do
        mv "${prefix}-operator-run-${extra_run_number}.log" "$op_log"
        ((++extra_run_number))
    done

    if [ ! -e "$out_file" ] 
    then
        echo "No stdout: $qsub_path" 
        echo "$qsub_path" >> "reruns.txt"
        continue
    fi

    if [ ! -e "$state_log" ] 
    then
        echo "No state log: $qsub_path" 
        echo "$qsub_path" >> "reruns.txt"
        continue
    fi

    runtime_line="$(grep "Runtime:" "$out_file")"
    if [ -z "$runtime_line" ]
    then 
        echo "Incomplete stdout: $qsub_path" 
        echo "$qsub_path" >> "reruns.txt"
        continue
    fi

    nlines="$(wc -l "$state_log" | awk '{print $1}')"
    if [ "$nlines" != "$expected_nlines" ] 
    then
        echo "Incomplete log: $qsub_path" 
        echo "$qsub_path" >> "reruns.txt"
        continue
    fi

    seed_line="$(grep "seed" "$qsub_path")"
    after_seed="${seed_line##*--seed}"
    expected_seed="$(echo ${after_seed%%--*} | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    seed_line="$(grep -i "seed" "$out_file")"
    seed="$(echo ${seed_line##*:} | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    
    if [ "$expected_seed" != "$seed" ]
    then
        echo "Bad seed: $qsub_path"
        echo "$qsub_path" >> "reruns.txt"
        continue
    fi
done
