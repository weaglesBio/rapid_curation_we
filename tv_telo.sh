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

module load kmer-jellyfish/2.3.1--h4ac6f70_0
cd $path/data
echo "python /nfs/treeoflife-01/teams/tola/users/we3/source/rapid_curation_we/telo_finder.py ref.fa --telofile /nfs/treeoflife-01/teams/tola/users/we3/source/rapid_curation_we/telomere_list.txt --tolid $tolid"|bsub -J telo_${tolid} -q normal -o d.o -e d.e -n 1 -M40000 -R'select[mem>40000] rusage[mem=40000] span[hosts=1]'