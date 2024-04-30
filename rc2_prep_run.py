#!/usr/bin/env python

from ToLJiraAuth import ToLJiraAuth
import JiraMethods as jm
import os
import re
import glob
import subprocess

species_dict = {
            'a': ['amphibians','',''],
            'b': ['bird','GallusGallus.GRCg7b,TaeniopygiaGuttata.bTaeGut1_4','aves_odb10'],
            'cb': ['non-vascular-plants','',''],
            'cs': ['non-vascular-plants','',''],
            'da': ['dicots','',''],
            'dc': ['dicots','',''],
            'dd': ['dicots','ArabidopsisThaliana.TAIR10,MalusDomestica.ASM211411v1,QuercusSuber.CorkOak1','eudicots_odb'],
            'dh': ['dicots','ArabidopsisThaliana.TAIR10,MalusDomestica.ASM211411v1,QuercusSuber.CorkOak1','eudicots_odb'],
            'dm': ['dicots','ArabidopsisThaliana.TAIR10,HelianthusAnnuus.HanXRQr1,QuercusSuber.CorkOak1','eudicots_odb'],
            'dr': ['dicots','ArabidopsisThaliana.TAIR10,MalusDomestica.ASM211411v1,QuercusSuber.CorkOak1','eudicots_odb'],
            # 'dm': ['','',''],
            'f': ['fish','Danio_rerio.GRCz11,Gadus_morhua.gadMor1,OryziasLatipes.ASM223467v1','actinopterygii_odb10'],
            'gd': ['fungi','',''],
            'gf': ['fungi','',''],
            'gr': ['fungi','',''],
            'gl': ['fungi','',''],
            'ht': ['platyhelminths','',''],
            'ic': ['insects','AnoplophoraGlabripennis.Agla_2,TriboliumCastaneum.Tcas5_2,PhotinusPyralis.Ppyr1_3,DendroctonusPonderosae.Dpon_F_20191213v2',''],
            'id': ['insects','ScaevaPyrastri.idScaPyr1,SyrittaPipiens.idSyrPip1,DrosophilaMelanogaster.Release6,AnophelesGambiae.AgamP3',''],
            'ie': ['insects','',''],
            'ih': ['insects','AphisGossypii.ASM2018417v2','RhopalosiphumMaidis.ASM367621v3','LaodelphaxStriatellus.ASM1714139v1'],
            'ii': ['insects','',''],
            'il': ['insects','PlutellaXylostella.ilPluXylo3,LeptideaSinapis.LSINAPIS,DanausPlexippus.Dpv3,BombyxMori.Bmori_2016v1','lepidoptera_odb10'],
            'iq': ['insects','CloenDipterum.CLODIP2,PlutellaXylostella.ilPluXylo3,AphisGossypii.ASM2018417v2',''],
            'in': ['insects','',''],
            'io': ['insects','',''],
            'iu': ['insects','',''],
            'iy': ['insects','',''],
            'ja': ['jellyfish','',''],
            'jh': ['jellyfish','',''],
            'js': ['jellyfish','',''],
            'ka': ['chordates','StyelaClava.ASM1312258v2,CionaIntestinalis.KH','metazoa_odb10'],
            'la': ['monocots','',''],
            'lp': ['monocots','AlloteropsisSemialata-ASEM_AUS1_V1,TriticumTurgidum-Svevo_v1,TyphaLatifolia-TyphaL0001',''],
            'ld': ['monocots','TriticumTurgidum.Svevo_v1,TyphaLatifolia.TyphaL0001','liliopsida_odb10'],
            'm': ['mammals','BosTaurus.ARSUCD1_3,CanisLupusFamiliaris.Dog10K_Tasha,FalisCatus.Fca126_mat1','mammalia_odb10'],
            'nr': ['nematode','OscheiusTipulae.ASM1342590v1,CaenorhabditisElegans.WBcel235,Gae_host.Gae','nematoda_odb10'],
            'nx': ['nematode','OscheiusTipulae.ASM1342590v1,CaenorhabditisElegans.WBcel235,Gae_host.Gae','nematoda_odb10'],
            'pe': ['protists','',''],
            'px': ['protists','',''],
            'py': ['protists','',''],
            'qq': ['arthropods','StegodyphusMimosarum.Stegodyphus_mimosarum_v1,DinothrombiumTinctorium.ASM367599v1,IoxdesScapularis.ASM1692078v2','arthropoda_odb10'],
            'qd': ['arthropods','',''],
            'qm': ['arthropods','',''],
            'qe': ['arthropods','',''],
            'od': ['sponges','CoccomyxaOrbi.COCOBI_1,CoccomyxaSubellipsoidae.CoccomyxaSubellipsoidaeV2,PicochlorumBPE23.ASM2520934v1','metazoa_odb10'],
            'oh': ['sponges','',''],
            'r': ['reptile','PodarcisMuralis.GCF004329235,PogonaVitticeps.pvi1',''],
            's': ['sharks','CallorhinchusMilii.IMCB_Cmil_1,RhincodonTypus.sRhiTyp1,SqualusSuckleyi.GSC_Ssuck_1',''],
            'tn': ['other-animal-phyla','',''],
            'tx': ['other-animal-phyla','',''],
            'uc': ['algae','',''],
            'uo': ['algae','',''],
            'uy': ['algae','',''],
            'xb': ['mollusc','OctopusBimaculoides.ASM119413v2,PomaceaCanaliculata.ASM307304v1','mollusca_odb10'],
            'xc': ['mollusc','PomaceaCanaliculata.ASM307304v1,TridacnaCrocea.GCA943736015_1,FragumFragum.GCA946902895_1,SpisulaSolida.GCA947247005_1','mollusca_odb10'],
            'xg': ['mollusc','',''],
            'wa': ['annelids','',''],
            'wc': ['annelids','',''],
            'wf': ['annelids','',''],
            'wg': ['annelids','',''],
            'wl': ['annelids','',''],
            'wk': ['annelids','',''],
            'ws': ['annelids','','']
}


