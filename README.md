# rapid_curation_we


module load conda
conda activate grit_curation

## Step 1 - Prepare files for TreeVal:

## Step 2 - 

telo_finder.py /lustre/scratch124/tol/projects/asg/data/annelids/Pterobdella_sp._o_SKG-2022/assembly/draft/treeval/wcPteSpea6_1/data/ref.fa --telofile telomere_list.txt --tolid wcPteSpea6q


## Step 3 - 


## Step 4 - 


cd /lustre/scratch124/tol/projects/darwin/data/fish/Scardinius_erythrophthalmus/assembly/draft/treeval/fScaEry2_1/data
echo 'python /nfs/treeoflife-01/teams/tola/users/we3/source/rapid_curation_we/telo_finder.py ref.fa --telofile /nfs/treeoflife-01/teams/tola/users/we3/source/rapid_curation_we/telomere_list.txt --tolid fScaEry2_1'|bsub -J telo_fScaEry2_1 -q normal -o d.o -e d.e -n 1 -M40000 -R'select[mem>40000] rusage[mem=40000] span[hosts=1]'
cd /lustre/scratch124/tol/projects/darwin/data/fish/Scardinius_erythrophthalmus/assembly/draft/treeval/fScaEry2_2/data
echo 'python ~alt/python/bin/telo_finder.py ref.fa --telofile /nfs/treeoflife-01/teams/tola/users/we3/source/rapid_curation_we/telomere_list.txt --tolid fScaEry2_2'|bsub -J telo_fScaEry2_2 -q normal -o d.o -e d.e -n 1 -M40000 -R'select[mem>40000] rusage[mem=40000] span[hosts=1]'
cd /lustre/scratch122/tol/data/a/5/e/1/6/d/Culex_laticinctus/assembly/draft/treeval/idCulLati1_1/data
echo 'python /nfs/treeoflife-01/teams/tola/users/we3/source/rapid_curation_we/telo_finder.py ref.fa --telofile /nfs/treeoflife-01/teams/tola/users/we3/source/rapid_curation_we/telomere_list.txt --tolid idCulLati1_1'|bsub -J telo_idCulLati1_1 -q normal -o d.o -e d.e -n 1 -M40000 -R'select[mem>40000] rusage[mem=40000] span[hosts=1]'
cd /lustre/scratch122/tol/data/a/5/e/1/6/d/Culex_laticinctus/assembly/draft/treeval/idCulLati1_2/data
echo 'python /Volumes/treeoflife-01/teams/tola/users/we3/source/rapid_curation_we/telo_finder.py ref.fa --telofile /nfs/treeoflife-01/teams/tola/users/we3/source/rapid_curation_we/telomere_list.txt --tolid idCulLati1_2'|bsub -J telo_idCulLati1_2 -q normal -o d.o -e d.e -n 1 -M40000 -R'select[mem>40000] rusage[mem=40000] span[hosts=1]'


./tv_post.sh -t wcPteSpea6_1 -p /lustre/scratch124/tol/projects/asg/data/annelids/Pterobdella_sp._o_SKG-2022/assembly/draft/treeval/wcPteSpea6_1/
./tv_post.sh -t ilTheJuni1_1 -p /lustre/scratch124/tol/projects/darwin/data/insects/Thera_juniperata/assembly/draft/treeval/ilTheJuni1_1/
./tv_post.sh -t ilTheJuni1_2 -p /lustre/scratch124/tol/projects/darwin/data/insects/Thera_juniperata/assembly/draft/treeval/ilTheJuni1_2/

fScaEry2 - TTAGGG
idCul - none



./tv_telo.sh -t jaCalGrac1_1 -p /lustre/scratch124/tol/projects/asg/data/jellyfish/Callogorgia_gracilis/assembly/draft/treeval/jaCalGrac1_1
./tv_telo.sh -t jaCypSala7_1 -p /lustre/scratch124/tol/projects/asg/data/jellyfish/Cyphastrea_salae/assembly/draft/treeval/jaCypSala7_1
./tv_telo.sh -t bColPal1_1 -p /lustre/scratch124/tol/projects/darwin/data/birds/Columba_palumbus/assembly/draft/treeval/bColPal1_1
./tv_telo.sh -t ilEreAlbe1_1 -p /lustre/scratch124/tol/projects/tol/data/insects/Erebia_albergana/assembly/draft/treeval/ilEreAlbe1_1
./tv_telo.sh -t ilMecPoly1_1 -p /lustre/scratch125/tol/teams/meier/data/assemblies_Sanger/insects/Mechanitis_polymnia/assembly/draft/treeval/ilMecPoly1_1
./tv_telo.sh -t ilMecPoly1_2 -p /lustre/scratch125/tol/teams/meier/data/assemblies_Sanger/insects/Mechanitis_polymnia/assembly/draft/treeval/ilMecPoly1_2
./tv_telo.sh -t ngDicVivi2_1 -p /lustre/scratch124/tol/projects/tol/data/nematodes/Dictyocaulus_viviparus/assembly/draft/treeval/ngDicVivi2_1
./tv_telo.sh -t ngDicVivi2_2 -p /lustre/scratch124/tol/projects/tol/data/nematodes/Dictyocaulus_viviparus/assembly/draft/treeval/ngDicVivi2_2



touch /lustre/scratch124/tol/projects/darwin/data/insects/Agapeta_zoegana/assembly/draft/treeval/ilAgaZoeg1_1/data/canonical.txt
touch /lustre/scratch124/tol/projects/darwin/data/insects/Agapeta_zoegana/assembly/draft/treeval/ilAgaZoeg1_2/data/canonical.txt
touch /lustre/scratch124/tol/projects/darwin/data/insects/Argyresthia_cupressella/assembly/draft/treeval/ilArgCupr1_1/data/canonical.txt
touch /lustre/scratch124/tol/projects/darwin/data/insects/Argyresthia_cupressella/assembly/draft/treeval/ilArgCupr1_2/data/canonical.txt
touch /lustre/scratch125/tol/teams/meier/data/assemblies_Sanger/insects/Hypoleria_sarepta/assembly/draft/treeval/ilHypSare1_1/data/canonical.txt
touch /lustre/scratch125/tol/teams/meier/data/assemblies_Sanger/insects/Hypoleria_sarepta/assembly/draft/treeval/ilHypSare1_2/data/canonical.txt
touch /lustre/scratch125/tol/teams/meier/data/assemblies_Sanger/insects/Methona_grandior/assembly/draft/treeval/ilMetGran1_1/data/canonical.txt
touch /lustre/scratch125/tol/teams/meier/data/assemblies_Sanger/insects/Methona_grandior/assembly/draft/treeval/ilMetGran1_2/data/canonical.txt