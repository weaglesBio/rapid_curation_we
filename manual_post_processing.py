#!/usr/bin/env python

from methods.ToLTreevalJira import ToLTreevalJira
from methods.ToLHiGlass import ToLHiGlass
from methods.ToLKubeHiGlass import ToLKubeHiGlass
from methods.ToLTreevalFiles import ToLTreevalFiles
from methods.ToLS3 import ToLS3
from methods.ToLApi import ToLApi
from methods.ToLTreevalData import ToLTreevalData
import argparse


def parse_args(args=None):
    Description = "."
    Epilog = ">"

    parser = argparse.ArgumentParser(description=Description, epilog=Epilog)

    parser.add_argument('--ticket', metavar='ticket', type=str, required=True, help='ticket number')
    parser.add_argument('--environment_yaml', metavar='environment_yaml', nargs='?', default="environment_params.yaml", help=".")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    return parser.parse_args(args)

def main(args=None):

    args = parse_args(args)

    path = "/lustre/scratch124/tol/projects/tol/data/insects/Polyommatus_atlantica/assembly/draft/treeval/ilPolAtla1_8"
    tolid = "ilPolAtla1_8"
    ticket = "RC-1498"


    treeval_data = ToLTreevalData()

    # Load environment params file.
    env_params = treeval_data.load_environment_params(args.environment_yaml)

    # Load objects
    jira = ToLTreevalJira(env_params["jira_path"], env_params["jira_token"])
    s3 = ToLS3(env_params["local_s3_config"], env_params["pretext_snapshot_dir"], env_params["kmer_spectra_dir"])
    kube_higlass = ToLKubeHiGlass(env_params["higlass_kubeconfig"], env_params["higlass_namespace"], env_params["higlass_deployment_name"])

    

    # Load issue from jira from ticket.
    tv_issue = jira.get_issue_from_ticket_id(args.ticket)

    # Load object dependent on internal mode.
    farm_dir = ToLTreevalFiles((env_params["higlass_internal_upload_dir"] if tv_issue.is_internal else env_params["higlass_upload_dir"]), 
                                env_params["stats_dir"], 
                                env_params["pretext_snapshot_dir"], 
                                env_params["kmer_spectra_dir"], 
                                env_params["jbrowse_dev_dir"],
                                env_params["jbrowse_prod_dir"],
                                env_params["btk_dir"], 
                                env_params["pretext_maps_dir"])

    higlass = ToLHiGlass((env_params["higlass_internal_url"] if tv_issue.is_internal else env_params["higlass_url"]), (env_params["higlass_internal_upload_dir"] if tv_issue.is_internal else env_params["higlass_upload_dir"]))

    ###
    ### Check for assemblies requiring treeval post-processing.
    ###
    tv_assemblies_to_progress = []


    if farm_dir.check_treeval_completed(path):
        tv_assemblies_to_progress.append((tolid, path))

    ###
    ### Run Post-Processing
    ###
    postprocessing_succeeded = []
    postprocessing_failed = []

    for tv_assembly in tv_assemblies_to_progress:

        print(f"{tv_assembly[0]} - Running higlass digest...")
        result, status = farm_dir.copy_files_from_treeval_output(tv_assembly[0], tv_assembly[1])

        if result:
            s3.upload_pretext_to_s3(tv_assembly[0])
            s3.upload_kmer_to_s3(tv_assembly[0])

            # Run higlass digest
            print(f"{tv_assembly[0]} - Running higlass digest...")
            kube_higlass.run_higlass_digest(tv_assembly[0])

            print(f"{tv_assembly[0]} - Generate higlass link...")
            url = higlass.generate_higlass_link(tv_assembly[0])

            postprocessing_succeeded.append((tv_assembly[0], url))
        else:
            postprocessing_failed.append((tv_assembly[0], status))



if __name__ == "__main__":
    main()