def check_telo(tolid,treeval_path):

    with open(f"{treeval_path}/data/canonical.txt") as f:
        canon = f.read()
        print("====================")
        print(f"{tolid} - {get_scaffold_count(treeval_path)}")
        print("====================")
        print(f"Ends:")
        print(f"{get_scaffold_ends(treeval_path)}")
        print("====================")
        print(canon)
        print("====================")
        val = input(f"{tolid} - Set telo [TACG], check first 10 scaffolds (c), skip (s) or end (e)?\n")

        if val == "c":
            #check first 10 scaffolds
            print(get_scaffold_summary(treeval_path))
            val = check_telo(tolid,treeval_path)
        elif val == "e" or val == "s":
            return val
            # if enter any characters other than TACG then state invalid input and ask again.
        elif re.search("[^TACG]", val):
            print("Invalid telo")
            val = check_telo(tolid,treeval_path)
            # If valid input ask for confirmation
        else:
            approve = input(f"Is this correct {tolid} - {val}\n")
            if approve != "y":
                val = check_telo(tolid,treeval_path)
    
        return val

def get_scaffold_count(treeval_path):
    return run_command(f'grep ">" {treeval_path}/data/ref.fa | wc -l')

def get_scaffold_summary(treeval_path):
    return run_command(f'grep -m10 -B 10 -A 10 ">" {treeval_path}/data/ref.fa')

def get_scaffold_ends(treeval_path):
    return run_command(f'grep ">" {treeval_path}/data/ref.fa | head -n 1; grep ">" {treeval_path}/data/ref.fa | tail -n 1')

def run_command(cmd):

    process = subprocess.Popen(cmd,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE,
                            text = True,
                            shell = True
            )
    std_out, std_err = process.communicate()
    return std_out

