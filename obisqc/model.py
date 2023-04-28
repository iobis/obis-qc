from __future__ import annotations
from typing import Any, Dict, List
from obisqc.util.flags import Flag
import hashlib
import json
from abc import ABC, abstractmethod


RANKS = [
    "superdomain", "domain", "kingdom", "subkingdom", "infrakingdom", "phylum", "phylum (division)", "subphylum",
    "subphylum (subdivision)", "infraphylum", "parvphylum", "gigaclass", "megaclass", "superclass", "class",
    "subclass", "infraclass", "subterclass", "division", "subdivision", "superorder", "order", "suborder",
    "infraorder", "parvorder", "section", "subsection", "superfamily", "family", "subfamily", "supertribe",
    "tribe", "subtribe", "genus", "subgenus", "species", "subspecies", "variety", "subvariety", "forma",
    "subforma"
]
RANK_IDS = [r + "id" for r in RANKS]
TAXONOMY_FIELDS = RANKS + RANK_IDS + ["aphiaid", "unaccepted", "taxonID", "scientificNameID", "acceptedNameUsageID", "parentNameUsageID", "originalNameUsageID", "taxonConceptID", "scientificName", "acceptedNameUsage", "parentNameUsage", "originalNameUsage", "higherClassification", "genericName", "infragenericEpithet", "specificEpithet", "infraspecificEpithet", "cultivarEpithet", "taxonRank", "verbatimTaxonRank", "scientificNameAuthorship", "vernacularName", "nomenclaturalCode", "taxonomicStatus", "nomenclaturalStatus", "marine", "brackish", "redlist_category", "hab", "wrims"]


class Field:

    def __init__(self, value=None, invalid=None, missing=None, **kwargs):
        self.verbatim = value
        self.invalid = invalid
        self.missing = missing

        for k, v in kwargs.items():
            if k == "interpreted":
                self.interpreted = v


class Record:

    def __init__(self, data: Dict = None, **kwargs):
        self.type: str = None
        self.absence: bool = None
        self.dropped: bool = None
        self.fields: Dict[str, Field] = {}
        self.flags: List[Flag] = []
        self.extensions: Dict[str, List[Record]] = {}
        self.extras: Dict[str, Any] = {}

        if data is not None:
            for key, value in data.items():
                self.set(key, value)

        for key, value in kwargs.items():
            self.set(key, value)

    def get(self, field: str):
        return self.fields[field].verbatim if field in self.fields else None

    def set(self, field: str, value) -> None:
        self.fields[field] = Field(value if value != "" else None)

    def get_interpreted(self, field: str):
        return self.fields[field].interpreted if field in self.fields and hasattr(self.fields[field], "interpreted") else None

    def has_interpreted(self, field: str):
        return field in self.fields and hasattr(self.fields[field], "interpreted")

    def set_interpreted(self, field: str, value) -> None:
        if field not in self.fields:
            self.fields[field] = Field(interpreted=value)
        else:
            self.fields[field].interpreted = value

    def is_missing(self, field: str) -> bool:
        return self.fields[field].missing if field in self.fields else False

    def set_missing(self, field: str, value: bool = True) -> None:
        if field not in self.fields:
            self.fields[field] = Field(missing=value)
        else:
            self.fields[field].missing = value

    def is_invalid(self, field: str) -> bool:
        return self.fields[field].invalid

    def set_invalid(self, field: str, value: bool = True):
        if field not in self.fields:
            self.fields[field] = Field(invalid=value)
        else:
            self.fields[field].invalid = value

    def set_flag(self, flag: Flag) -> None:
        if flag not in self.flags:
            self.flags.append(flag)

    def trim_whitespace(self) -> None:
        for field in self.fields:
            if isinstance(self.get(field), str):
                self.set(field, self.get(field).strip())

    def get_taxonomy(self) -> Taxon:
        record = Taxon()
        for field in TAXONOMY_FIELDS:
            record.set(field, self.get(field))
        return record

    def merge_taxonomy(self, other: Taxon) -> None:
        for field in TAXONOMY_FIELDS:
            self.fields[field] = other.fields[field]

    def get_hash(self) -> str:
        record_dict = {field: self.get(field) for field in self.fields}
        dhash = hashlib.md5()
        encoded = json.dumps(record_dict, sort_keys=True).encode()
        dhash.update(encoded)
        return dhash.hexdigest()


class Taxon(Record):

    def __init__(self):
        Record.__init__(self)
        self.aphiaid: int = None
        self.aphia_info: AphiaInfo = None
        self.aphia_info_accepted: AphiaInfo = None


class AphiaInfo:

    def __init__(self, record: Dict = None, classification: Dict = None, bold_id: str = None, ncbi_id: str = None, distribution: Dict = None, redlist_category: str = None, hab: bool = None, wrims: bool = None):
        self.record = record
        self.classification = classification
        self.bold_id = bold_id
        self.ncbi_id = ncbi_id
        self.distribution = self.distribution
        self.redlist_category = self.redlist_category
        self.hab = self.hab
        self.wrims = self.wrims


class AphiaCacheInterface(ABC):

    @abstractmethod
    def store(self, aphia_info: AphiaInfo) -> None:
        pass

    @abstractmethod
    def fetch(self, aphia_id) -> AphiaInfo:
        pass

    @abstractmethod
    def match_name(self, name: str) -> int:
        pass
