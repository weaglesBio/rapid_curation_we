#!/bin/bash


for f in /lustre/scratch12*/tol/*/*/data/*/*/assembly/draft/treeval/*/; do
    sample_name=$( echo "$f" | cut -d "/" -f 13 )
    if [ -f "$f/${sample_name}.yaml" ] &&  [ ! -d "$f/tv_output" ]; then
        echo ${sample_name}
        ./tv_launch.sh -e R -t ${sample_name}
    fi
done

for f in /lustre/scratch12*/tol/teams/*/data/*/*/*/assembly/draft/treeval/*/; do
    sample_name=$( echo "$f" | cut -d "/" -f 14 )
    if [ -f "$f/${sample_name}.yaml" ] && [ ! -d "$f/tv_output" ]; then
        echo ${sample_name}
        ./tv_launch.sh -e R -t ${sample_name}
    fi
done