def build_yaml(tolid, geval_type, telo_seq, tv_path, longread_type, pacbio_read_dir, hic_read_dir, map_order):

    ref_file_path = f"{tv_path}/data/ref.fa"

    # ref_stats = os.stat(ref_file_path)
    # if ref_stats.st_size > (1024 * 1024 * 1024 * 4):
    #     genome_size = "L"
    # else:
    #     genome_size = "S"

    sample_id = tolid.split("_")[0]
    asm_version = tolid.split("_")[1]

    # data_path = ref_file_path[:ref_file_path.rfind("/")].replace("_3", "_2").replace("_2", "_1")
    data_path = ref_file_path[:ref_file_path.rfind("/")]

    # with open(f"{data_path}/fasta.fofn") as ff:
    #     first_line = ff.readline()
    #     pacbio_read_dir = first_line[:first_line.rfind("/")+1]

    # with open(f"{data_path}/cram.fofn") as cf:
    #     first_line = cf.readline()
    #     hic_read_dir = first_line[:first_line.rfind("/")+1]

    regexed = re.search(r"([a-z]*)[A-Z][a-zA-Z]*[0-9]*",sample_id)
    species = regexed.group(1)

    # tja = ToLJiraAuth()
    # jql_request = f"project in ('RC', 'GRIT') AND 'Sample ID' ~ {sample_id} ORDER BY updated DESC"
    # results = tja.auth_jira.search_issues(jql_request)

    # # Return most recently created entry if there are multiple with same name.
    # issue = tja.auth_jira.issue(results[0])
    # telo_seq = jm.get_telo_seq(issue)


    if telo_seq == "":
        telo_seq = "TTTTTTTTTT"

    # Create input yaml
    input_yaml_contents = f'''assembly:
  assem_level: scaffold
  assem_version: {asm_version}
  sample_id: {sample_id}
  latin_name: to_provide_taxonomic_rank
  defined_class: {species_dict[species][0]}
  project_id: {geval_type}
reference_file: {ref_file_path}
map_order: {map_order}
assem_reads:
  read_type: {longread_type}
  read_data: {pacbio_read_dir}/fasta
  supplementary_data: path
hic_data:
  hic_cram: {hic_read_dir}/
  hic_aligner: bwamem2
kmer_profile:
  # kmer_length will act as input for kmer_read_cov fastk and as the name of folder in profile_dir
  kmer_length: 31
  dir: {pacbio_read_dir}/
alignment:
  data_dir: /lustre/scratch123/tol/resources/treeval/gene_alignment_data/
  common_name: "" # For future implementation (adding bee, wasp, ant etc)
  geneset_id: "{species_dict[species][1]}"
  #Path should end up looking like "{{data_dir}}{{classT}}/{{common_name}}/csv_data/{{geneset}}-data.csv"
self_comp:
  motif_len: 0
  mummer_chunk: 10
synteny:
  synteny_genome_path: /lustre/scratch123/tol/resources/treeval/synteny/
  synteny_genomes: ""
intron:
  size: "50k"
telomere:
  teloseq: {telo_seq}
busco:
  lineages_path: /lustre/scratch123/tol/resources/busco/v5
  lineage: {species_dict[species][2]}'''

    # Create fasta.fofn
    with open(f"{tv_path}/{tolid}.yaml", 'w') as input_yaml:
        input_yaml.write(input_yaml_contents)

def get_project(title):
    if ' Darwin assembly' in title:
        return 'DTOL'
    elif ' TOL assembly' in title:
        return 'TOL'
    elif ' ASG assembly' in title:
        return 'ASG'
    elif ' VGP assembly' in title:
        return 'VGP'
    elif ' BGE assembly' in title:
        return 'BGE'
    elif ' GenomeArk assembly' in title:
        return 'VGP'
    elif ' ERGA assembly' in title:
        return 'ERGA'
    elif ' faculty assembly' in title:
        return 'TOL'
    elif ' external assembly' in title:
        return 'EXT'
    elif ' assembly' in title:
        return 'TOL'

