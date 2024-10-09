#!/usr/bin/env python

from methods.ToLTreevalJira import ToLTreevalJira
from methods.ToLHiGlass import ToLHiGlass
from methods.ToLKubeHiGlass import ToLKubeHiGlass
from methods.ToLTreevalFiles import ToLTreevalFiles
from methods.ToLS3 import ToLS3
from methods.ToLApi import ToLApi
from methods.ToLTreevalData import ToLTreevalData
import argparse
import yaml

def main(args=None):
    # args = parse_args(args)

    # Read parameters from environment parameters yaml.
    with open("environment_params.yaml", 'r') as file:
        env_params = yaml.safe_load(file)

    # Load objects
    jira = ToLTreevalJira(env_params["jira_path"])
    # s3 = ToLS3(env_params["local_s3_config"], env_params["pretext_snapshot_dir"], env_params["kmer_spectra_dir"])
    # kube_higlass = ToLKubeHiGlass(env_params["higlass_kubeconfig"], env_params["higlass_namespace"], env_params["higlass_deployment_name"])
    # tol_api = ToLApi()
    # treeval_data = ToLTreevalData()


    tv_issues = jira.get_issues_with_curation_status()
    for tv_issue in tv_issues:
        print(tv_issue.hap1_path)
        print(tv_issue.hap2_path)

    #     # Reload issue, so curation date is available.
    #     curation_issue = jira.load_issue(tv_issue.jira_key)
    #     # Update jira link
    #     values_dict = {}
    #     values_dict["jbrowse"], values_dict["jb_server"], values_dict["jb_scaffold"] = farm_dir.get_jbrowse_link_data(curation_issue.primary_tolid)
    #     values_dict["start"] = curation_issue.added_to_curation_date
    #     values_dict["btk_pr"], values_dict["btk_hp"] = farm_dir.get_btk_path(curation_issue.primary_tolid)
    #     values_dict["higlass"] = tv_issue.primary_tolid if kube_higlass.check_higlass_exists_for_tolid(curation_issue.primary_tolid) else ""
    #     values_dict["hic_plot"] = "Y" if s3.check_pretext_exists_in_s3(curation_issue.primary_tolid) else "N"
    #     values_dict["kmer_plot"] = "Y" if s3.check_kmer_exists_in_s3(curation_issue.primary_tolid) else "N"
    #     values_dict["taxon_id"] = tol_api.get_taxonid_from_tolid(curation_issue.species_id) or ""

    #     if treeval_data.check_if_treeval_data_string_update_required(tv_issue.treeval_data_dict, values_dict):
    #         jira.update_treeval_data_for_issue(tv_issue.jira_key, values_dict)


if __name__ == "__main__":
    main()