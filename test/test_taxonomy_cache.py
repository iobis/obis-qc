import unittest
from obisqc import taxonomy
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%H:%M:%S")
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("obisqc.util.aphia").setLevel(logging.INFO)


class DummyCache:
    def store(self, aphiaid, aphia_info):
        pass
    def fetch(self, aphiaid):
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
            { "id": 0, "scientificNameID": "urn:lsid:marinespecies.org:taxname:141433" }
        ]

        results_nocache = taxonomy.check(records)
        self.assertTrue(results_nocache[0]["annotations"]["aphia"] == 141433)
        self.assertFalse(results_nocache[0]["dropped"])
        self.assertNotIn("not_marine", results_nocache[0]["flags"])

        results_cache = taxonomy.check(records, self.cache)
        self.assertTrue(results_cache[0]["annotations"]["aphia"] == 141433)
        self.assertTrue(results_cache[0]["dropped"])
        self.assertIn("not_marine", results_cache[0]["flags"])


if __name__ == "__main__":
    unittest.main()