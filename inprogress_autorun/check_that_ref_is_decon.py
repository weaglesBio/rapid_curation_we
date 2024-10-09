#!/usr/bin/env python

from methods.ToLTreevalJira import ToLTreevalJira
from methods.ToLTreevalFiles import ToLTreevalFiles
from methods.ToLTreevalData import ToLTreevalData
from methods.ToLTelofinder import TelomereFinder
import argparse
import yaml
import sys
import os
import filecmp

def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Taking a jira ticket number, derive the yaml file to run TREEVAL', formatter_class=argparse.ArgumentDefaultsHelpFormatter) 
    parser.add_argument('--ticket', metavar='ticket', type=str, required=True, help='ticket number')
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    
    return parser.parse_args(args)


def main(args=None):
    args = parse_args(args)

    # Read parameters from environment parameters yaml.
    with open("environment_params.yaml", 'r') as file:
        env_params = yaml.safe_load(file)

    # Load objects
    jira = ToLTreevalJira(env_params["jira_path"])
    treeval_data = ToLTreevalData()

    # Load issue from jira from ticket.
    tv_issue = jira.get_issue_from_ticket_id(args.ticket)
    print(f"Issue {tv_issue.species_id} loaded from ticket ID: {args.ticket}")

    # Load object dependent on internal mode.
    farm_dir = ToLTreevalFiles((env_params["higlass_internal_upload_dir"] if tv_issue.is_internal else env_params["higlass_upload_dir"]), 
                                env_params["stats_dir"], 
                                env_params["pretext_snapshot_dir"], 
                                env_params["kmer_spectra_dir"], 
                                env_params["jbrowse_dev_dir"],
                                env_params["jbrowse_prod_dir"],
                                env_params["btk_dir"], 
                                env_params["pretext_maps_dir"])


    if tv_issue.tv_path_hap1:
        print(tv_issue.hap1_path)
        farm_dir.copy_reference_file(tv_issue.hap1_path, os.path.join(tv_issue.tv_path_hap1, "raw"), "decon.fa")
        cmpresult = filecmp.cmp(os.path.join(tv_issue.tv_path_hap1, "raw", "ref.fa"), os.path.join(tv_issue.tv_path_hap1, "raw", "decon.fa"))
        print(os.path.join(tv_issue.tv_path_hap1, "raw", "ref.fa"))
        print(os.stat(os.path.join(tv_issue.tv_path_hap1, "raw", "ref.fa")).st_size)
        print(os.path.join(tv_issue.tv_path_hap1, "raw", "decon.fa"))
        print(os.stat(os.path.join(tv_issue.tv_path_hap1, "raw", "decon.fa")).st_size)
        print(cmpresult)


        # os.path.pardir(tv_issue.tv_path_hap1)
        # os.path.pardir(tv_issue.tv_path_hap1)
        # os.path.pardir(tv_issue.tv_path_hap2)
        # os.path.pardir(tv_issue.tv_path_merged)


    # Copy file to existing folder for each, called decon.fa

    # Compare the files


if __name__ == "__main__":
    main()