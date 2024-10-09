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

def parse_args(args=None):
    Description = "."
    Epilog = ">"

    parser = argparse.ArgumentParser(description=Description, epilog=Epilog)
    parser.add_argument("TOLID", nargs='?', default="", help="TOLID.")
    parser.add_argument("Assignee", nargs='?', default="", help="TOLID.")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    return parser.parse_args(args)

def main(args=None):

    args = parse_args(args)

    # Read parameters from environment parameters yaml.
    with open("environment_params.yaml", 'r') as file:
        env_params = yaml.safe_load(file)

    # Load objects
    jira = ToLTreevalJira(env_params["jira_path"])
    farm_dir = ToLTreevalFiles(env_params["higlass_upload_dir"], 
                                env_params["higlass_internal_upload_dir"], 
                                env_params["stats_dir"], 
                                env_params["pretext_snapshot_dir"], 
                                env_params["kmer_spectra_dir"], 
                                env_params["jbrowse_dev_dir"],
                                env_params["jbrowse_prod_dir"],
                                env_params["btk_dir"], 
                                env_params["pretext_maps_dir"])
    kube_higlass = ToLKubeHiGlass(env_params["higlass_kubeconfig"], env_params["higlass_namespace"], env_params["higlass_deployment_name"])
    higlass = ToLHiGlass(env_params["higlass_url"], env_params["higlass_upload_dir"], env_params["higlass_internal_upload_dir"])
    s3 = ToLS3(env_params["local_s3_config"], env_params["pretext_snapshot_dir"], env_params["kmer_spectra_dir"])
    tol_api = ToLApi()
    treeval_data = ToLTreevalData()
                        
    tolid_list = kube_higlass.get_all_tileset_tolids()
    with open("tileset_summary.txt", 'w') as f_out:
        f_out.write(kube_higlass.get_all_tileset_details())

    tileset_names = kube_higlass.get_all_tileset_names()

    tracks_missing = {}
    for tolid in tolid_list:
        missing = []

        if not f"{tolid}_grid" in tileset_names:
            missing.append("grid")

        if not f"{tolid}_map" in tileset_names:
            missing.append("map")

        if not f"{tolid}_coverage" in tileset_names and not f"{tolid}_coverage_normal" in tileset_names:
            missing.append("coverage")

        if not f"{tolid}_repeat_density" in tileset_names:
            missing.append("repeat_density")

        if not f"{tolid}_seqgap" in tileset_names:
            missing.append("telomere")

        if not f"{tolid}_telomere" in tileset_names:
            missing.append("telomere")


        if len(missing) > 0:
            tracks_missing[tolid] = missing

    for key, val in tracks_missing.items():
        print(f"{key} - {','.join(val)}")
    print(len(tracks_missing))


    # Get list of all tolids on server.


if __name__ == "__main__":
    main()