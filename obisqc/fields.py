import logging
logger = logging.getLogger(__name__)


def check_record(record):
    result = {
        "id": record["id"],
        "missing": [],
        "invalid": [],
        "flags": [],
        "annotations": {},
        "dropped": False
    }

    # basisOfRecord

    vocab = ["PreservedSpecimen", "FossilSpecimen", "LivingSpecimen", "MaterialSample", "Event", "HumanObservation", "MachineObservation", "Taxon", "Occurrence"]
    if "basisOfRecord" in record and record["basisOfRecord"] is not None:
        if not record["basisOfRecord"].lower() in [value.lower() for value in vocab]:
            result["invalid"].append("basisOfRecord")
    else:
        result["missing"].append("basisOfRecord")

    return result


def check(records):
    return [check_record(record) for record in records]
