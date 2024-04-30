#!/usr/bin/env python

from ToLJiraAuth import ToLJiraAuth
import JiraMethods as jm
import os
import glob
import shutil
import subprocess
import json
import requests
import argparse

higlass_digest_path = "/lustre/scratch123/tol/share/grit-higlass/data_to_load"
local_s3_config = "/nfs/users/nfs_w/we3/.s3cfg"
pretext_snapshot_directory = "/lustre/scratch123/tol/resources/treeval/treeval_pretext_snapshots"
kmer_spectra_directory = "/lustre/scratch123/tol/resources/treeval/treeval_kmer_spectra"
jira_path = "jira.sanger.ac.uk"

def check_pretext_exists_in_s3(tolid_assem):
    exists = run_command(f's3cmd -c {local_s3_config} ls s3://treeval/pretextsnapshot_{tolid_assem}.png | wc -l')
    # print(f"|{str(exists)}|")
    if str(exists).strip() == "1":
        return True
    else:
        return False

def upload_pretext_to_s3(tolid_assem):
    return run_command(f's3cmd -c {local_s3_config} --quiet --acl-public put {pretext_snapshot_directory}/{tolid_assem}_normalFullMap.png s3://treeval/pretextsnapshot_{tolid_assem}.png')

def check_kmer_exists_in_s3(tolid_assem):
    exists = run_command(f's3cmd -c {local_s3_config} ls s3://treeval/kmerspectra_{tolid_assem}.png | wc -l')
    # print(f"|{str(exists)}|")
    if str(exists).strip() == "1":
        return True
    else:
        return False

def upload_kmer_to_s3(tolid_assem):
    return run_command(f's3cmd -c {local_s3_config} --quiet --acl-public put {kmer_spectra_directory}/{tolid_assem}.ref.spectra-cn.ln.png s3://treeval/kmerspectra_{tolid_assem}.png')

def launch_post(tolid, treeval_path):
    return run_command(f'bash tv_post.sh -t {tolid} -p {treeval_path}')


def run_command(cmd):

    process = subprocess.Popen(cmd,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE,
                            text = True,
                            shell = True
            )
    std_out, std_err = process.communicate()
    return std_out

