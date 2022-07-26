import logging
from typing import List
from obisqc.model import Record


logger = logging.getLogger(__name__)


def check_record(record: Record) -> None:
    """Check required fields."""

    # basisOfRecord

    vocab = ["PreservedSpecimen", "FossilSpecimen", "LivingSpecimen", "MaterialSample", "Event", "HumanObservation", "MachineObservation", "Taxon", "Occurrence"]

    if record.get("basisOfRecord") is not None:
        if not record.get("basisOfRecord").lower() in [value.lower() for value in vocab]:
            record.set_invalid("basisOfRecord")
    else:
        record.set_missing("basisOfRecord")


def check(records: List[Record]) -> None:
    for record in records:
        check_record(record)
