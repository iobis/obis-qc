import pyworms
import logging
import requests
from obisqc.util.flags import Flag
from obisqc.util.status import Status
import re

logger = logging.getLogger(__name__)

match_cache = {}
annotated_list = None


def parse_scientificnameid(s):
    if not isinstance(s, str):
        return None
    if "urn:lsid:marinespecies.org:taxname:" in s:
        m = re.search("^urn:lsid:marinespecies.org:taxname:([0-9]+)$", s)
        if m:
            return m.group(1)
        else:
            return None
    elif "www.marinespecies.org/aphia.php" in s:
        m = re.search("^http[s]?:\/\/www\.marinespecies\.org\/aphia\.php\?p=taxdetails&id=([0-9]+)$", s)
        if m:
            return m.group(1)
        else:
            return None


def check(taxa, cache=None):
    """Run all steps for taxonomic quality control."""

    if annotated_list is None:
        get_annotated_list()

    check_fields(taxa)
    detect_lsid(taxa)
    match_worms(taxa, cache)
    check_blacklist(taxa)
    fetch(taxa, cache)
    process_info(taxa)


def check_fields(taxa):
    """Check if taxonomy related fields are present."""
    for key, taxon in taxa.items():
        if "scientificName" not in taxon or taxon["scientificName"] is None:
            taxon["missing"].append("scientificName")
        if "scientificNameID" not in taxon or taxon["scientificNameID"] is None:
            taxon["missing"].append("scientificNameID")


def detect_lsid(taxa):
    """Check if scientificNameID is present and parse LSID to Aphia ID."""
    for key, taxon in taxa.items():
        if "scientificNameID" in taxon and taxon["scientificNameID"] is not None:
            aphiaid = parse_scientificnameid(taxon["scientificNameID"])
            if aphiaid is None:
                taxon["invalid"].append("scientificNameID")
            else:
                taxon["aphiaid"] = aphiaid


def get_annotated_list():
    global annotated_list
    response = requests.get("https://api.obis.org/taxon/annotations")
    if response.status_code == 200:
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            annotated_list = dict()
            for entry in data["results"]:
                if entry["scientificname"] not in annotated_list:
                    annotated_list[entry["scientificname"]] = list()
                annotated_list[entry["scientificname"]].append(entry)
            logger.info("Fetched annotated list with %s names" % (len(data["results"])))
            return
    raise RuntimeError("Cannot access annotated list")


