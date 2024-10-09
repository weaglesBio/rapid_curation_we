#!/bin/bash

while getopts "t:p:" arg; do
  case $arg in
    t)
      tolid=$OPTARG
      ;;    
    p)
      path=$OPTARG
      ;;
  esac
done

nftower_config="/nfs/users/nfs_w/we3/.nftowerconfig"
repo_path="/nfs/treeoflife-01/teams/tola/users/we3/source/higlass_digest"
# sample=$(echo $tolid | rev | cut -c3- | rev)

# path=""
# # Get full path from tolid
# for f in /lustre/scratch12*/tol/*/*/data/*/*/assembly/draft/treeval/${tolid}/post/; do
#   path="${f}"
# done
# for f in /lustre/scratch12*/tol/teams/*/data/*/*/*/assembly/draft/treeval/${tolid}/post/; do
#   path="${f}"
# done

if [ -d "${path}/post" ]; then

    if [ ! -d ${path}/post/working ]; then
        mkdir "${path}/post/working"
    fi

    cd ${path}/post/working

    unset PYTHONPATH
    export MODULEPATH=$MODULEPATH:/software/treeoflife/custom-installs/modules
    module load nextflow/23.10.0-5889
    export MODULEPATH=$MODULEPATH:/software/modules/
    module load ISG/singularity

    bsub -e nf_run_p.e -o nf_run_p.o -n 2 -q normal -M1000 -R'select[mem>1000] rusage[mem=1000] span[hosts=1]' "nextflow run ${repo_path}/main.nf -profile sanger,singularity --input ${path}/post/${tolid}_post.yaml --outdir ${path}/post/hg_link"
fi