def copy_file(input_path, output_path):
    with open(input_path,'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)               

def build_post_yaml(tolid, tv_path, mode):

    if mode == "internal":
        higlass_url = "http://grit-internal-higlass.tol.sanger.ac.uk"
        higlass_kubeconfig = f"{tv_path}/post/config.tol-it-prod-k8s"
        higlass_upload_directory = "/lustre/scratch123/tol/share/grit-internal-higlass/data_to_load/"
    elif mode == "dev":
        higlass_url = "http://grit-higlass.tol-dev.sanger.ac.uk"
        higlass_kubeconfig = "~/.kube/config.tol-it-dev-k8s"
        higlass_upload_directory = "/lustre/scratch123/tol/share/grit-higlass/data_to_load/"
    else:
        higlass_url = "https://grit-higlass.tol.sanger.ac.uk/"
        higlass_kubeconfig = f"{tv_path}/post/config.tol-it-prod-k8s"
        higlass_upload_directory = "/lustre/scratch123/tol/share/grit-higlass/data_to_load/"

    # Create input yaml
    post_yaml_contents = f'''sample:
  tolid: {tolid}
  directory: {tv_path}
higlass:
  higlass_url: {higlass_url}
  higlass_deployment_name: higlass-app-grit
  higlass_namespace: tol-higlass-grit
  higlass_kubeconfig: {higlass_kubeconfig}
  higlass_upload_directory: {higlass_upload_directory}'''

    print(f"{tolid} - Saving higlass .yaml...") 

    # Create fasta.fofn
    with open(f"{tv_path}/post/{tolid}_post.yaml", 'w') as input_yaml:
        input_yaml.write(post_yaml_contents)


def ingest_completed_sample(sample_path, mode):

    try:
        sample_name = os.path.basename(sample_path)

        # Save images to resources directory
        print(f"{sample_name} - Saving images to resources...") 
        copy_file(f"{sample_path}/tv_output/hic_files/{sample_name}_normalFullMap.png", f"/lustre/scratch123/tol/resources/treeval/treeval_pretext_snapshots/{sample_name}_normalFullMap.png")
        if glob.glob(f"{sample_path}/tv_output/hic_files/{sample_name}.ref.spectra-cn.ln.png"):
            copy_file(f"{sample_path}/tv_output/hic_files/{sample_name}.ref.spectra-cn.ln.png", f"/lustre/scratch123/tol/resources/treeval/treeval_kmer_spectra/{sample_name}.ref.spectra-cn.ln.png")
        
        # Save stats to resources directory
        print(f"{sample_name} - Saving stats to resources...") 
        for summary_file in glob.glob(f"{sample_path}/tv_output/pipeline_info/TreeVal_run_*"):
            copy_file(summary_file, f"/lustre/scratch123/tol/resources/treeval/treeval_stats/1_1_0/{os.path.basename(summary_file)}")

        # Saving CO2 summary
        print(f"{sample_name} - Saving co2 trace to resources...") 
        for co2_file in glob.glob(f"{sample_path}/work/co2footprint_trace_*"):
            copy_file(co2_file, f"/lustre/scratch123/tol/resources/treeval/treeval_stats/1_1_0/co2footprint_{sample_name}.txt")

        print(f"{sample_name} - Copying pretext maps...") 
        copy_file(f"{sample_path}/tv_output/hic_files/{sample_name}_normal.pretext", f"/nfs/treeoflife-01/teams/grit/data/pretext_maps/{sample_name}_normal.pretext")
        copy_file(f"{sample_path}/tv_output/hic_files/{sample_name}_hr.pretext", f"/nfs/treeoflife-01/teams/grit/data/pretext_maps/{sample_name}_hr.pretext")
        copy_file(f"/nfs/treeoflife-01/teams/grit/data/pretext_maps/{sample_name}_hr.pretext", f"/nfs/treeoflife-01/teams/tola/users/we3/check_pretext/{sample_name}_hr.pretext")

        # Prepare higlass ingestion
        print(f"{sample_name} - Preparing for higlass ingestion...") 

        if not os.path.isdir(f"{sample_path}/post"):
            os.mkdir(f"{sample_path}/post")

        build_post_yaml(sample_name, sample_path, mode)
        
        copy_file(f"/nfs/users/nfs_w/we3/.kube/config.tol-it-prod-k8s", f"{sample_path}/post/config.tol-it-prod-k8s")
        
        print(f"{sample_name} - Launch higlass ingestion...")
        launch_post(sample_name, sample_path)


        # sample = sample_name.split("_")[0]

        # os.mkdir(f"{higlass_digest_path}/{sample_name}")
        # print("Copying telo bed/bedgraph...")
        # copy_file(f"{sample_path}/tv_output/hic_files/{sample_name}_telomere.bed", f"{higlass_digest_path}/{sample_name}/{sample_name}_telomere.bed")
        # copy_file(f"{sample_path}/tv_output/hic_files/{sample_name}_telomere.bedgraph", f"{higlass_digest_path}/{sample_name}/{sample_name}_telomere.bedgraph")
        # print("Copying repeat density bigwig...")
        # copy_file(f"{sample_path}/tv_output/hic_files/{sample_name}_repeat_density.bigWig", f"{higlass_digest_path}/{sample_name}/{sample_name}_repeat_density.bw")

        # print("Copying .genome...")
        # if glob.glob(f"{sample_path}/tv_output/treeval_upload/{sample_name}_len_sorted.genome"):
        #     copy_file(f"{sample_path}/tv_output/treeval_upload/{sample_name}_len_sorted.genome", f"{higlass_digest_path}/{sample_name}/{sample_name}.genome")
        # elif glob.glob(f"{sample_path}/tv_output/treeval_upload/{sample_name}.unsorted.genome"):
        #     copy_file(f"{sample_path}/tv_output/treeval_upload/{sample_name}.unsorted.genome", f"{higlass_digest_path}/{sample_name}/{sample_name}.genome")
        
        # print("Copying mcool...")
        # copy_file(f"{sample_path}/tv_output/hic_files/{sample_name}.mcool", f"{higlass_digest_path}/{sample_name}/{sample_name}.mcool")
        # print("Copying gap bed/bedgraph...")
        # copy_file(f"{sample_path}/tv_output/hic_files/{sample_name}_gap.bed", f"{higlass_digest_path}/{sample_name}/{sample_name}_gap.bed")
        # copy_file(f"{sample_path}/tv_output/hic_files/{sample_name}_gap.bedgraph", f"{higlass_digest_path}/{sample_name}/{sample_name}_gap.bedgraph")
        # print("Copying coverage bigwig...")
        # copy_file(f"{sample_path}/tv_output/hic_files/{sample_name}_coverage_normal.bigWig", f"{higlass_digest_path}/{sample_name}/{sample_name}_coverage.bw")
        # print("Copying average coverage bigwig...")

        # if glob.glob(f"{sample_path}/tv_output/hic_files/{sample_name}_coverage_avg.bigWig"):
        #     copy_file(f"{sample_path}/tv_output/hic_files/{sample_name}_coverage_avg.bigWig", f"{higlass_digest_path}/{sample_name}/{sample_name}_coverage_avg.bw")
        # elif glob.glob(f"{sample_path}/tv_output/hic_files/{sample}_coverage_avg.bigWig"):
        #     copy_file(f"{sample_path}/tv_output/hic_files/{sample}_coverage_avg.bigWig", f"{higlass_digest_path}/{sample_name}/{sample_name}_coverage_avg.bw")
        

        return True
    except:
        return False

def get_jbrowse_run_details(run_path, jbrowse_directory):

    jb_run_name = run_path.split("/")[-1]
                        
    if not os.path.isfile(f"{jbrowse_directory}/{jb_run_name}.fa.fai"):
        jb_scaffold_name = "SCAFFOLD_1"
    else:
        with open(f"{jbrowse_directory}/{jb_run_name}.fa.fai") as fai:
            jb_scaffold_name = fai.readline().split("\t")[0]

    return jb_run_name, jb_scaffold_name

def get_taxonid_from_tolid(tolid):

    response = requests.get(
        url = f"https://id.tol.sanger.ac.uk/api/v2/tol-ids/{tolid}",
        headers={'Accept': 'application/json'},
    )

    if (response.status_code == 200):

        if response.json():
            data = response.json()[0]
            species_data = data['species']

            return species_data['taxonomyId']
        else:
            print(f"Unable to load taxon id for {tolid}")
            return None
    else:
        return response.json()


def get_btk_links(species_id):

    btk_directory = "/lustre/scratch123/tol/share/grit-btk-prod/blobplots"

    btk_plots = glob.glob(f"{btk_directory}/{species_id}*.fa.ascc")

    btk_pri_plot = ""
    btk_hap_plot = ""
    btk_mit_plot = ""
    for btk_plot in btk_plots:

        btk_plot_name = btk_plot.split("/")[-1].replace('.fa.ascc','')

        if btk_plot_name.endswith("-MT"):
            btk_mit_plot = btk_plot_name

        elif btk_plot_name.endswith(".haplotigs"):
            btk_hap_plot = btk_plot_name

        else:
            btk_pri_plot = btk_plot_name

    return btk_pri_plot, btk_hap_plot, btk_mit_plot

def get_jbrowse_links(issue, tolid, species_id):
    jbrowse_prod_directory = "/lustre/scratch123/tol/share/jbrowse/prod/data"
    jbrowse_dev_directory = "/lustre/scratch123/tol/share/jbrowse/dev/data"

    run_name = ""
    scaffold_name = ""
    jb_server = ""

    # If specific tolid known, otherwise check for existing (the old method)
    if tolid:
        # Check if exists in dev
        jbrowse_dev_runs = glob.glob(f"{jbrowse_dev_directory}/{species_id}*")
        if os.path.isdir(f"{jbrowse_dev_directory}/{tolid}"):
            run_name, scaffold_name = get_jbrowse_run_details(tolid, jbrowse_dev_directory)
            jb_server = "dev"

        # Check if exists in pro
        if os.path.isdir(f"{jbrowse_prod_directory}/{tolid}"):
            run_name, scaffold_name = get_jbrowse_run_details(tolid, jbrowse_prod_directory)
            jb_server = "prod"

    else:
        # Check dev
        jbrowse_dev_runs = glob.glob(f"{jbrowse_dev_directory}/{species_id}*")

        if len(jbrowse_dev_runs) > 1:
            for run in jbrowse_dev_runs:
                if "(hap1)" in issue.fields.summary and run.split("/")[-1].endswith("_1"):
                    run_name, scaffold_name = get_jbrowse_run_details(run, jbrowse_dev_directory)
                    jb_server = "dev"

                if "(hap2)" in issue.fields.summary and run.split("/")[-1].endswith("_2"):
                    run_name, scaffold_name = get_jbrowse_run_details(run, jbrowse_dev_directory)
                    jb_server = "dev"
            
                if issue.fields.customfield_12200 == run.split("/")[-1]:
                    run_name, scaffold_name = get_jbrowse_run_details(run, jbrowse_prod_directory)
                    jb_server = "dev"

        elif len(jbrowse_dev_runs) == 1:
            run_name, scaffold_name = get_jbrowse_run_details(jbrowse_dev_runs[0], jbrowse_dev_directory)
            jb_server = "dev"
            

        # Check prod
        jbrowse_prod_runs = glob.glob(f"{jbrowse_prod_directory}/{species_id}*")

        if len(jbrowse_prod_runs) > 1:
            for run in jbrowse_prod_runs:
                if "(hap1)" in issue.fields.summary and run.split("/")[-1].endswith("_1"):
                    run_name, scaffold_name = get_jbrowse_run_details(run, jbrowse_prod_directory)
                    jb_server = "prod"

                if "(hap2)" in issue.fields.summary and run.split("/")[-1].endswith("_2"):
                    run_name, scaffold_name = get_jbrowse_run_details(run, jbrowse_prod_directory)
                    jb_server = "prod"

                if issue.fields.customfield_12200 == run.split("/")[-1]:
                    run_name, scaffold_name = get_jbrowse_run_details(run, jbrowse_prod_directory)
                    jb_server = "prod"

        elif len(jbrowse_prod_runs) == 1:
            run_name, scaffold_name = get_jbrowse_run_details(jbrowse_prod_runs[0], jbrowse_prod_directory)
            jb_server = "prod"

    return run_name, jb_server, scaffold_name

def add_pretext_snapshot(tolid_assem):

    hic_plot_exists = "N"
    # Check if exists in directory
    if glob.glob(f"{pretext_snapshot_directory}/{tolid_assem}_normalFullMap.png"):
        # Check if exists in s3
        if check_pretext_exists_in_s3(tolid_assem):
            hic_plot_exists = "Y"
        else:
            hic_plot_exists = "N"
            # If available on lustre, upload to s3
            upload_pretext_to_s3(tolid_assem)

            # If check again after upload
            if check_pretext_exists_in_s3(tolid_assem):
                hic_plot_exists = "Y"
            else:
                hic_plot_exists = "N"

    # Add kmer plot
    kmer_plot_exists = "N"

    # Check if exists in directory
    if glob.glob(f"{kmer_spectra_directory}/{tolid_assem}.ref.spectra-cn.ln.png"):
        # Check if exists in s3
        if check_kmer_exists_in_s3(tolid_assem):
            kmer_plot_exists = "Y"
        else:
            kmer_plot_exists = "N"
            # If available on lustre, upload to s3
            upload_kmer_to_s3(tolid_assem)

            # If check again after upload
            if check_kmer_exists_in_s3(tolid_assem):
                kmer_plot_exists = "Y"
            else:
                kmer_plot_exists = "N"
    
    return hic_plot_exists, kmer_plot_exists

def build_treeval_details(issue):       

    values_dict = {}
    existing_treeval_data_dict = {}

    species_id = issue.fields.customfield_11627
    # tolid_assem = issue.fields.customfield_11643
    existing_treeval_data_string = issue.fields.customfield_12800

    if existing_treeval_data_string:
        try:
            existing_treeval_data_dict = json.loads(existing_treeval_data_string)
        except ValueError as e:
            existing_treeval_data_dict = {}

    ##  Ticket values 
    # Add 'Added to curation date'
    values_dict["start"] = jm.get_added_to_curation_date_from_issue(issue)

    # Add BTK links
    btk_pri_plot, btk_hap_plot, btk_mit_plot = get_btk_links(species_id)
    values_dict["btk_pr"] = btk_pri_plot      
    values_dict["btk_hp"] = btk_hap_plot 

    # Add GoaT link
    taxon_response = get_taxonid_from_tolid(species_id)

    if isinstance(taxon_response, int):
        values_dict["taxon_id"] = taxon_response

    ## Assembly values
    hap1_id, hap2_id, merged_id = jm.get_treeval_run_ids(issue)

    # Add jbrowse links.
    values_dict["jbrowse"], values_dict["jb_server"], values_dict["jb_scaffold"] = get_jbrowse_links(issue, hap1_id, species_id)
    values_dict["jbrowse_hap2"], values_dict["jb_server_hap2"], values_dict["jb_scaffold_hap2"] = get_jbrowse_links(issue, hap2_id, species_id)
    values_dict["jbrowse_merged"], values_dict["jb_server_merged"], values_dict["jb_scaffold_merged"] = get_jbrowse_links(issue, merged_id, species_id)
    
    # Add higlass
    if existing_treeval_data_dict.get("higlass"):
        values_dict["higlass"] = existing_treeval_data_dict["higlass"]
    else:
        values_dict["higlass"] = ""

    # Add pretext snapshot
    values_dict["hic_plot"], values_dict["kmer_plot"] = add_pretext_snapshot(hap1_id)
    values_dict["hic_plot_hap2"], values_dict["kmer_plot_hap2"] = add_pretext_snapshot(hap2_id)
    values_dict["hic_plot_merged"], values_dict["kmer_plot_merged"] = add_pretext_snapshot(merged_id)

    # Build updated output string to compare with existing.
    out_string = json.dumps(values_dict)

    for key in values_dict.keys():
        if existing_treeval_data_dict.get(key) == None:
            print(f"Missing field: {key}")
            
            update_issue = True
            break

        if values_dict[key] != existing_treeval_data_dict[key]:
            print(f"Differing value for {key}. Jira: {existing_treeval_data_dict[key]}. Local: {values_dict[key]}")
            update_issue = True
            break

    if update_issue:
        print(f"To Update - {species_id}")

        issue.update(fields={'customfield_12800': out_string})



# def advance_to_curation():


    # 

    # Images to be submitted to s3


    # Stats saved to resources (prob needs to change)


    # Higlass ingestion prepared and launched. 


    # Jira ticket updated - if all assemblies from ticket are available.


def parse_args(args=None):
    Description = "."
    Epilog = ">"

    parser = argparse.ArgumentParser(description=Description, epilog=Epilog)
    parser.add_argument("TOLID", nargs='?', default="", help="TOLID.")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    return parser.parse_args(args)


def main(args=None):

    args = parse_args(args)



    tja = ToLJiraAuth()
    # jql_request = f"project = RC AND status = 'HiC Building' AND assignee = 'Will Eagles' AND 'Telomere motif k-mer length' is EMPTY AND 'Sample ID' ~ ilAgrLych1 ORDER BY priority DESC, updated DESC"
    # jql_request = f"status in ('HiC Building', 'geval analysis', 'curation') AND assignee = 'Will Eagles' AND 'Telomere motif k-mer length' is not EMPTY AND 'HiGlass entry' is EMPTY ORDER BY priority DESC, updated DESC"
    
    if not args.TOLID:
        jql_request = f"status in ('HiC Building', 'geval analysis', 'curation') AND assignee = 'Will Eagles' AND 'Telomere motif k-mer length' is not EMPTY ORDER BY priority DESC, updated DESC"
    else:
        jql_request = f"status in ('HiC Building', 'geval analysis', 'curation') AND assignee = 'Will Eagles' AND 'Telomere motif k-mer length' is not EMPTY AND 'Sample ID' ~ {args.TOLID} ORDER BY priority DESC, updated DESC"
        
    # jql_request = f"project = RC AND status = 'HiC Building' AND 'Sample ID' ~ 'txAmpSpea1*'"

    results = tja.auth_jira.search_issues(jql_request,maxResults=0, expand='changelog')

    # Return most recently created entry if there are multiple with same name.
    samples_ready = []
    samples_succeeded = []
    samples_failed = []

    for result in results:
        issue = tja.auth_jira.issue(result)

        species_id = jm.get_species_id(issue)
        # if species_id == "idCulPerx1":
        #     continue

        treeval_run_path = os.path.dirname(os.path.dirname(jm.get_hap1_path(issue)))

        hap1_id, hap2_id, merged_id = jm.get_treeval_run_ids(issue)

        if ' external assembly' in issue.fields.summary:
            mode = "internal"
        else:
            mode = "prod"

        # Add to dictionary of (tolid, path to working directory)
        if glob.glob(f"{treeval_run_path}/treeval/{hap1_id}/tv_output/pipeline_info/TreeVal_run_*"):
            if not os.path.isdir(f"{higlass_digest_path}/{hap1_id}"):
                samples_ready.append((hap1_id, f"{treeval_run_path}/treeval/{hap1_id}", mode))

        if glob.glob(f"{treeval_run_path}/treeval/{hap2_id}/tv_output/pipeline_info/TreeVal_run_*"):
            if not os.path.isdir(f"{higlass_digest_path}/{hap2_id}"):
                samples_ready.append((hap2_id, f"{treeval_run_path}/treeval/{hap2_id}", mode))

        if glob.glob(f"{treeval_run_path}/treeval/{merged_id}/tv_output/pipeline_info/TreeVal_run_*"):
            if not os.path.isdir(f"{higlass_digest_path}/{merged_id}"):        
                samples_ready.append((merged_id, f"{treeval_run_path}/treeval/{merged_id}", mode))

        if not hap1_id:
            tv_id = jm.get_treeval_run_id(issue)
            if glob.glob(f"{treeval_run_path}/treeval/{tv_id}/tv_output/pipeline_info/TreeVal_run_*"):
                if not os.path.isdir(f"{higlass_digest_path}/{tv_id}"):
                    samples_ready.append((tv_id, f"{treeval_run_path}/treeval/{tv_id}", mode))

    samples_ready.append(("idCulPerx1_2", f"/lustre/scratch124/tol/projects/erga-bge/data/insects/Culex_perexiguus/assembly/draft/treeval/idCulPerx1_2", "prod"))

    for sample in samples_ready:
        print(sample[0])

    val = input(f"Continue?\n")

    if val == "y":
        for sample in samples_ready:
            result = ingest_completed_sample(sample[1], sample[2])
            if result:
                samples_succeeded.append(sample[0])
            else:
                samples_failed.append(sample[0])

        print("Succeeded:")
        for sample in samples_succeeded:
            print(sample)
        print("")
        print("Failed:")
        for sample in samples_failed:
            print(sample)


if __name__ == "__main__":
    main()