from .util import aphia


def check(records):

    # first map all input rows to sets of taxonomic information (scientificName and scientificNameID)

    taxa = {}

    for record in records:
        record_id = record["id"]
        key = (record["scientificName"] if "scientificName" in record else "") + "::" + (record["scientificNameID"] if "scientificNameID" in record else "")
        if key in taxa:
            taxa[key]["ids"].append(record_id)
        else:
            taxa[key] = {
                "ids": [ record_id ],
                "scientificName": record["scientificName"] if "scientificName" in record else None,
                "scientificNameID": record["scientificNameID"] if "scientificNameID" in record else None,
                "lsid": None,
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

    aphia.check(taxa)

    # map back to qc results structure

    results = []

    for key, taxon in taxa.items():
        for record_id in taxon["ids"]:
            results.append({
                "id": record_id,
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
            })

    return results
