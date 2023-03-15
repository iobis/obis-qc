from typing import Dict
import pyworms
import logging
import requests
from obisqc.model import AphiaCacheInterface, AphiaInfo
from obisqc.util.flags import Flag
from obisqc.util.status import Status
import re
import asyncio
import itertools
import time
from math import ceil


logger = logging.getLogger(__name__)

match_cache: Dict[str, int] = {}
annotated_list = None


def parse_scientificnameid(input: str) -> int:
    if not isinstance(input, str):
        return None
    if "urn:lsid:marinespecies.org:taxname:" in input:
        m = re.search("^urn:lsid:marinespecies.org:taxname:([0-9]+)$", input)
        if m:
            return int(m.group(1))
        else:
            return None
    elif "www.marinespecies.org/aphia.php" in input:
        m = re.search("^http[s]?:\/\/www\.marinespecies\.org\/aphia\.php\?p=taxdetails&id=([0-9]+)$", input)
        if m:
            return int(m.group(1))
        else:
            return None


def get_annotated_list() -> None:
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
            logger.debug("Fetched annotated list with %s names" % (len(data["results"])))
            return
    raise RuntimeError("Cannot access annotated list")


def check_annotated_list(taxa):

    for key, taxon in taxa.items():
        if taxon.get("scientificName") is not None and taxon.aphiaid is None:

            if taxon.get("scientificName") in annotated_list:
                possible_matches = annotated_list[taxon.get("scientificName")]

                for possible_match in possible_matches:
                    if (
                        possible_match["scientificnameid"] == taxon.get("scientificNameID") and
                        possible_match["phylum"] == taxon.get("phylum") and
                        possible_match["class"] == taxon.get("class") and
                        possible_match["order"] == taxon.get("order") and
                        possible_match["family"] == taxon.get("family") and
                        possible_match["genus"] == taxon.get("genus")
                    ):

                        if possible_match["annotation_resolved_aphiaid"] is not None:
                            if possible_match["annotation_resolved_aphiaid"] is not None:
                                taxon.aphiaid = int(possible_match["annotation_resolved_aphiaid"])
                            logger.debug("Matched name %s using annotated list" % (taxon.get("scientificName")))

                        annotation_type = possible_match["annotation_type"].lower()
                        if annotation_type == "black: no biota":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_NO_BIOTA)
                        elif annotation_type == "black (no biota)":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_NO_BIOTA)
                        elif annotation_type == "black (unresolvable, looks like a scientific name)":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_UNRESOLVABLE)
                        elif annotation_type == "black: unresolvable, looks like a scientific name":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_UNRESOLVABLE)
                        elif annotation_type == "grey/reject habitat":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_REJECT_HABITAT)
                        elif annotation_type == "grey: reject: habitat":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_REJECT_HABITAT)
                        elif annotation_type == "grey/reject species grouping":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_REJECT_GROUPING)
                        elif annotation_type == "grey: reject: species grouping":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_REJECT_GROUPING)
                        elif annotation_type == "grey/reject ambiguous":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_REJECT_AMBIGUOUS)
                        elif annotation_type == "grey: reject: ambiguous":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_REJECT_AMBIGUOUS)
                        elif annotation_type == "grey/reject fossil":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_REJECT_FOSSIL)
                        elif annotation_type == "grey: reject: fossil":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_REJECT_FOSSIL)
                        elif annotation_type == "white/typo: resolvable to aphiaid":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_RESOLVABLE_TYPO)
                        elif annotation_type == "white/exact match, authority included":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_RESOLVABLE_AUTHORITY)
                        elif annotation_type == "white/unpublished combination: resolvable to aphiaid":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_RESOLVABLE_UNPUBLISHED)
                        elif annotation_type == "white/human intervention, resolvable to aphiaid":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_RESOLVABLE)
                        elif annotation_type == "white: human intervention: resolvable to aphiaid":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_RESOLVABLE)
                        elif annotation_type == "white: human intervention, resolvable to aphiaid":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_RESOLVABLE)
                        elif annotation_type == "white: human intervention: exact match, authority included":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_RESOLVABLE_AUTHORITY)
                        elif annotation_type == "white/human intervention, loss of info, resolvable to aphiaid":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_RESOLVABLE_LOSS)
                        elif annotation_type == "white: human intervention: loss of information, resolvable to aphiaid":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_RESOLVABLE_LOSS)
                        elif annotation_type == "blue/awaiting editor feedback":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_AWAIT_EDITOR)
                        elif annotation_type == "blue/awaiting provider feedback":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_AWAIT_PROVIDER)
                        elif annotation_type == "blue/dmt to process":
                            taxon.set_flag(Flag.WORMS_ANNOTATION_TODO)
                        else:
                            raise RuntimeError("Unknown annotation %s" % (annotation_type))

                        break


def sanitize_name(name: str) -> str:
    return name.replace("#", "")


async def match_task(names):
    matches = pyworms.aphiaRecordsByMatchNames(names, False)
    return matches


def chunk_into_n(lst, n):
    size = ceil(len(lst) / n)
    return list(map(lambda x: lst[x * size:x * size + size], list(range(n))))


