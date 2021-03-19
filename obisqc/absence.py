from obisqc.util import misc
import logging
logger = logging.getLogger(__name__)


def check_record(record):
    """Check is a record is an absence record."""

    result = {
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
        count_check = misc.check_float(record["individualCount"])
        if not count_check["valid"]:
            result["invalid"].append("individualCount")
        else:
            value = float(record["individualCount"])
            if value == 0:
                result["absence"] = True

    return result


def check(records):
    return [check_record(record) for record in records]