def main():

    # Get list awaiting telo check
    tja = ToLJiraAuth()
    jql_request = f"project = RC AND status = 'HiC Building' AND assignee = 'Will Eagles' AND 'Telomere motif k-mer length' is EMPTY ORDER BY priority DESC, updated DESC"
    # jql_request = f"status in ('HiC Building', 'geval analysis', 'curation') AND assignee = 'Will Eagles' ORDER BY priority DESC, updated DESC"
    # jql_request = f"key = 'RC-1347'"
    results = tja.auth_jira.search_issues(jql_request)

    # print(results)
    # Return most recently created entry if there are multiple with same name.
    telos_ready = []
    for result in results:
        issue = tja.auth_jira.issue(result)
        
        species_id = jm.get_species_id(issue)

        if species_id == "idCulPerx1":
            continue

        hap1_id, hap2_id, merged_id = jm.get_treeval_run_ids(issue)

        treeval_run_path = os.path.dirname(os.path.dirname(jm.get_hap1_path(issue)))

        hap1_path = f"{treeval_run_path}/treeval/{hap1_id}"
        hap2_path = f"{treeval_run_path}/treeval/{hap2_id}"
        merged_path = f"{treeval_run_path}/treeval/{merged_id}"

        if not glob.glob(f"{hap1_path}/{hap1_id}.yaml"):
            if os.path.exists(f"{hap1_path}/data/canonical.txt"):
                if not os.path.exists(f"{hap1_path}/telomere"):
                    telos_ready.append(f"{hap1_path}")

        if not glob.glob(f"{hap2_path}/{hap2_id}.yaml"):
            if os.path.exists(f"{hap2_path}/data/canonical.txt"):
                if not os.path.exists(f"{hap2_path}/telomere"):
                    telos_ready.append(f"{hap2_path}")

        if not glob.glob(f"{merged_path}/{merged_id}.yaml"):
            if os.path.exists(f"{merged_path}/data/canonical.txt"):
                if not os.path.exists(f"{merged_path}/telomere"):
                    telos_ready.append(f"{merged_path}")

    telos = {}
    print(telos_ready)
    for tv_path_int in range(len(telos_ready)):

        tv_path = telos_ready[tv_path_int]
        telo_tolid = os.path.basename(tv_path)
        tc_out = check_telo(telo_tolid, tv_path)
        # if 's' skip to next sample,
        if tc_out == 's':
            continue
        # if 'e' end process
        elif tc_out == 'e':
            break
        else:      
            telos[telo_tolid] = (tc_out,tv_path)

    print("")
    print("TELO UPDATED - JIRA")
    print("")
    # Loop through 
    for result in results:
        issue = tja.auth_jira.issue(result)
        species_id = jm.get_species_id(issue)

        # if species_id == "idCulPerx1":
        #     continue

        longread_type = jm.get_longread_type(issue)
        pacbio_dir = jm.get_pacbio_dir(issue)
        hic_dir = jm.get_hic_read_dir(issue)
        # longread_type = "ont"
        for key,val in telos.items():

            hap1_id, hap2_id, merged_id = jm.get_treeval_run_ids(issue)
            if key == merged_id:
                map_order = "unsorted"
            else:
                map_order = "length"

            # print(key)
            if key[:-2] == species_id:

                project_name = get_project(issue.fields.summary)

                build_yaml(key, project_name, val[0], val[1], longread_type, pacbio_dir, hic_dir, map_order)

                # Check yaml build worked.
                if not glob.glob(f"{val[1]}/{key}.yaml"):
                    print(f"{key[:-2]} failed")
                else:
                    issue.update(fields=  {'customfield_11650': val[0],
                                    'customfield_11651' : len(val[0])
                                }
                        )
                    with open(f"telomere_log.txt", 'a') as tl:
                        tl.write(f"{key[:-2]} - {val[0]}\n")
                    print(f"{key} - {val[0]}")
                    # break

                    

if __name__ == "__main__":
    main()