def check_blacklist(taxa):

    for key, taxon in taxa.items():
        if "scientificName" in taxon and taxon["scientificName"] is not None and "aphiaid" in taxon and taxon["aphiaid"] is None:

            if taxon["scientificName"] in annotated_list:
                possible_matches = annotated_list[taxon["scientificName"]]

                for possible_match in possible_matches:
                    if (possible_match["scientificnameid"] == taxon["scientificNameID"] and
                        possible_match["phylum"] == taxon["phylum"] and
                        possible_match["class"] == taxon["class"] and
                        possible_match["order"] == taxon["order"] and
                        possible_match["family"] == taxon["family"] and
                        possible_match["genus"] == taxon["genus"]
                    ):

                        if possible_match["annotation_resolved_aphiaid"] is not None:
                            taxon["aphiaid"] = possible_match["annotation_resolved_aphiaid"]
                            logger.info("Matched name %s using annotated list" % (taxon["scientificName"]))

                        annotation_type = possible_match["annotation_type"].lower()
                        if annotation_type == "black: no biota": taxon["flags"].append(Flag.WORMS_ANNOTATION_NO_BIOTA.value)
                        elif annotation_type == "black (no biota)": taxon["flags"].append(Flag.WORMS_ANNOTATION_NO_BIOTA.value)
                        elif annotation_type == "black (unresolvable, looks like a scientific name)": taxon["flags"].append(Flag.WORMS_ANNOTATION_UNRESOLVABLE.value)
                        elif annotation_type == "black: unresolvable, looks like a scientific name": taxon["flags"].append(Flag.WORMS_ANNOTATION_UNRESOLVABLE.value)
                        elif annotation_type == "grey/reject habitat": taxon["flags"].append(Flag.WORMS_ANNOTATION_REJECT_HABITAT.value)
                        elif annotation_type == "grey: reject: habitat": taxon["flags"].append(Flag.WORMS_ANNOTATION_REJECT_HABITAT.value)
                        elif annotation_type == "grey/reject species grouping": taxon["flags"].append(Flag.WORMS_ANNOTATION_REJECT_GROUPING.value)
                        elif annotation_type == "grey: reject: species grouping": taxon["flags"].append(Flag.WORMS_ANNOTATION_REJECT_GROUPING.value)
                        elif annotation_type == "grey/reject ambiguous": taxon["flags"].append(Flag.WORMS_ANNOTATION_REJECT_AMBIGUOUS.value)
                        elif annotation_type == "grey: reject: ambiguous": taxon["flags"].append(Flag.WORMS_ANNOTATION_REJECT_AMBIGUOUS.value)
                        elif annotation_type == "grey/reject fossil": taxon["flags"].append(Flag.WORMS_ANNOTATION_REJECT_FOSSIL.value)
                        elif annotation_type == "grey: reject: fossil": taxon["flags"].append(Flag.WORMS_ANNOTATION_REJECT_FOSSIL.value)
                        elif annotation_type == "white/typo: resolvable to aphiaid": taxon["flags"].append(Flag.WORMS_ANNOTATION_RESOLVABLE_TYPO.value)
                        elif annotation_type == "white/exact match, authority included": taxon["flags"].append(Flag.WORMS_ANNOTATION_RESOLVABLE_AUTHORITY.value)
                        elif annotation_type == "white/unpublished combination: resolvable to aphiaid": taxon["flags"].append(Flag.WORMS_ANNOTATION_RESOLVABLE_UNPUBLISHED.value)
                        elif annotation_type == "white/human intervention, resolvable to aphiaid": taxon["flags"].append(Flag.WORMS_ANNOTATION_RESOLVABLE.value)
                        elif annotation_type == "white: human intervention: resolvable to aphiaid": taxon["flags"].append(Flag.WORMS_ANNOTATION_RESOLVABLE.value)
                        elif annotation_type == "white: human intervention, resolvable to aphiaid": taxon["flags"].append(Flag.WORMS_ANNOTATION_RESOLVABLE.value)
                        elif annotation_type == "white: human intervention: exact match, authority included": taxon["flags"].append(Flag.WORMS_ANNOTATION_RESOLVABLE_AUTHORITY.value)
                        elif annotation_type == "white/human intervention, loss of info, resolvable to aphiaid": taxon["flags"].append(Flag.WORMS_ANNOTATION_RESOLVABLE_LOSS.value)
                        elif annotation_type == "white: human intervention: loss of information, resolvable to aphiaid": taxon["flags"].append(Flag.WORMS_ANNOTATION_RESOLVABLE_LOSS.value)
                        elif annotation_type == "blue/awaiting editor feedback": taxon["flags"].append(Flag.WORMS_ANNOTATION_AWAIT_EDITOR.value)
                        elif annotation_type == "blue/awaiting provider feedback": taxon["flags"].append(Flag.WORMS_ANNOTATION_AWAIT_PROVIDER.value)
                        elif annotation_type == "blue/dmt to process": taxon["flags"].append(Flag.WORMS_ANNOTATION_TODO.value)
                        else: raise RuntimeError("Unknown annotation %s" % (annotation_type))

                        break


def sanitize_name(name):
    return name.replace("#", "")


def match_worms(taxa, cache=None):
    """Try to match any records that have a scientificName but no LSID. Results from previous batches are kept in a cache."""

    logger.debug("There are %s names in match cache" % (len(match_cache.keys())))

    # gather all keys and names that need matching (no LSID, not in matching cache)

    allkeys = taxa.keys()
    names = []
    keys = []
    for key in allkeys:
        if taxa[key]["aphiaid"] is None and "scientificName" in taxa[key] and taxa[key]["scientificName"] is not None:
            name = taxa[key]["scientificName"]
            if name in match_cache:
                taxa[key]["aphiaid"] = match_cache[name]
            else:
                keys.append(key)
                names.append(name)

    # sanitize

    names = [sanitize_name(name) for name in names]

    # do matching (todo: support cache)

    if len(names) > 0:
        allmatches = pyworms.aphiaRecordsByMatchNames(names, False)
        assert (len(allmatches) == len(names))
        for i in range(0, len(allmatches)):
            aphiaid = None
            #matches = list(filter(lambda m: "status" in m and m["status"] != "uncertain", allmatches[i]))
            matches = allmatches[i]
            if matches is not None and len(matches) == 1:
                if matches[0]["match_type"] == "exact" or matches[0]["match_type"] == "exact_subgenus":
                    aphiaid = matches[0]["AphiaID"]
            taxa[keys[i]]["aphiaid"] = aphiaid
            match_cache[names[i]] = aphiaid


def has_alternative(aphia_info):
    """Check if an alternative valid AphiaID is present and different from the AphiaID."""
    return "valid_AphiaID" in aphia_info["record"] and aphia_info["record"]["valid_AphiaID"] is not None and aphia_info["record"]["AphiaID"] != aphia_info["record"]["valid_AphiaID"]


