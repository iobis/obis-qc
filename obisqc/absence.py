from isodateparser import ISODateParser
import datetime
import logging
logger = logging.getLogger(__name__)


def check_record(record):
    result = {
        "id": record["id"],
        "missing": [],
        "invalid": [],
        "flags": [],
        "annotations": {},
        "dropped": False,
        "absence": False
    }

    # occurrenceStatus

    if "occurrenceStatus" in record and record["occurrenceStatus"] is not None:
        if record["occurrenceStatus"].lower() == "absent":
            result["absence"] = True
        elif record["occurrenceStatus"].lower() != "present":
            result["invalid"].append("occurrenceStatus")
    else:
        result["missing"].append("occurrenceStatus")

    # individualCount

    if "individualCount" in record and record["individualCount"] is not None:
        try:
            value = float(record["individualCount"])
            if value == 0:
                result["absence"] = True
        except ValueError:
            pass

    return result


def check(records):
    return [check_record(record) for record in records]
