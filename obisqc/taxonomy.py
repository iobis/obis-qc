from obisqc.util import aphia
from obisqc.util.misc import trim_whitespace
import logging

logger = logging.getLogger(__name__)


def check(records, cache=None):

    # first map all input rows to sets of taxonomic information

    taxa = {}

    for index, record in enumerate(records):
        record = trim_whitespace(record)
        parts = [
            record["scientificName"] if "scientificName" in record and record["scientificName"] is not None else "",
            record["scientificNameID"] if "scientificNameID" in record and record["scientificNameID"] is not None else "",
            record["phylum"] if "phylum" in record and record["phylum"] is not None else "",
            record["class"] if "class" in record and record["class"] is not None else "",
            record["order"] if "order" in record and record["order"] is not None else "",
            record["family"] if "family" in record and record["family"] is not None else "",
            record["genus"] if "genus" in record and record["genus"] is not None else ""
        ]
        key = "|".join(parts)
        if key in taxa:
            taxa[key]["indexes"].append(index)
        else:
            taxa[key] = {
                "indexes": [index],
                "scientificName": record["scientificName"] if "scientificName" in record else None,
                "scientificNameID": record["scientificNameID"] if "scientificNameID" in record else None,
                "phylum": record["phylum"] if "phylum" in record else None,
                "class": record["class"] if "class" in record else None,
                "order": record["order"] if "order" in record else None,
                "family": record["family"] if "family" in record else None,
                "genus": record["genus"] if "genus" in record else None,
                "aphiaid": None,
                "missing": [],
                "invalid": [],
                "flags": [],
                "aphia": None,
                "unaccepted": None,
                "dropped": False,
                "aphia_info": None,
                "aphia_info_accepted": None,
                "marine": None,
                "brackish": None
            }

    # submit all sets of taxonomic information to the aphia component

    logger.debug("Checking %s names" % (len(taxa.keys())))
    aphia.check(taxa, cache)

    # map back to qc results structure

    results = [None] * len(records)

    for key, taxon in taxa.items():
        for index in taxon["indexes"]:
            results[index] = {
                "missing": taxon["missing"],
                "invalid": taxon["invalid"],
                "flags": taxon["flags"],
                "annotations": {
                    "aphia": taxon["aphia"],
                    "unaccepted": taxon["unaccepted"],
                    "marine": taxon["marine"],
                    "brackish": taxon["brackish"]
                },
                "dropped": taxon["dropped"]
            }

    return results
