from typing import Dict, List
from obisqc.model import Record, RANKS, RANK_IDS
from obisqc.util.aphia import match_worms, match_obis, check_annotated_list, fetch, detect_lsid, detect_external
import logging
from obisqc.model import AphiaCacheInterface, AphiaInfo, Taxon
from obisqc.util.flags import Flag
from obisqc.util.aphia import is_accepted, convert_environment


logger = logging.getLogger(__name__)


def check_fields(taxa: Dict[str, AphiaInfo]) -> None:
    """Check if taxonomy related fields are present."""
    for key, taxon in taxa.items():
        if taxon.get("scientificName") is None:
            taxon.set_missing("scientificName")
        if taxon.get("scientificNameID") is None:
            taxon.set_missing("scientificNameID")


def check_taxa(taxa: Dict[str, AphiaInfo], cache: AphiaCacheInterface = None) -> None:
    """Run all steps for taxonomic quality control."""

    check_fields(taxa)
    detect_lsid(taxa)
    detect_external(taxa)
    match_obis(taxa, cache)
    match_worms(taxa)
    check_annotated_list(taxa)
    fetch(taxa, cache)


def check(records: List[Record], cache: AphiaCacheInterface = None) -> None:

    # first map all input rows to sets of taxonomic information

    taxa: Dict[str, Taxon] = {}
    indexes: Dict[str, List[str]] = {}

    for index, record in enumerate(records):
        record.trim_whitespace()
        taxonomy = record.get_taxonomy()
        hash = taxonomy.get_hash()
        if hash in indexes:
            indexes[hash].append(index)
        else:
            taxa[hash] = taxonomy
            indexes[hash] = [index]

    # submit all sets of taxonomic information to the aphia component

    logger.debug("Checking %s names" % (len(taxa.keys())))
    check_taxa(taxa, cache)

    # process aphia results

    for hash, taxon in taxa.items():

        if taxon.aphia_info is None:
            taxon.set_flag(Flag.NO_MATCH)
            taxon.dropped = True
            if taxon.get("scientificNameID") is not None:
                taxon.set_invalid("scientificNameID")

        else:

            master_aphia_info = None
            taxon.dropped = False

            if not is_accepted(taxon.aphia_info):
                if taxon.aphia_info_accepted is not None:
                    taxon.set_interpreted("unaccepted", int(taxon.aphia_info["record"]["AphiaID"]))
                    master_aphia_info = taxon.aphia_info_accepted
                else:
                    taxon.set_flag(Flag.NO_ACCEPTED_NAME)
                    taxon.set_interpreted("unaccepted", None)
                    master_aphia_info = taxon.aphia_info
            else:
                taxon.set_interpreted("unaccepted", None)
                master_aphia_info = taxon.aphia_info

            # populate other fields

            taxon.set_interpreted("scientificName", master_aphia_info["record"]["scientificname"])
            taxon.set_interpreted("aphiaid", int(master_aphia_info["record"]["AphiaID"]))
            taxon.set_interpreted("marine", convert_environment(master_aphia_info["record"]["isMarine"]))
            taxon.set_interpreted("brackish", convert_environment(master_aphia_info["record"]["isBrackish"]))
            taxon.set_interpreted("terrestrial", convert_environment(master_aphia_info["record"]["isTerrestrial"]))

            if "hab" in master_aphia_info:
                taxon.set_interpreted("hab", master_aphia_info["hab"])
            if "wrims" in master_aphia_info:
                taxon.set_interpreted("wrims", master_aphia_info["wrims"])
            if "redlist_category" in master_aphia_info:
                taxon.set_interpreted("redlist_category", master_aphia_info["redlist_category"])

            for rank in RANKS:
                if rank in master_aphia_info["classification"]:
                    taxon.set_interpreted(rank, master_aphia_info["classification"][rank])
            for rank_id in RANK_IDS:
                if rank_id in master_aphia_info["classification"]:
                    taxon.set_interpreted(rank_id, master_aphia_info["classification"][rank_id])

            # derive marine flag

            if taxon.get_interpreted("marine") is False and taxon.get_interpreted("brackish") is False:
                taxon.set_flag(Flag.NOT_MARINE)
                taxon.dropped = True
            elif taxon.get_interpreted("marine") is not True and taxon.get_interpreted("brackish") is not True:
                taxon.set_flag(Flag.MARINE_UNSURE)

    # merge results back into records

    for hash, taxon in taxa.items():

        for index in indexes[hash]:

            if taxon.dropped:
                records[index].dropped = True
            records[index].flags.extend(taxon.flags)
            records[index].merge_taxonomy(taxon)
