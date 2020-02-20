import pyworms
import logging
from .flags import Flag
from .status import Status
logger = logging.getLogger(__name__)


match_cache = {}


def check(taxa, cache=None):
    """Run all steps for taxonomic quality control."""
    check_fields(taxa)
    detect_lsid(taxa)
    match_worms(taxa, cache)
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
            aphiaid = pyworms.parseLSID(taxon["scientificNameID"])
            if aphiaid is None:
                taxon["invalid"].append("scientificNameID")
            else:
                taxon["aphiaid"] = aphiaid


def match_worms(taxa, cache=None):
    """Try to match any records that have a scientificName but no LSID. Results from previous batches are kept in a cache."""

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

    # do matching (todo: support cache)

    if len(names) > 0:
        allmatches = pyworms.aphiaRecordsByMatchNames(names, False)
        assert (len(allmatches) == len(names))
        for i in range(0, len(allmatches)):
            aphiaid = None
            matches = list(filter(lambda m: "status" in m and m["status"] != "uncertain", allmatches[i]))
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
    aphia_info = {
        "record": record,
        "classification": classification
    }
    if cache is not None:
        # cache did not have this info, storing it now
        cache.store(aphiaid, aphia_info)
    logger.debug(aphia_info)
    return aphia_info


def fetch(taxa, cache=None):
    """Fetch Aphia info from WoRMS, including alternative."""

    for key, taxon in taxa.items():
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

                    if taxon["aphia_info"]["record"]["status"] in [
                        Status.NOMEN_NUDUM.value,
                        Status.UNCERTAIN.value,
                        Status.UNACCEPTED.value,
                        Status.NOMEN_DUBIUM.value,
                        Status.TAXON_INQUIRENDUM.value,
                        Status.INTERIM_UNPUBLISHED.value,
                        Status.TEMPORARY_NAME.value
                    ]:
                        taxon["dropped"] = False
                    else:
                        taxon["dropped"] = True

            else:

                # accepted

                taxon["aphia"] = taxon["aphia_info"]["record"]["AphiaID"]
                taxon["marine"] = convert_environment(taxon["aphia_info"]["record"]["isMarine"])
                taxon["brackish"] = convert_environment(taxon["aphia_info"]["record"]["isBrackish"])

            # marine flag

            if taxon["marine"] is False and taxon["brackish"] is False:
                taxon["flags"].append(Flag.NOT_MARINE.value)
                taxon["dropped"] = True
            elif taxon["marine"] is None or taxon["marine"] is None:
                taxon["flags"].append(Flag.MARINE_UNSURE.value)
