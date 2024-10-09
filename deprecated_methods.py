def get_issues(self, tolid_assembly, assignee, status):
        jql_clauses = []
        messages = []
        if status:
            jql_clauses.append(f"status in ('{status}')")
            messages.append(f"Status: {status}")
        if assignee:
            jql_clauses.append(f"assignee = {assignee}")
            messages.append(f"Assignee: {assignee}")
        if tolid_assembly:
            jql_clauses.append(f"'Sample ID' ~ {tolid_assembly}")
            messages.append(f"TOLID: {tolid_assembly}")

        if jql_clauses:
            jql_query = f"{' AND '.join(jql_clauses)} ORDER BY priority DESC, updated DESC"

            results = self.jira_api.search_issues(jql_query,maxResults=0, expand='changelog')
            issues = []

            if results:
                for result in results:
                    # parse jira issue into ToLTreevalJira object.
                    try:
                        issue = self.jira_api.issue(result)
                        tv_issue = ToLTreevalJiraIssue(issue, self._override_hap1_path, self._override_hap2_path, self._override_longread_dir, self._override_hic_dir)
                        issues.append(tv_issue)
                    except Exception as e:
                        print("Unable to parse issue.")
                        print(e)
                        sys.exit(1)

                return issues
            else:
                print(f"No results found for {', '.join(messages)}")
                sys.exit(1)
        else:
            print("No parameters provided for query.")
            sys.exit(1)


                def delete_http_request(self, url, headers, params):
        session = self.launch_http_request_session()
        response = session.delete(
            url = url,
            headers=headers,
            params=params
        )
        if (response.status_code == 200) or (response.status_code == 204):
            return True
        else:
            print(f"Delete HTTP Request to {url} failed.")
            print(response.json())
            sys.exit(1)
        # Saving CO2 summary
        # for co2_file in glob.glob(f"{treeval_path}/work/co2footprint_trace_*"):
        #     self.copy_file(co2_file, f"{self.stats_dir}/co2footprint_{tolid_assembly}.txt")

                # def cleanup_treeval_working_directory(self, tolid_assembly_hap1, tolid_assembly_hap2, tolid_assembly_merged):
    #     # Clean up working directory.
    #     if os.path.isdir(f"{tolid_assembly_hap1}/working/work"):
    #         shutil.rmtree(f"{tolid_assembly_hap1}/working/work")
    #     if os.path.isdir(f"{tolid_assembly_hap2}/working/work"):        
    #         shutil.rmtree(f"{tolid_assembly_hap2}/working/work")
    #     if os.path.isdir(f"{tolid_assembly_merged}/working/work"):
    #         shutil.rmtree(f"{tolid_assembly_merged}/working/work")


        def get_geval_project(self, issue):
        geval_project = issue.fields.customfield_11643

        if geval_project:
            return geval_project.split("_")[1].upper()
        else:
            return ""
        
            def get_telo_seq(self, issue):
        get_telo_seq = issue.fields.customfield_11650

        if get_telo_seq:
            return get_telo_seq
        else:
            return ""
        
            def get_alternative_hic(self, issue):
        yaml_data = self.get_yaml_attachment(issue)
        yaml_notes = yaml_data["combine_for_curation"]

        for yaml_note in yaml_notes:
            # Trim unused common name
            prefix = "hic data was from "
            if yaml_note.startswith(prefix):
                return yaml_note[len(prefix):]
            

        def get_haplotype_to_curate(self, issue):
        yaml_data = self.get_yaml_attachment(issue)
        haplotype_to_curate = yaml_data["haplotype_to_curate"]

        if haplotype_to_curate:
            return haplotype_to_curate
        else:
            return "hap1"
        
            def get_geval_species_id(self, issue):
        geval_species_id = issue.fields.customfield_11643

        if geval_species_id:
            return geval_species_id.split("_")[2] + "_" + geval_species_id.split("_")[3]
        else:
            return ""
        

            def get_species_name(self, issue):
        species_name = issue.fields.customfield_11676

        if species_name:

            # Trim unused common name
            suffix = " ()"
            if species_name.endswith(suffix):
                species_name = species_name[:-len(suffix)]

            return species_name
        else:
            return ""
        



    def get_species_id(self, issue):
        species_id = issue.fields.customfield_11627

        if species_id:
            return species_id
        else:
            return ""