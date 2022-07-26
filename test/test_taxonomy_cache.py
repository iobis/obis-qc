from typing import Dict
import unittest
from obisqc import taxonomy
import logging
from obisqc.model import Record
from obisqc.util.flags import Flag

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%H:%M:%S")
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("obisqc.util.aphia").setLevel(logging.INFO)


class DummyCache:
    def store(self, aphiaid: str, aphia_info: Dict) -> None:
        pass

    def fetch(self, aphiaid) -> Dict:
        if str(aphiaid) == "141433":
            return {
                "record": {
                    "AphiaID": 141433,
                    "scientificname": "Abra alba",
                    "status": "accepted",
                    "valid_AphiaID": 141433,
                    "isMarine": False, # modified for testing purposes
                    "isBrackish": False, # modified for testing purposes
                    "isFreshwater": None,
                    "isTerrestrial": None
                },
                "classification": {}
            }


class TestTaxonomyCache(unittest.TestCase):

    def setUp(self):
        self.cache = DummyCache()

    def test_cache(self):
        records = [
            Record(scientificNameID="urn:lsid:marinespecies.org:taxname:141433")
        ]
        taxonomy.check(records)
        self.assertTrue(records[0].get_interpreted("aphia") == 141433)
        self.assertFalse(records[0].dropped)
        self.assertNotIn(Flag.NOT_MARINE, records[0].flags)

    def test_no_cache(self):
        records = [
            Record(scientificNameID="urn:lsid:marinespecies.org:taxname:141433")
        ]
        taxonomy.check(records)
        self.assertTrue(records[0].get_interpreted("aphia") == 141433)
        self.assertFalse(records[0].dropped)
        self.assertNotIn(Flag.NOT_MARINE, records[0].flags)


if __name__ == "__main__":
    unittest.main()