def is_accepted(aphia_info):
    """Check if the Aphia status is accepted."""
    return aphia_info["record"]["status"] == Status.ACCEPTED.value


def convert_environment(env):
    """Convert an environment flag from integer to boolean."""
    if env is None:
        return None
    else:
        return bool(env)


def fetch_aphia(aphiaid, cache=None):
    """Fetch the Aphia record and classification for an AphiaID."""
    if cache is not None:
        aphia_info = cache.fetch(aphiaid)
        if aphia_info is not None:
            # cache has result, return
            return aphia_info
    # no cache or no cache result

    record = pyworms.aphiaRecordByAphiaID(aphiaid)
    classification = pyworms.aphiaClassificationByAphiaID(aphiaid)
    bold_id = pyworms.aphiaExternalIDByAphiaID(aphiaid, "bold")
    ncbi_id = pyworms.aphiaExternalIDByAphiaID(aphiaid, "ncbi")
    distribution = pyworms.aphiaDistributionsByAphiaID(aphiaid)
    bold_id = bold_id[0] if bold_id is not None and isinstance(bold_id, list) and len(bold_id) > 0 else None
    ncbi_id = ncbi_id[0] if ncbi_id is not None and isinstance(ncbi_id, list) and len(ncbi_id) > 0 else None
    aphia_info = {
        "record": record,
        "classification": classification,
        "bold_id": bold_id,
        "ncbi_id": ncbi_id,
        "distribution": distribution
    }
    if cache is not None:
        # cache did not have this info, storing it now
        cache.store(aphiaid, aphia_info)
    return aphia_info


def fetch(taxa, cache=None):
    """Fetch Aphia info from WoRMS, including alternative."""

    for key, taxon in taxa.items():

        # TODO: fetch all aphia info records including alternatives in one go

        if "aphiaid" in taxon and taxon["aphiaid"] is not None:
            aphiaid = taxon["aphiaid"]
            aphia_info = fetch_aphia(aphiaid, cache)
            if aphia_info["record"] is None or aphia_info["classification"] is None:
                pass
            else:
                taxon["aphia_info"] = aphia_info
                if has_alternative(aphia_info):

                    # alternative provided

                    aphia_info_accepted = fetch_aphia(taxon["aphia_info"]["record"]["valid_AphiaID"], cache)
                    if aphia_info_accepted["record"] is None or aphia_info_accepted["classification"] is None:
                        pass
                    else:
                        taxon["aphia_info_accepted"] = aphia_info_accepted


def process_info(taxa):
    """Go through processed list of taxa to add flags and mark as dropped."""

    for key, taxon in taxa.items():

        if taxon["aphia_info"] is None:

            # no Aphia record found

            taxon["flags"].append(Flag.NO_MATCH.value)
            taxon["dropped"] = True

            if taxon["scientificNameID"] is not None:
                if "scientificNameID" not in taxon["invalid"]:
                    taxon["invalid"].append("scientificNameID")

        else:

            taxon["dropped"] = False

            # Aphia record found

            if not is_accepted(taxon["aphia_info"]):

                # not accepted

                if taxon["aphia_info_accepted"] is not None:

                    # alternative provided

                    taxon["aphia"] = taxon["aphia_info_accepted"]["record"]["AphiaID"]
                    taxon["unaccepted"] = taxon["aphia_info"]["record"]["AphiaID"]
                    taxon["marine"] = convert_environment(taxon["aphia_info_accepted"]["record"]["isMarine"])
                    taxon["brackish"] = convert_environment(taxon["aphia_info_accepted"]["record"]["isBrackish"])

                else:

                    # no alternative provided

                    taxon["flags"].append(Flag.NO_ACCEPTED_NAME.value)

                    taxon["aphia"] = taxon["aphia_info"]["record"]["AphiaID"]
                    taxon["marine"] = convert_environment(taxon["aphia_info"]["record"]["isMarine"])
                    taxon["brackish"] = convert_environment(taxon["aphia_info"]["record"]["isBrackish"])

            else:

                # accepted

                taxon["aphia"] = taxon["aphia_info"]["record"]["AphiaID"]
                taxon["marine"] = convert_environment(taxon["aphia_info"]["record"]["isMarine"])
                taxon["brackish"] = convert_environment(taxon["aphia_info"]["record"]["isBrackish"])

            # marine flag

            if taxon["marine"] is False and taxon["brackish"] is False:
                taxon["flags"].append(Flag.NOT_MARINE.value)
                taxon["dropped"] = True
            elif taxon["marine"] is not True and taxon["brackish"] is not True:
                taxon["flags"].append(Flag.MARINE_UNSURE.value)
