from typing import Dict, List
from obisqc.model import Record
from obisqc.util.aphia import match_worms, check_blacklist, fetch, process_info, parse_scientificnameid
from obisqc.util.misc import trim_whitespace
import logging
from obisqc.model import AphiaCacheInterface, AphiaInfo
from obisqc.util.flags import Flag


logger = logging.getLogger(__name__)


def check_fields(taxa: Dict[str: AphiaInfo]) -> None:
    """Check if taxonomy related fields are present."""
    for key, taxon in taxa.items():
        if taxon.record.get("scientificName") is None:
            taxon.record.set_missing("scientificName")
        if taxon.record.get("scientificNameID") is None:
            taxon.record.set_missing("scientificNameID")


def detect_lsid(taxa: Dict[str: AphiaInfo]) -> None:
    """Check if scientificNameID is present and parse LSID to Aphia ID."""
    for taxon in taxa.values():
        if taxon.record.get("scientificNameID") is not None:
            aphiaid = parse_scientificnameid(taxon.record.get("scientificNameID"))
            if aphiaid is None:
                taxon.record.set_invalid("scientificNameID")
            else:
                taxon.record.set_interpreted("aphiaid", aphiaid)


def check(taxa: Dict[str: AphiaInfo], cache: AphiaCacheInterface=None) -> None:
    """Run all steps for taxonomic quality control."""

    check_fields(taxa)
    detect_lsid(taxa)
    match_worms(taxa, cache)
    check_blacklist(taxa)
    fetch(taxa, cache)
    process_info(taxa)


def check(records: List[Record], cache=None) -> None:

    # first map all input rows to sets of taxonomic information

    taxa = {}

    for index, record in enumerate(records):
        record.trim_whitespace()
        taxonomy = record.get_taxonomy()
        hash = taxonomy["hash"]
        if hash in taxa:
            taxa[hash]["indexes"].append(index)
        else:
            taxa[hash] = taxonomy
            taxa[hash]["indexes"] = [index]
            taxa[hash]["record"] = Record()

    # submit all sets of taxonomic information to the aphia component

    logger.debug("Checking %s names" % (len(taxa.keys())))
    aphia.check(taxa, cache)
