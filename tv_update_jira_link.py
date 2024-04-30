#!/usr/bin/env python
from ToLJiraAuth import ToLJiraAuth
import JiraMethods as jm
import glob
import os
import json
import requests
import subprocess

jbrowse_prod_directory = "/lustre/scratch123/tol/share/jbrowse/prod/data"
jbrowse_dev_directory = "/lustre/scratch123/tol/share/jbrowse/dev/data"
btk_directory = "/lustre/scratch123/tol/share/grit-btk-prod/blobplots"
pretext_snapshot_directory = "/lustre/scratch123/tol/resources/treeval/treeval_pretext_snapshots"
kmer_spectra_directory = "/lustre/scratch123/tol/resources/treeval/treeval_kmer_spectra"
jira_path = "jira.sanger.ac.uk"

local_s3_config = "/nfs/users/nfs_w/we3/.s3cfg"

# s3cmd -c /nfs/users/nfs_w/we3/.s3cfg --quiet --acl-public put /lustre/scratch123/tol/resources/treeval/treeval_kmer_spectra/gfInoCfpo1_1.ref.spectra-cn.ln.png s3://treeval/kmerspectra_gfInoCfpo1_1.png
# s3cmd -c /nfs/users/nfs_w/we3/.s3cfg --quiet --acl-public put /lustre/scratch123/tol/resources/treeval/treeval_pretext_snapshots/gfInoCfpo1_1_normalFullMap.png s3://treeval/pretextsnapshot_gfInoCfpo1_1.png
# s3cmd -c /nfs/users/nfs_w/we3/.s3cfg --quiet --acl-public put /lustre/scratch123/tol/resources/treeval/treeval_pretext_snapshots/drCraLaev2_1_normalFullMap.png s3://treeval/pretextsnapshot_drCraLaev2_1.png
# s3cmd -c /nfs/users/nfs_w/we3/.s3cfg --quiet --acl-public put /lustre/scratch123/tol/resources/treeval/treeval_kmer_spectra/ilAgrLych1_1.ref.spectra-cn.ln.png s3://treeval/kmerspectra_ilAgrLych1_1.png
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

def run_command(cmd):

    process = subprocess.Popen(cmd,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE,
                            text = True,
                            shell = True
            )
    std_out, std_err = process.communicate()
    return std_out

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

def main():
    # print(get_all_from_jira(5, 2, f'[]', 'jira_issue',""))
    # curation_dates = get_curation_dates()
# AND (Treeval is EMPTY OR Treeval ~ NA)
    tja = ToLJiraAuth()
    # jql_request = f"project in (GRIT,RC) AND status = Curation AND (Treeval is EMPTY OR Treeval ~ NA)"
    jql_request = f"project in (GRIT,RC) AND status = Curation"
    results = tja.auth_jira.search_issues(jql_request,maxResults=0, expand='changelog')



    for result in results:
        update_issue = False
        
        issue = tja.auth_jira.issue(result)

        values_dict = {}
        existing_treeval_data_dict = {}

        species_id = issue.fields.customfield_11627
        # print(species_id)
        # if species_id == "idCulPerx1":
        #     continue

        tolid_assem = issue.fields.customfield_11643

        treeval_run_path = os.path.dirname(os.path.dirname(jm.get_hap1_path(issue)))

        # existing_treeval_data_string = issue.fields.customfield_12800
        existing_treeval_data_string = issue.fields.customfield_12800

        if existing_treeval_data_string:
            try:
                existing_treeval_data_dict = json.loads(existing_treeval_data_string)
            except ValueError as e:
                existing_treeval_data_dict = {}

        # Add jbrowse link
        run_name = ""
        scaffold_name = ""
        jb_server = ""

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

        values_dict["jbrowse"] = run_name
        values_dict["jb_server"] = jb_server
        values_dict["jb_scaffold"] = scaffold_name

        # Add 'Added to curation date'
        created_dates = []
        is_into_curation = False
        for cl_entry in issue.changelog.histories:
            is_into_curation = False
            for cl_item in cl_entry.items:
                if cl_item.field == "status" and cl_item.toString in ("curation", "Curation"):
                    is_into_curation = True

            if is_into_curation:
                created_dates.append(cl_entry.created)

        if len(created_dates) > 1:
            curation_date = min(created_dates)
        else:
            curation_date = created_dates[0]

        values_dict["start"] = curation_date

        # Add BTK links
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

        values_dict["btk_pr"] = btk_pri_plot      
        values_dict["btk_hp"] = btk_hap_plot 

        # Add higlass
        if existing_treeval_data_dict.get("higlass"):
            values_dict["higlass"] = existing_treeval_data_dict["higlass"]
        else:
            if glob.glob(f"{treeval_run_path}/treeval/{tolid_assem}/post/{tolid_assem}_post.yaml"):
                values_dict["higlass"] = tolid_assem
            else:
                values_dict["higlass"] = ""

        # Add pretext snapshot
        values_dict["hic_plot"] = "N"
        # Check if exists in directory
        if glob.glob(f"{pretext_snapshot_directory}/{tolid_assem}_normalFullMap.png"):
            # Check if exists in s3
            if check_pretext_exists_in_s3(tolid_assem):
                values_dict["hic_plot"] = "Y"
            else:
                values_dict["hic_plot"] = "N"
                # If available on lustre, upload to s3
                upload_pretext_to_s3(tolid_assem)

                # If check again after upload
                if check_pretext_exists_in_s3(tolid_assem):
                    values_dict["hic_plot"] = "Y"
                else:
                    values_dict["hic_plot"] = "N"

        # Add kmer plot
        values_dict["kmer_plot"] = "N"

        # Check if exists in directory
        if glob.glob(f"{kmer_spectra_directory}/{tolid_assem}.ref.spectra-cn.ln.png"):
            # Check if exists in s3
            if check_kmer_exists_in_s3(tolid_assem):
                values_dict["kmer_plot"] = "Y"
            else:
                values_dict["kmer_plot"] = "N"
                # If available on lustre, upload to s3
                upload_kmer_to_s3(tolid_assem)

                # If check again after upload
                if check_kmer_exists_in_s3(tolid_assem):
                    values_dict["kmer_plot"] = "Y"
                else:
                    values_dict["kmer_plot"] = "N"

        # Add GoaT link
        taxon_response = get_taxonid_from_tolid(species_id)

        if isinstance(taxon_response, int):
            values_dict["taxon_id"] = taxon_response

        # print("======================================")
        existing_treeval_data_string
        out_string = json.dumps(values_dict)

        # if len(out_string) > 255:
        #     excess = len(out_string) - 255
        #     print(f"{species_id} output is {excess} characters too long")

        # print("Current:")
        # print(existing_treeval_data_string)
        # print("New:")
        # print(out_string)
        # print("")
        # print("Current keys:")
        # print(existing_treeval_data_dict.keys())
        # print("New keys:")
        # print(values_dict.keys())
        # print("")
        # Check if existing data different, if so update.
        for key in values_dict.keys():
            if existing_treeval_data_dict.get(key) == None:
                print(f"Missing field: {key}")
                
                update_issue = True
                break

            if values_dict[key] != existing_treeval_data_dict[key]:
                print(f"Differing value for {key}. Jira: {existing_treeval_data_dict[key]}. Local: {values_dict[key]}")
                update_issue = True
                break

        # Update issue with data
        # customfield_12200 - Treeval
        # customfield_12800 - Treeval data
        if update_issue:
            print(f"To Update - {species_id}")

            issue.update(fields={'customfield_12800': out_string})
        # print("======================================")

if __name__ == "__main__":
    main()