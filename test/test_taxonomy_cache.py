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
                    "isMarine": True,
                    "isBrackish": True,
                    "isFreshwater": None,
                    "isTerrestrial": None
                },
                "classification": {}
            }
        elif str(aphiaid) == "160528":
            return {
                "record": {
                    "AphiaID": 160528,
                    "scientificname": "Pseudo-nitzschia pungens",
                    "status": "accepted",
                    "isMarine": True,
                    "isBrackish": True,
                    "isFreshwater": None,
                    "isTerrestrial": None
                },
                "classification": {},
                "hab": True,
                "wrims": True
            }

    def match_name(self, name) -> int:
        if name == "Abra alba":
            return 141433


class TestTaxonomyCache(unittest.TestCase):

    def setUp(self):
        self.cache = DummyCache()

    def test_hab_wrims(self):
        records = [
            Record(data={"scientificName": "Pseudo-nitzschia pungens"}),
        ]
        taxonomy.check(records, self.cache)
        self.assertTrue(records[0].get_interpreted("hab"))
        self.assertTrue(records[0].get_interpreted("wrims"))

    def test_cache(self):
        records = [
            Record(scientificNameID="urn:lsid:marinespecies.org:taxname:141433")
        ]
        taxonomy.check(records, self.cache)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 141433)
        self.assertFalse(records[0].dropped)
        self.assertNotIn(Flag.NOT_MARINE, records[0].flags)

    def test_match(self):
        records = [
            Record(scientificName="Abra alba")
        ]
        taxonomy.check(records, self.cache)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 141433)
        self.assertFalse(records[0].dropped)
        self.assertNotIn(Flag.NOT_MARINE, records[0].flags)

    def test_no_cache(self):
        records = [
            Record(scientificNameID="urn:lsid:marinespecies.org:taxname:141433")
        ]
        taxonomy.check(records)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 141433)
        self.assertFalse(records[0].dropped)
        self.assertNotIn(Flag.NOT_MARINE, records[0].flags)


if __name__ == "__main__":
    unittest.main()
