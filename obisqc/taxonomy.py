from obisqc.util import aphia
from obisqc.util.misc import trim_whitespace


def check(records, cache=None):

    # first map all input rows to sets of taxonomic information (scientificName and scientificNameID)

    taxa = {}

    for index, record in enumerate(records):
        record = trim_whitespace(record)
        key = (record["scientificName"] if "scientificName" in record else "") + "::" + (record["scientificNameID"] if "scientificNameID" in record else "")
        if key in taxa:
            taxa[key]["indexes"].append(index)
        else:
            taxa[key] = {
                "indexes": [index],
                "scientificName": record["scientificName"] if "scientificName" in record else None,
                "scientificNameID": record["scientificNameID"] if "scientificNameID" in record else None,
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
