from obisqc import absence
from obisqc import fields
from obisqc import mof_fields
from obisqc import location
from obisqc import taxonomy
from obisqc import time
from obisqc.model import AphiaCacheInterface, Record
from typing import List


def check(records: List[Record], xylookup: bool=False, cache: AphiaCacheInterface=None):
    absence.check(records)
    fields.check(records)
    time.check(records)
    taxonomy.check(records, cache)
    location.check(records, xylookup=xylookup)
