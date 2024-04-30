#!/usr/bin/env python

from ToLJiraAuth import ToLJiraAuth
import JiraMethods as jm
import argparse


def parse_args(args=None):
    Description = "."
    Epilog = ">"

    parser = argparse.ArgumentParser(description=Description, epilog=Epilog)
    parser.add_argument("TOLID", help="TOLID.")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    return parser.parse_args(args)


def advance_to_curation(jira, issue, tolid, telo_exists):

     # To advance to curation.
        # 1. Set higlass entry
        # 2. Set pretext file location
        # 3. Add values to HiC checklist.
        # 4. Change status to curation

    if telo_exists:
        available_tracks = [{"value": "Pretext map"}, {"value": "HiGlass map"}, {"value": "Read coverage"}, {"value": "Repeat density"}, {"value": "Sequence gaps"}, {"value": "Telomeres"}]
    else:
        available_tracks = [{"value": "Pretext map"}, {"value": "HiGlass map"}, {"value": "Read coverage"}, {"value": "Repeat density"}, {"value": "Sequence gaps"}]

    fields = {
        "customfield_11603" : "/nfs/treeoflife-01/teams/grit/data/pretext_maps/",
        "customfield_11643" : tolid,
        "customfield_11619" : available_tracks
    }
    jira.transition_issue(issue, '491', fields=fields)


def main(args=None):

    args = parse_args(args)

    sample_name = args.TOLID.split("_")[0]


    tja = ToLJiraAuth()
    jql_request = f"status in ('HiC Building', 'geval analysis') AND 'Sample ID' ~ '{sample_name}'"

    results = tja.auth_jira.search_issues(jql_request)
    samples_ready = []

    for result in results:
        issue = tja.auth_jira.issue(result)

        species_id = jm.get_species_id(issue)
        # hap1_id, hap2_id, merged_id = jm.get_treeval_run_ids(issue)

        samples_ready.append(species_id)

    for sample in samples_ready:
        print(sample)

    val = input(f"Continue?\n")

    if val == "y":

        for result in results:
            issue = tja.auth_jira.issue(result)

            hap1_id, hap2_id, merged_id = jm.get_treeval_run_ids(issue)

            # transitions = tja.auth_jira.transitions(issue)
            # print(hap1_id)
            # print([(t['id'], t['name']) for t in transitions])

        # Check Higlass
        # module 


        # Check Pretext




            # telo_exists = True
            telo_exists = True
            advance_to_curation(tja.auth_jira, issue, hap1_id, telo_exists)


if __name__ == "__main__":
    main()

