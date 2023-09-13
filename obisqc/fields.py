import logging
from typing import List
from obisqc.model import Record
from obisqc.util import vocabularies


logger = logging.getLogger(__name__)
vocabs = vocabularies.get_vocabularies()


def check_record(record: Record) -> None:
    """Check required fields."""

    # basisOfRecord

    if record.get("basisOfRecord") is not None:
        if not record.get("basisOfRecord").lower() in [value.lower() for value in vocabs["dwc:basisOfRecord"]]:
            record.set_invalid("basisOfRecord")
    else:
        record.set_missing("basisOfRecord")


def check(records: List[Record]) -> None:
    for record in records:
        check_record(record)
