#!/bin/bash

while getopts "e:t:c:" arg; do
  case $arg in
    e)
      entry=$OPTARG
      ;;
    t)
      tolid=$OPTARG
      ;;
    c)
      config_path=$OPTARG
      ;;
  esac
done


if [ ${entry} == "R" ]
then
  rapid_entry=" -entry RAPID_TOL"
else
  rapid_entry=""
fi

if [ ${config_path} ]
then
  extras_config=" -config ${config_path}"
else
  extras_config=""
fi

nftower_config="/nfs/users/nfs_w/we3/.nftowerconfig"
repo_path="/nfs/treeoflife-01/teams/tola/users/we3/source/treeval"
# sample=$(echo $tolid | rev | cut -c3- | rev)
# Get full path from tolid
for f in /lustre/scratch12*/tol/*/*/data/*/*/assembly/draft/treeval/${tolid}/; do
  if [ -d "${f}" ]; then
    if [ ! -d ${f}working ]; then
      mkdir "${f}working"
    fi

    cd "${f}working"
    module load ISG/singularity/3.11.4
    module load conda
    conda activate nf-core_2.11
    bsub -e nf_run.e -o nf_run.o -n 2 -q oversubscribed -M2000 -R'select[mem>2000] rusage[mem=2000] span[hosts=1]' "nextflow run ${repo_path}/main.nf -profile sanger,singularity${rapid_entry} --input ${f}${tolid}.yaml --outdir ${f}tv_output --hook_url https://hooks.slack.com/services/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 -config ${nftower_config}${extras_config} -plugins nf-co2footprint -resume"
  fi
done
for f in /lustre/scratch12*/tol/teams/*/data/*/*/*/assembly/draft/treeval/${tolid}/; do
  if [ -d "${f}" ]; then
    if [ ! -d ${f}working ]; then
      mkdir "${f}working"
    fi

    cd "${f}working"
    module load ISG/singularity/3.11.4
    module load conda
    conda activate nf-core_2.11
    bsub -e nf_run.e -o nf_run.o -n 2 -q oversubscribed -M2000 -R'select[mem>2000] rusage[mem=2000] span[hosts=1]' "nextflow run ${repo_path}/main.nf -profile sanger,singularity${rapid_entry} --input ${f}${tolid}.yaml --outdir ${f}tv_output --hook_url https://hooks.slack.com/services/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 -config ${nftower_config}${extras_config} -plugins nf-co2footprint -resume"
  fi
done
