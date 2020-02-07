import pyworms
import logging
logger = logging.getLogger(__name__)


match_cache = {}


def check(taxa):
    check_fields(taxa)
    detect_lsid(taxa)
    #match_locally(taxa) # Todo: allow local matching?
    match_worms(taxa)
    fetch(taxa)
    process_info(taxa)


def check_fields(taxa):
    for key, taxon in taxa.items():
        if "scientificName" not in taxon or taxon["scientificName"] is None:
            taxon["missing"].append("scientificName")
        if "scientificNameID" not in taxon or taxon["scientificNameID"] is None:
            taxon["missing"].append("scientificNameID")


def detect_lsid(taxa):
    """Checks if scientificNameID is present and parses LSID to Aphia ID."""

    for key, taxon in taxa.items():
        if "scientificNameID" in taxon and taxon["scientificNameID"] is not None:
            lsid = pyworms.parseLSID(taxon["scientificNameID"])
            if lsid is None:
                taxon["invalid"].append("scientificNameID")
            else:
                taxon["lsid"] = lsid


def match_worms(taxa):
    """Try to match any records that have a scientificName but no LSID. Results from previous batches are kept in a cache."""

    # gather all keys and names that need matching (no LSID, not in cache)

    allkeys = taxa.keys()
    names = []
    keys = []
    for key in allkeys:
        if taxa[key]["lsid"] is None and "scientificName" in taxa[key] and taxa[key]["scientificName"] is not None:
            name = taxa[key]["scientificName"]
            if name in match_cache:
                taxa[key]["lsid"] = match_cache[name]
            else:
                keys.append(key)
                names.append(name)

    # do matching

    if len(names) > 0:
        allmatches = pyworms.aphiaRecordsByMatchNames(names, False)
        assert (len(allmatches) == len(names))
        for i in range(0, len(allmatches)):
            lsid = None
            matches = list(filter(lambda m: "status" in m and m["status"] != "uncertain", allmatches[i]))
            if matches is not None and len(matches) == 1:
                if matches[0]["match_type"] == "exact" or matches[0]["match_type"] == "exact_subgenus":
                    lsid = matches[0]["AphiaID"]
            taxa[keys[i]]["lsid"] = lsid
            match_cache[names[i]] = lsid


def has_alternative(aphia_info):
    return "valid_AphiaID" in aphia_info["record"] and aphia_info["record"]["valid_AphiaID"] is not None and aphia_info["record"]["AphiaID"] != aphia_info["record"]["valid_AphiaID"]


def convert_environment(env):
    if env is None:
        return None
    else:
        return bool(env)


def fetch_aphia(lsid):
    record = pyworms.aphiaRecordByAphiaID(lsid)
    classification = pyworms.aphiaClassificationByAphiaID(lsid)
    aphia_info = {
        "record": record,
        "classification": classification
    }
    logger.debug(aphia_info)
    return aphia_info


def fetch(taxa):
    """Fetch aphia info from WoRMS. Todo: sync with OBIS database."""

    for key, taxon in taxa.items():
        if "lsid" in taxon and taxon["lsid"] is not None:
            lsid = taxon["lsid"]
            aphia_info = fetch_aphia(lsid)
            if aphia_info["record"] is None or aphia_info["classification"] is None:
                pass
            else:
                taxon["aphia_info"] = aphia_info
                if has_alternative(aphia_info):

                    # status not accepted

                    aphia_info_accepted = fetch_aphia(taxon["aphia_info"]["record"]["valid_AphiaID"])
                    if aphia_info_accepted["record"] is None or aphia_info_accepted["classification"] is None:
                        pass
                    else:
                        taxon["aphia_info_accepted"] = aphia_info_accepted


def process_info(taxa):
    """Go through processed list of taxa to add flags and mark as dropped."""

    for key, taxon in taxa.items():
        if taxon["aphia_info"] is None:

            # no Aphia record found

            taxon["flags"].append("no_match")
            taxon["dropped"] = True

            if taxon["scientificNameID"] is not None:
                if "scientificNameID" not in taxon["invalid"]:
                    taxon["invalid"].append("scientificNameID")

        else:

            # Aphia record found

            if has_alternative(taxon["aphia_info"]):

                # not accepted

                if taxon["aphia_info_accepted"] is not None:

                    # alternative provided

                    taxon["aphia"] = taxon["aphia_info_accepted"]["record"]["AphiaID"]
                    taxon["unaccepted"] = taxon["aphia_info"]["record"]["AphiaID"]
                    taxon["marine"] = convert_environment(taxon["aphia_info_accepted"]["record"]["isMarine"])
                    taxon["brackish"] = convert_environment(taxon["aphia_info_accepted"]["record"]["isBrackish"])

                else:

                    # no alternative provided

                    taxon["flags"].append("no_match")
                    taxon["dropped"] = True
                    return

            else:

                # accepted

                taxon["aphia"] = taxon["aphia_info"]["record"]["AphiaID"]
                taxon["marine"] = convert_environment(taxon["aphia_info"]["record"]["isMarine"])
                taxon["brackish"] = convert_environment(taxon["aphia_info"]["record"]["isBrackish"])

            if taxon["marine"] is False and taxon["brackish"] is False:

                # not marine

                taxon["flags"].append("not_marine")
                taxon["dropped"] = True

            elif taxon["marine"] is None or taxon["marine"] is None:

                # marine unsure

                taxon["flags"].append("marine_unsure")
