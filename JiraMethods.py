import yaml
from yaml.loader import SafeLoader

# Methods for reading from JIRA object.

def get_species_name(issue):
    species_name = issue.fields.customfield_11676

    if species_name:

        # Trim unused common name
        suffix = " ()"
        if species_name.endswith(suffix):
            species_name = species_name[:-len(suffix)]

        return species_name
    else:
        return ""

def get_species_id(issue):
    species_id = issue.fields.customfield_11627

    if species_id:
        return species_id
    else:
        return ""

def get_treeval_run_ids(issue):
    treeval_runs = issue.fields.customfield_12200
    hap1 = None
    hap2 = None
    merged = None

    if treeval_runs:

        for treeval_run in treeval_runs.split(', '):
            # print(treeval_run)
            if treeval_run.startswith("hap1:"):
                hap1 = treeval_run.replace("hap1: ","")
            elif treeval_run.startswith("hap2:"):
                hap2 = treeval_run.replace("hap2: ","")
            elif treeval_run.startswith("merged:"):
                merged = treeval_run.replace("merged: ","")

    return hap1, hap2, merged

def get_treeval_run_id(issue):
    treeval_run = issue.fields.customfield_12200
    # hap1 = None
    # hap2 = None
    # merged = None

    # if treeval_runs:

    #     for treeval_run in treeval_runs.split(', '):
    #         # print(treeval_run)
    #         if treeval_run.startswith("hap1:"):
    #             hap1 = treeval_run.replace("hap1: ","")
    #         elif treeval_run.startswith("hap2:"):
    #             hap2 = treeval_run.replace("hap2: ","")
    #         elif treeval_run.startswith("merged:"):
    #             merged = treeval_run.replace("merged: ","")

    return treeval_run

def get_geval_species_id(issue):
    geval_species_id = issue.fields.customfield_11643

    if geval_species_id:
        return geval_species_id.split("_")[2] + "_" + geval_species_id.split("_")[3]
    else:
        return ""

def get_geval_project(issue):
    geval_project = issue.fields.customfield_11643

    if geval_project:
        return geval_project.split("_")[1].upper()
    else:
        return ""

def get_assembly_version(issue):
    get_assembly_version = issue.fields.customfield_11625

    if get_assembly_version:
        return get_assembly_version
    else:
        return ""

def get_telo_seq(issue):
    get_telo_seq = issue.fields.customfield_11650

    if get_telo_seq:
        return get_telo_seq
    else:
        return ""

def get_clade(issue):
    con_file_path = issue.fields.customfield_11677

    if con_file_path:

        if con_file_path.split("/")[5] == "tol-nematodes":
            return "nematodes"
        else:
            return con_file_path.split("/")[7]
    else:
        return ""

def get_contamination_files_path(issue):
    con_file_path = issue.fields.customfield_11677

    if con_file_path:
        return con_file_path
    else:
        return ""

def get_yaml_attachment(issue):
    for attachment in issue.fields.attachment:
        if attachment.filename.endswith('.yaml') or attachment.filename.endswith('.yml'):
            yaml_data = yaml.load(attachment.get(), Loader=SafeLoader)
            return yaml_data

def get_alternative_hic(issue):
    yaml_data = get_yaml_attachment(issue)
    yaml_notes = yaml_data["combine_for_curation"]

    for yaml_note in yaml_notes:
        # Trim unused common name
        prefix = "hic data was from "
        if yaml_note.startswith(prefix):
            return yaml_note[len(prefix):]

def get_combine_for_curation_status(issue):
    yaml_data = get_yaml_attachment(issue)
    if yaml_data.get("combine_for_curation") is not None:
        combine_status = yaml_data["combine_for_curation"]
    
        if combine_status:
            return True
        else:
            return False
    else:
        return False

def get_haplotype_to_curate(issue):
    yaml_data = get_yaml_attachment(issue)
    haplotype_to_curate = yaml_data["haplotype_to_curate"]

    if haplotype_to_curate:
        return haplotype_to_curate
    else:
        return "hap1"

def get_hap1_path(issue):
    yaml_data = get_yaml_attachment(issue)
    if yaml_data:
        if yaml_data.get("hap1") is not None:
            hap1 = yaml_data["hap1"]

            if hap1:
                return hap1
            else:
                return ""
        elif yaml_data.get("primary") is not None:
            pri = yaml_data["primary"]

            if pri:
                return pri
            else:
                return ""
        else:
            return ""
    else:
        return ""

def get_hap2_path(issue):
    yaml_data = get_yaml_attachment(issue)
    if yaml_data.get("hap2") is not None:
        hap2 = yaml_data["hap2"]

        if hap2:
            return hap2
        else:
            return ""

    elif yaml_data.get("haplotigs") is not None:
        haplo = yaml_data["haplotigs"]

        if haplo:
            return haplo
        else:
            return ""
    else:
        return ""

def get_pacbio_dir(issue):
    yaml_data = get_yaml_attachment(issue)
    return yaml_data["pacbio_read_dir"]

def get_hic_read_dir(issue):
    yaml_data = get_yaml_attachment(issue)
    return yaml_data["hic_read_dir"]

def get_longread_type(issue):
    yaml_data = get_yaml_attachment(issue)
    return yaml_data["pacbio_read_type"]


def get_added_to_curation_date_from_issue(issue):
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
        return min(created_dates)
    else:
        return created_dates[0]