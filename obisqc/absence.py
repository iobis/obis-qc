from typing import List
from obisqc.model import Record
from obisqc.util import misc
import logging


logger = logging.getLogger(__name__)

ABSENT_VALUES = {"absent", "notdetected"}
PRESENT_VALUES = {"present", "detected"}


def check_record(record: Record) -> None:
    """Check is a record is an absence record."""

    record.absence = False

    # individualCount

    if record.get("individualCount") is not None:
        count_check = misc.check_float(record.get("individualCount"))
        if not count_check["valid"]:
            record.set_invalid("individualCount")
        else:
            if count_check["float"] == 0:
                record.absence = True

    # occurrenceStatus

    if record.get("occurrenceStatus") is not None:
        status = record.get("occurrenceStatus").lower()
        if status in ABSENT_VALUES:
            record.absence = True
        elif status in PRESENT_VALUES:
            if record.absence:
                # individualCount is 0 but occurrenceStatus indicates presence
                record.set_invalid("occurrenceStatus")
        else:
            record.set_invalid("occurrenceStatus")
    else:
        record.set_missing("occurrenceStatus")


def check(records: List[Record]):
    for record in records:
        check_record(record)
