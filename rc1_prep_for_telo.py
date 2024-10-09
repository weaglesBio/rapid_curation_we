#!/usr/bin/env python

from ToLJiraAuth import ToLJiraAuth
import JiraMethods as jm
import os
import glob
import gzip
import shutil
import subprocess


def combine_and_rename_fasta(hap1_path, hap2_path, merged_path ):
    return run_command(f'bash create_merged_fasta.sh -fasta1 {hap1_path} -fasta2 {hap2_path} -output {merged_path}')

def combine_fasta(hap1_path, hap2_path, merged_path ):
    return run_command(f'cat {hap1_path} {hap2_path} > {merged_path}')

def launch_telo_finder(tolid, path):
    return run_command(f'bash tv_telo.sh -t {tolid} -p {path} ')

def get_first_line_zipped(path):
    return run_command(f'zcat {path} | head -1 ')

def run_command(cmd):

    process = subprocess.Popen(cmd,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE,
                            text = True,
                            shell = True
            )
    std_out, std_err = process.communicate()
    return std_out


def main():

    tja = ToLJiraAuth()
    # jql_request = f"'Sample ID' ~ 'xcSepAtla11'"
    jql_request = f"project = RC AND status = 'HiC Building' AND assignee is EMPTY ORDER BY priority DESC, updated DESC"
    # jql_request = f"project = GRIT AND status = 'geval analysis' AND 'Sample ID' ~ 'bColPal1' AND assignee is EMPTY ORDER BY priority DESC, updated DESC"
    results = tja.auth_jira.search_issues(jql_request)

    # Return most recently created entry if there are multiple with same name.

    fail_summary = {}
    successes = {}

    for result in results:
        fails = []
        issue = tja.auth_jira.issue(result)
        species_id = jm.get_species_id(issue)

        jql_check_count_request = f"project in (RC, GRIT) AND 'Sample ID' ~ '{species_id}'"
        canonical_run_count = len(tja.auth_jira.search_issues(jql_check_count_request))

        # # Check pretext map for existing
        # pretext_run_count = 0

        # # Use higher for canonical run count.
        # if jira_run_count > pretext_run_count:
        #     canonical_run_count = jira_run_count
        # else:
        #     canonical_run_count = pretext_run_count

        tolid_hap1 = f"{species_id}_{canonical_run_count}"
        tolid_merged = f"{species_id}_{canonical_run_count + 1}"

        # Check if combine is required
        combine_for_curation = jm.get_combine_for_curation_status(issue)
        hap1_path = jm.get_hap1_path(issue)
        hap2_path = jm.get_hap2_path(issue)
        decon_hap1_path = hap1_path.replace(".fa.gz", ".decontaminated.fa.gz")
        decon_hap2_path = hap2_path.replace(".fa.gz", ".decontaminated.fa.gz")        

        # For time being always using hap1

        decon_hap1_scaffold = get_first_line_zipped(decon_hap1_path)
        decon_hap2_scaffold = get_first_line_zipped(decon_hap2_path)

        decon_hap1_scaffold = decon_hap1_scaffold.strip()
        decon_hap2_scaffold = decon_hap2_scaffold.strip()

        print(f"Checking {species_id}")

        if not os.path.exists(decon_hap1_path):
            fails.append("No hap1 ref.fa available.")
        
        if decon_hap1_scaffold != ">SCAFFOLD_1" and decon_hap1_scaffold != ">HAP1_SCAFFOLD_1":
            fails.append(f"Invalid hap1 scaffold name '{decon_hap1_scaffold}'.")

        # If combine requested - check haplotigs available
        if combine_for_curation:
            if not os.path.exists(decon_hap2_path):
                fails.append("No hap2 ref.fa available.")

            if not decon_hap2_scaffold == ">HAP2_SCAFFOLD_1":
                fails.append(f"Invalid hap2 scaffold name '{decon_hap2_scaffold}'.")

        pacbio_dir = jm.get_pacbio_dir(issue)
        if not glob.glob(f"{pacbio_dir}/fasta/*fasta.gz"):
            print(f"{pacbio_dir}/fasta/*fasta.gz")
            fails.append("No pacbio reads found.")


        hic_read_dir = jm.get_hic_read_dir(issue)
        if not glob.glob(f"{hic_read_dir}/*.cram"):
            print(f"{hic_read_dir}/*.cram")
            fails.append("No .cram found.")

        # Get path to ../assembly/draft directory
        assem_draft_dir = os.path.dirname(os.path.dirname(decon_hap1_path))
        treeval_dir = f"{assem_draft_dir}/treeval"
        assembly_hap1_dir = f"{treeval_dir}/{tolid_hap1}"
        assembly_merged_dir = f"{treeval_dir}/{tolid_merged}"

        if not os.path.exists(treeval_dir):
            os.mkdir(treeval_dir)
        else:
            if os.path.exists(assembly_hap1_dir):
                fails.append("Hap1 run directory already exists.")
        
            if os.path.exists(assembly_merged_dir):
                fails.append("Merged run directory already exists.")

        if len(fails) == 0:            
            # Assign self to ticket
            tja.auth_jira.assign_issue(issue, 'we3')
            # Start watching ticket
            tja.auth_jira.add_watcher(issue, 'we3')

            # Set Treeval value
            if combine_for_curation:
                issue.update(fields={'customfield_12200': f"hap1: {tolid_hap1}, merged: {tolid_merged}"})
            else:
                issue.update(fields={'customfield_12200': f"hap1: {tolid_hap1}"})

            # Copy assembly and convert to ref.fa for hap1
            os.mkdir(assembly_hap1_dir)
            os.mkdir(f"{assembly_hap1_dir}/data")
            with open(f"{assembly_hap1_dir}/data/ref.fa", 'wb') as f_out:
                with gzip.open(decon_hap1_path,'rb') as f_pri_in:
                    shutil.copyfileobj(f_pri_in, f_out)

            # Create fasta.fofn
            with open(f"{assembly_hap1_dir}/data/fasta.fofn", 'a') as fasta_fofn:
                for fasta_file in glob.glob(f"{pacbio_dir}/fasta/*fasta.gz"):
                    fasta_fofn.write(f"{fasta_file}\n")

            # Create cram.fofn
            with open(f"{assembly_hap1_dir}/data/cram.fofn", 'a') as cram_fofn:
                for cram_file in glob.glob(f"{hic_read_dir}/*.cram"):
                    cram_fofn.write(f"{cram_file}\n")
                        
            if combine_for_curation:
                os.mkdir(assembly_merged_dir)
                os.mkdir(f"{assembly_merged_dir}/data")
                # Copy assembly and merge with haplotigs for merge.fa
                with open(f"{assembly_merged_dir}/data/hap1.fa", 'wb') as h1_out:
                    with gzip.open(decon_hap1_path,'rb') as h1_in:
                        shutil.copyfileobj(h1_in, h1_out)
                    # If combine for curation, copy hap and combine the files for ref.fa
                with open(f"{assembly_merged_dir}/data/hap2.fa", 'wb') as h2_out:
                    with gzip.open(decon_hap2_path,'rb') as h2_in:
                        shutil.copyfileobj(h2_in, h2_out)

                combine_fasta(f"{assembly_merged_dir}/data/hap1.fa", f"{assembly_merged_dir}/data/hap2.fa", f"{assembly_merged_dir}/data/ref.fa",)

                # Create fasta.fofn
                with open(f"{assembly_merged_dir}/data/fasta.fofn", 'a') as fasta_fofn:
                    for fasta_file in glob.glob(f"{pacbio_dir}/fasta/*fasta.gz"):
                        fasta_fofn.write(f"{fasta_file}\n")

                # Create cram.fofn
                with open(f"{assembly_merged_dir}/data/cram.fofn", 'a') as cram_fofn:
                    for cram_file in glob.glob(f"{hic_read_dir}/*.cram"):
                        cram_fofn.write(f"{cram_file}\n")

            successes[tolid_hap1] = f"{assembly_hap1_dir}"
            if combine_for_curation:
                successes[tolid_merged] = f"{assembly_merged_dir}"
        else:
            fail_summary[species_id] = fails

    for species_id,fails in fail_summary.items():
        print(species_id)
        for fail in fails: 
            print(f"    {fail}")

    print("")
    print("Success")
    for species_id in successes.keys(): 
        print(f"{species_id}")
    # print("")
    # print("TELOMERE SCRIPT")
    # print("")
    # print("source activate curation_v2")
    # print("unset PYTHONPATH")
    for species_id,path in successes.items(): 
        launch_telo_finder(species_id, path)
        # print(f"cd {path}/data")
        # print(f"echo 'python ~alt/python/bin/telo_finder.py ref.fa'|bsub -J telo_{species_id} -q normal -o d.o -e d.e -n 1 -M40000 -R'select[mem>40000] rusage[mem=40000] span[hosts=1]'")

if __name__ == "__main__":
    main()