async def match_parallel(names):
    if len(names) > 2:
        parts = chunk_into_n(names, 5)
    else:
        parts = [names]
    matches = await asyncio.gather(*[match_task(part) for part in parts])
    return list(itertools.chain.from_iterable(matches))


def match_obis(taxa: Dict[str, AphiaInfo], cache: AphiaCacheInterface):
    if cache is not None:
        allkeys = taxa.keys()
        for key in allkeys:
            if taxa[key].aphiaid is None and taxa[key].get("scientificName") is not None:
                name = taxa[key].get("scientificName")
                taxa[key].aphiaid = cache.match_name(name)


def match_worms(taxa: Dict[str, AphiaInfo]):
    """Try to match any records that have a scientificName but no LSID. Results from previous batches are kept in a cache."""

    logger.debug("There are %s names in match cache" % (len(match_cache.keys())))

    # gather all keys and names that need matching (no LSID, not in matching cache)

    allkeys = taxa.keys()
    names = []
    keys = []
    for key in allkeys:
        if taxa[key].aphiaid is None and taxa[key].get("scientificName") is not None:
            name = taxa[key].get("scientificName")
            if name in match_cache:
                taxa[key].aphiaid = match_cache[name]
            else:
                keys.append(key)
                names.append(name)

    # sanitize

    names = [sanitize_name(name) for name in names]

    # do matching (todo: support cache)

    if len(names) > 0:

        start_time = time.time()
        loop = asyncio.get_event_loop()
        coroutine = match_parallel(names)
        allmatches = loop.run_until_complete(coroutine)
        seconds = format(time.time() - start_time, ".2f")
        logger.debug(f"Matched {len(names)} names in {seconds} seconds")

        assert (len(allmatches) == len(names))
        for i in range(0, len(allmatches)):
            aphiaid = None
            matches = allmatches[i]
            if matches is not None and len(matches) == 1:
                if matches[0]["match_type"] == "exact" or matches[0]["match_type"] == "exact_subgenus":
                    if matches[0]["AphiaID"] is not None:
                        aphiaid = int(matches[0]["AphiaID"])
            taxa[keys[i]].aphiaid = aphiaid
            match_cache[names[i]] = aphiaid


def has_alternative(aphia_info: AphiaInfo):
    """Check if an alternative valid AphiaID is present and different from the AphiaID."""
    return "valid_AphiaID" in aphia_info["record"] and aphia_info["record"]["valid_AphiaID"] is not None and aphia_info["record"]["AphiaID"] != aphia_info["record"]["valid_AphiaID"]


def is_accepted(aphia_info: AphiaInfo):
    """Check if the Aphia status is accepted."""
    return aphia_info["record"]["status"] == Status.ACCEPTED.value


def convert_environment(env: int):
    """Convert an environment flag from integer to boolean."""
    if env is None:
        return None
    else:
        return bool(env)


def fetch_aphia(aphiaid, cache: AphiaCacheInterface = None):
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


def detect_lsid(taxa: Dict[str, AphiaInfo]) -> None:
    """Check if scientificNameID is present and parse LSID to Aphia ID."""
    for taxon in taxa.values():
        if taxon.get("scientificNameID") is not None:
            aphiaid = parse_scientificnameid(taxon.get("scientificNameID"))
            if aphiaid is None:
                taxon.set_invalid("scientificNameID")
            else:
                taxon.aphiaid = aphiaid


def detect_external(taxa: Dict[str, AphiaInfo]) -> None:
    """Check if scientificNameID is present and convert external identifier to Aphia ID."""
    for taxon in taxa.values():
        if taxon.get("scientificNameID") is not None and taxon.aphiaid is None:
            identifier = taxon.get("scientificNameID").strip().lower()
            numbers = re.findall(r"\d+", identifier)
            if len(numbers) == 1:
                type = None
                if "tsn" in identifier or "itis" in identifier:
                    type = "tsn"
                elif "ncbi" in identifier:
                    type = "ncbi"
                elif "bold" in identifier:
                    type = "bold"
                if type is not None:
                    match = pyworms.aphiaRecordByExternalID(numbers[0], type)
                    if match is not None:
                        taxon.aphiaid = match["AphiaID"]
                        taxon.set_invalid("scientificNameID", False)
                        taxon.set_flag(Flag.SCIENTIFICNAMEID_EXTERNAL)


def fetch(taxa, cache: AphiaCacheInterface = None):
    """Fetch Aphia info from WoRMS, including alternative."""

    for key, taxon in taxa.items():

        # TODO: fetch all aphia info records including alternatives in one go

        if taxon.aphiaid is not None:
            aphia_info = fetch_aphia(taxon.aphiaid, cache)
            if aphia_info["record"] is None or aphia_info["classification"] is None:
                pass
            else:
                taxon.aphia_info = aphia_info
                if has_alternative(aphia_info):

                    # alternative provided

                    aphia_info_accepted = fetch_aphia(taxon.aphia_info["record"]["valid_AphiaID"], cache)
                    if aphia_info_accepted["record"] is None or aphia_info_accepted["classification"] is None:
                        pass
                    else:
                        taxon.aphia_info_accepted = aphia_info_accepted


get_annotated_list()
