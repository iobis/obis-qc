from typing import Dict
import pyworms
import logging
import requests
from obisqc.model import AphiaInfo
from obisqc.util.flags import Flag
from obisqc.util.status import Status
import re
from math import ceil
import sqlite3
import json
import os


logger = logging.getLogger(__name__)
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
        m = re.search("^http[s]?://www\.marinespecies\.org/aphia\.php\?p=taxdetails&id=([0-9]+)$", input)
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
    logger.info("Checking annotated list")

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


def match_with_sqlite(names: list[str]):
    import gnparser

    logger.info(f"Matching names against sqlite {os.getenv('WORMS_DB_PATH')}")

    # get all canonical names and authorships

    parsed_names = []

    for name in names:
        parsed_str = gnparser.parse_to_string(name, "compact", None, 1, 1)
        parsed = json.loads(parsed_str)
        if parsed.get("parsed"):
            canonical = parsed.get("canonical", None).get("full", None)
            authorship = parsed.get("authorship", {}).get("normalized", None)
            parsed_names.append((canonical, authorship))
        else:
            parsed_names.append((None, None))

    logger.info(f"Parsed {len(parsed_names)} names")

    # fetch all matches by canonical name

    logger.info(f"Connecting to sqlite {os.getenv('WORMS_DB_PATH')}")
    con = sqlite3.connect(os.getenv("WORMS_DB_PATH"))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    logger.info(f"Connected to sqlite {os.getenv('WORMS_DB_PATH')}")

    canonicals = list(set([name[0] for name in parsed_names if name[0] is not None]))
    placeholders = ",".join("?" * len(canonicals))
    
    logger.info(f"Checking {len(canonicals)} canonical names")
    
    cur.execute(f"select * from parsed where canonical in ({placeholders})", canonicals)
    matches = cur.fetchall()
    logger.info(f"Found {len(matches)} matches")
    canonicals_map = {}
    for row in matches:
        canonical = row["canonical"]
        if canonical not in canonicals_map:
            canonicals_map[canonical] = []
        canonicals_map[canonical].append({
            "aphiaid": row["aphiaid"],
            "scientificname": row["canonical"],
            "authorship": row["authorship"],
        })

    con.close()

    # get all matches by canonical name and authorship

    results = []

    for name_pair in parsed_names:
        canonical = name_pair[0]
        authorship = name_pair[1]
        if canonical is not None:
            if canonical in canonicals_map:
                matches = canonicals_map[canonical]
                if authorship is not None:
                    matches = [match for match in matches if match["authorship"] == authorship]
            else:
                matches = []
        else:
            matches = []
        results.append(matches)

    return results


def match_worms(taxa: Dict[str, AphiaInfo]):
    """Try to match any records that have a scientificName but no LSID."""

    # gather all keys and names that need matching (no LSID, not in matching cache)

    allkeys = taxa.keys()
    names = []
    keys = []
    for key in allkeys:
        if taxa[key].aphiaid is None and taxa[key].get("scientificName") is not None:
            name = taxa[key].get("scientificName")
            keys.append(key)
            names.append(name)

    # sanitize

    names = [sanitize_name(name) for name in names]

    # do matching

    if len(names) > 0:

        matches = match_with_sqlite(names)

        assert (len(matches) == len(names))
        for i in range(0, len(matches)):
            name_matches = matches[i]
            if name_matches is not None and len(name_matches) == 1:
                taxa[keys[i]].aphiaid = int(name_matches[0]["aphiaid"])
            else:
                taxa[keys[i]].aphiaid = None


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


def fetch_aphia(aphiaid):
    """Fetch the Aphia record an AphiaID."""

    con = sqlite3.connect(os.getenv("WORMS_DB_PATH"))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from parsed where aphiaid = ?", (aphiaid,))
    res = cur.fetchone()
    con.close()
    if res is None:
        return {"record": None}
    record = json.loads(res["record"])

    aphia_info = {
        "record": record,
        "bold_id": res["bold_id"],
        "ncbi_id": res["ncbi_id"]
    }
    return aphia_info


def detect_lsid(taxa: Dict[str, AphiaInfo]) -> None:
    """Check if scientificNameID is present and parse LSID to Aphia ID."""
    logger.info("Detecting LSIDs")
    for taxon in taxa.values():
        if taxon.get("scientificNameID") is not None:
            aphiaid = parse_scientificnameid(taxon.get("scientificNameID"))
            if aphiaid is None:
                taxon.set_invalid("scientificNameID")
            else:
                taxon.aphiaid = aphiaid


def detect_external(taxa: Dict[str, AphiaInfo]) -> None:
    """Check if scientificNameID is present and convert external identifier to Aphia ID."""
    logger.info("Detecting external identifiers")
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


def fetch(taxa):
    """Fetch Aphia info from WoRMS, including alternative."""

    logger.info("Fetching taxonomy info")

    for key, taxon in taxa.items():

        # TODO: fetch all aphia info records including alternatives in one go

        if taxon.aphiaid is not None:
            aphia_info = fetch_aphia(taxon.aphiaid)
            if aphia_info["record"] is None:
                pass
            else:
                taxon.aphia_info = aphia_info
                if has_alternative(aphia_info):

                    # alternative provided

                    aphia_info_accepted = fetch_aphia(taxon.aphia_info["record"]["valid_AphiaID"])
                    if aphia_info_accepted["record"] is None:
                        pass
                    else:
                        taxon.aphia_info_accepted = aphia_info_accepted


get_annotated_list()
