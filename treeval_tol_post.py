#!/usr/bin/env python

from ToLJiraAuth import ToLJiraAuth
import JiraMethods as jm
import os
import glob
import shutil
import subprocess
import argparse

repo_path="/nfs/treeoflife-01/teams/tola/users/we3/source/higlass_digest"
higlass_digest_path = "/lustre/scratch123/tol/share/grit-higlass/data_to_load"

def launch_post(tolid, treeval_path):
    return run_command(f'./tv_post.sh -t {tolid} -p {treeval_path}')

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

        if not os.path.isdir(f"{sample_path}/post/working"):
            os.mkdir(f"{sample_path}/post/working")

        build_post_yaml(sample_name, sample_path, mode)
        
        copy_file(f"/nfs/users/nfs_w/we3/.kube/config.tol-it-prod-k8s", f"{sample_path}/post/config.tol-it-prod-k8s")
        
        print(f"{sample_name} - Launch higlass ingestion...")
        # launch_post(sample_name, sample_path)

        return True
    except:
        return False

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
    if not args.TOLID:
        jql_request = f"status in ('HiC Building', 'geval analysis', 'curation') AND assignee = 'Will Eagles' AND 'Telomere motif k-mer length' is not EMPTY ORDER BY priority DESC, updated DESC"
    else:
        jql_request = f"status in ('HiC Building', 'geval analysis', 'curation') AND assignee = 'Will Eagles' AND 'Telomere motif k-mer length' is not EMPTY AND 'Sample ID' ~ {args.TOLID} ORDER BY priority DESC, updated DESC"
        
    results = tja.auth_jira.search_issues(jql_request,maxResults=0, expand='changelog')

    # Return most recently created entry if there are multiple with same name.
    samples_ready = []
    samples_succeeded = []
    samples_failed = []

    for result in results:
        issue = tja.auth_jira.issue(result)

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

    # samples_ready.append(("ilPolAtla1_7", "/lustre/scratch124/tol/projects/tol/data/insects/Polyommatus_atlantica/assembly/draft/treeval/ilPolAtla1_7", "prod"))

    for sample in samples_ready:
        print(sample[0])

    val = input(f"Continue?\n")

    if val == "y":
        for sample in samples_ready:
            result = ingest_completed_sample(sample[1], sample[2])
            if result:
                samples_succeeded.append((sample[0], sample[1]))
            else:
                samples_failed.append(sample[0])

        print("Succeeded:")      
        for sample in samples_succeeded:
            print(sample[0])

        print("")
        print("Failed:")
        for sample in samples_failed:
            print(sample[0])

        print("To launch Higlass:")
        print("")
        # print("unset PYTHONPATH")
        # print("export MODULEPATH=$MODULEPATH:/software/treeoflife/custom-installs/modules")
        # print("module load nextflow/23.10.0-5889")
        # print("export MODULEPATH=$MODULEPATH:/software/modules/")
        # print("module load ISG/singularity")


        print("module load ISG/singularity/3.11.4")
        print("module load conda")
        print("conda activate nf-core_2.11")

        for sample in samples_succeeded:
            print(f"bsub -e nf_run_p.e -o nf_run_p.o -n 2 -q normal -M1000 -R'select[mem>1000] rusage[mem=1000] span[hosts=1]' 'nextflow run {repo_path}/main.nf -profile sanger,singularity --input {sample[1]}/post/{sample[0]}_post.yaml --outdir {sample[1]}/post/hg_link'")


if __name__ == "__main__":
    main()