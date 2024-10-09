#!/bin/bash

shopt -s extglob

# Make list of all samples with all files present plus hic_done
# rc_data_path="/lustre/scratch123/tol/teams/tola/treeval_runs/RC"
arrSample=()
arrSuccess=()
arrFail=()
samples_to_skip=("mEquCab1_3")
# for f in $rc_data_path/*/; do
for f in /lustre/scratch12*/tol/*/*/data/*/*/assembly/draft/treeval/*/; do

    sample_name=$( echo "$f" | cut -d "/" -f 13 )
    if [[ ! " ${samples_to_skip[*]} " =~ " ${sample_name} " ]]; then
        if [ -d "/lustre/scratch123/tol/share/grit-higlass/data_to_load/${sample_name}" ] ; then
            if [ -d "$f/working/work" ] ; then
                arrSample+=(${f})
            fi
        fi
    fi
done

for f in /lustre/scratch12*/tol/*/*/data/*/*/*/assembly/draft/treeval/*/; do

    sample_name=$( echo "$f" | cut -d "/" -f 14 )
    if [[ ! " ${samples_to_skip[*]} " =~ " ${sample_name} " ]]; then
        if [ -d "/lustre/scratch123/tol/share/grit-higlass/data_to_load/${sample_name}" ] ; then
            if [ -d "$f/working/work" ] ; then
                arrSample+=(${f})
            fi
        fi
    fi
done



# for f in /lustre/scratch125/tol/teams/*/data/*/*/*/assembly/draft/treeval/*/; do

#     sample_name=$( echo "$f" | cut -d "/" -f 14 )
#     if [[ ! " ${samples_to_skip[*]} " =~ " ${sample_name} " ]]; then
#         if [ -d "/lustre/scratch123/tol/share/grit-higlass/data_to_load/${sample_name}" ] ; then
#             if [ -d "$f/working/work" ] ; then
#                 arrSample+=(${f})
#             fi
#         fi
#     fi
# done

echo ""
echo "To cleanup:"
for sample in "${arrSample[@]}"; do
    echo "${sample}"
done
read -p "Continue? " -n 1 -r 
echo
if [[ $REPLY =~ ^[Yy]$ ]] 
then

# Loop through all samples 
for sample in "${arrSample[@]}"; do
echo "Running ${sample}"
cd ${sample}

# sample_name=${sample}
# rm -rf -v !(higlass)
rm -r working/work
# rm -r /nfs/treeoflife-01/teams/tola/users/we3/check_pretext/${sample_name}_hr.pretext
# rm -r tv_output
# rm -r gap
# rm -r data
# rm -r coverage
# rm -r telomere
# rm -r pretext
# rm -r repeat

if [ -d "$rc_data_path/${sample}/telomere" ] && [ -d "$rc_data_path/${sample}/repeat" ] && [ -d "$rc_data_path/${sample}/pretext" ] && [ -d "$rc_data_path/${sample}/gap" ] && [ -d "$rc_data_path/${sample}/coverage" ] ; then
arrFail+=(${sample})
else
arrSuccess+=(${sample})
fi
done

    # # Revert failed 
    # for sample in "${arrFail[@]}"; do
    #     echo "Removing progress on ${sample}"
    #     cd /lustre/scratch123/tol/teams/grit/geval_pipeline/geval_runs/rc/${sample}
    #     mv pretext hic
    #     rm /nfs/team135/pretext_maps/${sample}.pretext
    #     rm -r higlass
    #     rm -r /lustre/scratch123/tol/share/grit-higlass/data_to_load/${sample}
    # done

    echo ""
    echo "Completed:"
    for sample in "${arrSuccess[@]}"; do
        echo "${sample}"
    done
    echo ""
    echo "Failed:"
    for sample in "${arrFail[@]}"; do
        echo "${sample}"
    done

fi