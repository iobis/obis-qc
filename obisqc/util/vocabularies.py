import requests
import io
import xmltodict
import logging
from functools import lru_cache


logger = logging.getLogger(__name__)


@lru_cache
def get_vocabularies() -> dict:
    vocabularies = {}

    vocabulary_definitions = {
        "dwc:basisOfRecord": "https://rs.gbif.org/vocabulary/dwc/basis_of_record_2022-02-02.xml"
    }

    for field, url in vocabulary_definitions.items():
        logger.info(f"Fetching vocabulary for {field}")
        res = requests.get(url, timeout=10, verify=False)
        content = io.BytesIO(res.content)
        document = xmltodict.parse(content)
        values = [item["@dc:identifier"] for item in document["thesaurus"]["concept"]]
        vocabularies[field] = values

    return vocabularies
