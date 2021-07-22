import unittest
from obisqc.util import aphia
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%H:%M:%S")
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("obisqc.util.aphia").setLevel(logging.INFO)


class TestUtil(unittest.TestCase):

    def test_parse_scientificnameid(self):

        id = aphia.parse_scientificnameid("12345")
        self.assertIsNone(id)

        id = aphia.parse_scientificnameid(None)
        self.assertIsNone(id)

        id = aphia.parse_scientificnameid("urn:lsid:marinespecies.org:taxname:")
        self.assertIsNone(id)

        id = aphia.parse_scientificnameid("urn:lsid:marinespecies.org:taxname:|urn:lsid:marinespecies.org:taxname:153087")
        self.assertIsNone(id)

        id = aphia.parse_scientificnameid("http://www.marinespecies.org/aphia.php?p=taxdetails&id=123456")
        self.assertEquals(id, "123456")

        id = aphia.parse_scientificnameid("https://www.marinespecies.org/aphia.php?p=taxdetails&id=123456")
        self.assertEquals(id, "123456")

        id = aphia.parse_scientificnameid("urn:lsid:marinespecies.org:taxname:123456")
        self.assertEquals(id, "123456")


if __name__ == "__main__":
    unittest.main()
