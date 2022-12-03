import unittest
import logging
from obisqc.util.flags import Flag
from obisqc.model import Record
from obisqc import check


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%H:%M:%S")
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("obisqc.util.aphia").setLevel(logging.INFO)


class TestCombined(unittest.TestCase):

    def test(self):
        records = [
            Record(occurrenceStatus="absent", scientificName="Vinundu guellemei", decimalLongitude=7.3, decimalLatitude=50.3, eventDate="1970-01-01T00:00:00")
        ]
        check(records, xylookup=True)
        self.assertTrue(records[0].absence)
        self.assertTrue(records[0].dropped)
        self.assertIn(Flag.WORMS_ANNOTATION_RESOLVABLE, records[0].flags)
        self.assertIn(Flag.NOT_MARINE, records[0].flags)
        self.assertIn(Flag.ON_LAND, records[0].flags)


if __name__ == "__main__":
    unittest.main()
