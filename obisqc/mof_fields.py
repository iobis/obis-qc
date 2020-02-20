import logging
logger = logging.getLogger(__name__)


def check_record(record):
    """Check required fields."""

    result = {
        "id": record["id"],
        "missing": [],
        "invalid": [],
        "flags": [],
        "annotations": {},
        "dropped": False
    }

    # measurementType

    if "measurementType" not in record or record["measurementType"] is None or str(record["measurementType"]) == "":
        result["missing"].append("measurementType")

    if "measurementTypeID" not in record or record["measurementTypeID"] is None or str(record["measurementTypeID"]) == "":
        result["missing"].append("measurementTypeID")

    return result


def check(records):
    return [check_record(record) for record in records]
