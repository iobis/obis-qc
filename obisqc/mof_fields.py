import logging
from obisqc.model import Record
from typing import List


logger = logging.getLogger(__name__)


def check_record(record: Record) -> None:
    """Check required fields."""

    if record.get("measurementType") is None:
        record.set_missing("measurementType")

    if record.get("measurementTypeID") is None:
        record.set_missing("measurementTypeID")


def check(records: List[Record]) -> None:
    for record in records:
        check_record(record)
