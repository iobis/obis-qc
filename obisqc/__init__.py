from obisqc import absence
from obisqc import fields
from obisqc import location
from obisqc import taxonomy
from obisqc import time
from obisqc.model import Record
from typing import List


def check(records: List[Record], xylookup: bool=False):
    absence.check(records)
    fields.check(records)
    time.check(records)
    taxonomy.check(records)
    location.check(records, xylookup=xylookup)
