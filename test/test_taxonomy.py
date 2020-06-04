import unittest
from obisqc import taxonomy
import logging
from obisqc.util.flags import Flag

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%H:%M:%S")
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("obisqc.util.aphia").setLevel(logging.INFO)


class TestTaxonomy(unittest.TestCase):

    def test_annotations(self):
        records = [
            { "id": 0, "scientificName": "Brachiolaria" },
            { "id": 1, "scientificName": "Cercocebus sanjei" },
            { "id": 2, "scientificName": "**non-current code** ??" }
        ]
        results = taxonomy.check(records)
        self.assertIn(Flag.WORMS_ANNOTATION_REJECT_GROUPING.value, results[0]["flags"])
        self.assertIn(Flag.WORMS_ANNOTATION_REJECT_HABITAT.value, results[1]["flags"])
        self.assertIn(Flag.WORMS_ANNOTATION_NO_BIOTA.value, results[2]["flags"])

    def test_name_valid(self):
        records = [
            { "id": 0, "scientificName": "Abra alba" }
        ]
        results = taxonomy.check(records)
        self.assertTrue(results[0]["annotations"]["aphia"] == 141433)
        self.assertIsNone(results[0]["annotations"]["unaccepted"])
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn("scientificName", results[0]["missing"])
        self.assertIn("scientificNameID", results[0]["missing"])
        self.assertTrue(len(results[0]["flags"]) == 0)

    def test_name_synonym(self):
        records = [
            { "id": 0, "scientificName": "Orca gladiator" }
        ]
        results = taxonomy.check(records)
        self.assertTrue(results[0]["annotations"]["aphia"] == 137102)
        self.assertTrue(results[0]["annotations"]["unaccepted"] == 384046)
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn("scientificName", results[0]["missing"])
        self.assertIn("scientificNameID", results[0]["missing"])
        self.assertTrue(len(results[0]["flags"]) == 0)

    def test_id_valid(self):
        records = [
            { "id": 0, "scientificNameID": "urn:lsid:marinespecies.org:taxname:141433" }
        ]
        results = taxonomy.check(records)
        self.assertTrue(results[0]["annotations"]["aphia"] == 141433)
        self.assertIsNone(results[0]["annotations"]["unaccepted"])
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn("scientificNameID", results[0]["missing"])
        self.assertIn("scientificName", results[0]["missing"])
        self.assertTrue(len(results[0]["flags"]) == 0)

    def test_id_synonym(self):
        records = [
            { "id": 0, "scientificNameID": "urn:lsid:marinespecies.org:taxname:384046" }
        ]
        results = taxonomy.check(records)
        self.assertTrue(results[0]["annotations"]["aphia"] == 137102)
        self.assertTrue(results[0]["annotations"]["unaccepted"] == 384046)
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn("scientificNameID", results[0]["missing"])
        self.assertIn("scientificName", results[0]["missing"])
        self.assertTrue(len(results[0]["flags"]) == 0)

    def test_name_invalid(self):
        records = [
            { "id": 0, "scientificName": "Bivalve" }
        ]
        results = taxonomy.check(records)
        self.assertIn("scientificNameID", results[0]["missing"])
        self.assertNotIn("scientificName", results[0]["missing"])
        self.assertTrue(results[0]["dropped"])
        self.assertIn(Flag.NO_MATCH.value, results[0]["flags"])
        self.assertIsNone(results[0]["annotations"]["aphia"])
        self.assertIsNone(results[0]["annotations"]["unaccepted"])

    def test_id_invalid(self):
        records = [
            { "id": 0, "scientificNameID": "urn:lsid:itis.gov:itis_tsn:28726" }
        ]
        results = taxonomy.check(records)
        self.assertNotIn("scientificNameID", results[0]["missing"])
        self.assertIn("scientificName", results[0]["missing"])
        self.assertTrue(results[0]["dropped"])
        self.assertIn(Flag.NO_MATCH.value, results[0]["flags"])
        self.assertIn("scientificNameID", results[0]["invalid"])
        self.assertTrue(len(results[0]["invalid"]) == 1)
        self.assertIsNone(results[0]["annotations"]["aphia"])
        self.assertIsNone(results[0]["annotations"]["unaccepted"])

    def test_id_non_existing(self):
        records = [
            { "id": 0, "scientificNameID": "urn:lsid:marinespecies.org:taxname:99999999" }
        ]
        results = taxonomy.check(records)
        self.assertNotIn("scientificNameID", results[0]["missing"])
        self.assertIn("scientificName", results[0]["missing"])
        self.assertTrue(results[0]["dropped"])
        self.assertIn(Flag.NO_MATCH.value, results[0]["flags"])
        self.assertIn("scientificNameID", results[0]["invalid"])
        self.assertIsNone(results[0]["annotations"]["aphia"])
        self.assertIsNone(results[0]["annotations"]["unaccepted"])

    def test_name_not_marine(self):
        records = [
            { "id": 0, "scientificName": "Ardea cinerea" }
        ]
        results = taxonomy.check(records)
        self.assertIn("scientificNameID", results[0]["missing"])
        self.assertNotIn("scientificName", results[0]["missing"])
        self.assertTrue(results[0]["dropped"])
        self.assertIn(Flag.NOT_MARINE.value, results[0]["flags"])
        self.assertTrue(results[0]["annotations"]["aphia"] == 212668)
        self.assertIsNone(results[0]["annotations"]["unaccepted"])

    def test_name_synonym_accepted_marine_unsure(self):
        records = [
            { "id": 0, "scientificName": "Brockmanniella brockmannii" }
        ]
        results = taxonomy.check(records)
        self.assertIn("scientificNameID", results[0]["missing"])
        self.assertNotIn("scientificName", results[0]["missing"])
        self.assertFalse(results[0]["dropped"])
        self.assertIn(Flag.MARINE_UNSURE.value, results[0]["flags"])
        self.assertTrue(results[0]["annotations"]["aphia"] == 971564)

    def test_nomen_nudum(self):
        records = [
            { "id": 0, "scientificNameID": "urn:lsid:marinespecies.org:taxname:152230", "scientificName": "Coelenterata tissue" }
        ]
        results = taxonomy.check(records)
        self.assertNotIn("scientificName", results[0]["missing"])
        self.assertNotIn("scientificNameID", results[0]["missing"])
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn(Flag.NO_MATCH.value, results[0]["flags"])
        self.assertIn(Flag.MARINE_UNSURE.value, results[0]["flags"])
        self.assertIn(Flag.NO_ACCEPTED_NAME.value, results[0]["flags"])
        self.assertTrue(results[0]["annotations"]["aphia"] == 152230)

    def test_aphiaid_zero(self):
        records = [
            { "id": 0, "scientificName": "Phytoplankton color", "scientificNameID": "urn:lsid:marinespecies.org:taxname:0" }
        ]
        results = taxonomy.check(records)
        self.assertNotIn("scientificName", results[0]["missing"])
        self.assertNotIn("scientificNameID", results[0]["missing"])
        self.assertTrue(results[0]["dropped"])
        self.assertIn(Flag.NO_MATCH.value, results[0]["flags"])

    def test_paraphyletic(self):
        records = [
            { "id": 0, "scientificNameID": "urn:lsid:marinespecies.org:taxname:794", "scientificName": "Turbellaria" }
        ]
        results = taxonomy.check(records)
        self.assertNotIn("scientificName", results[0]["missing"])
        self.assertNotIn("scientificNameID", results[0]["missing"])
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn(Flag.NO_MATCH.value, results[0]["flags"])
        self.assertIn(Flag.NO_ACCEPTED_NAME.value, results[0]["flags"])
        self.assertNotIn(Flag.MARINE_UNSURE.value, results[0]["flags"])
        self.assertTrue(results[0]["annotations"]["aphia"] == 794)

    def test_uncertain(self):
        records = [
            { "id": 0, "scientificNameID": "urn:lsid:marinespecies.org:taxname:835694", "scientificName": "Operculodinium centrocarpum" }
        ]
        results = taxonomy.check(records)
        self.assertNotIn("scientificName", results[0]["missing"])
        self.assertNotIn("scientificNameID", results[0]["missing"])
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn(Flag.NO_MATCH.value, results[0]["flags"])
        self.assertIn(Flag.NO_ACCEPTED_NAME.value, results[0]["flags"])
        self.assertIn(Flag.MARINE_UNSURE.value, results[0]["flags"])
        self.assertTrue(results[0]["annotations"]["aphia"] == 835694)

    def test_uncertain_2(self):
        records = [
            { "id": 0, "scientificName": "Dactyliosolen flexuosus" }
        ]
        results = taxonomy.check(records)
        self.assertNotIn("scientificName", results[0]["missing"])
        self.assertIn("scientificNameID", results[0]["missing"])
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn(Flag.NO_MATCH.value, results[0]["flags"])
        self.assertIn(Flag.NO_ACCEPTED_NAME.value, results[0]["flags"])
        self.assertNotIn(Flag.MARINE_UNSURE.value, results[0]["flags"])
        self.assertTrue(results[0]["annotations"]["aphia"] == 637279)

    def test_unaccepted(self):
        records = [
            { "id": 0, "scientificName": "Dactyliosolen flexuosus" }
        ]
        results = taxonomy.check(records)
        self.assertNotIn("scientificName", results[0]["missing"])
        self.assertIn("scientificNameID", results[0]["missing"])
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn(Flag.NO_MATCH.value, results[0]["flags"])
        self.assertIn(Flag.NO_ACCEPTED_NAME.value, results[0]["flags"])
        self.assertNotIn(Flag.MARINE_UNSURE.value, results[0]["flags"])
        self.assertTrue(results[0]["annotations"]["aphia"] == 637279)

    def test_nomen_dubium(self):
        records = [
            { "id": 0, "scientificNameID": "urn:lsid:marinespecies.org:taxname:130270", "scientificName": "Magelona minuta" }
        ]
        results = taxonomy.check(records)
        self.assertNotIn("scientificName", results[0]["missing"])
        self.assertNotIn("scientificNameID", results[0]["missing"])
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn(Flag.NO_MATCH.value, results[0]["flags"])
        self.assertIn(Flag.NO_ACCEPTED_NAME.value, results[0]["flags"])
        self.assertNotIn(Flag.MARINE_UNSURE.value, results[0]["flags"])
        self.assertTrue(results[0]["annotations"]["aphia"] == 130270)

    def test_taxon_inquirendum(self):
        records = [
            { "id": 0, "scientificNameID": "urn:lsid:marinespecies.org:taxname:133144" }
        ]
        results = taxonomy.check(records)
        self.assertNotIn("scientificNameID", results[0]["missing"])
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn(Flag.NO_MATCH.value, results[0]["flags"])
        self.assertIn(Flag.NO_ACCEPTED_NAME.value, results[0]["flags"])
        self.assertTrue(results[0]["annotations"]["aphia"] == 133144)

    def test_interim_unpublished(self):
        records = [
            { "id": 0, "scientificNameID": "urn:lsid:marinespecies.org:taxname:1057043" }
        ]
        results = taxonomy.check(records)
        self.assertNotIn("scientificNameID", results[0]["missing"])
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn(Flag.NO_MATCH.value, results[0]["flags"])
        self.assertIn(Flag.NO_ACCEPTED_NAME.value, results[0]["flags"])
        self.assertTrue(results[0]["annotations"]["aphia"] == 1057043)

    def test_interim_quarantined(self):
        records = [
            { "id": 0, "scientificNameID": "urn:lsid:marinespecies.org:taxname:493822" }
        ]
        results = taxonomy.check(records)
        self.assertNotIn("scientificNameID", results[0]["missing"])
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn(Flag.NO_MATCH.value, results[0]["flags"])
        self.assertIn(Flag.NO_ACCEPTED_NAME.value, results[0]["flags"])
        self.assertTrue(results[0]["annotations"]["aphia"] == 493822)

    def test_interim_deleted(self):
        records = [
            { "id": 0, "scientificNameID": "urn:lsid:marinespecies.org:taxname:22747" }
        ]
        results = taxonomy.check(records)
        self.assertNotIn("scientificNameID", results[0]["missing"])
        self.assertFalse(results[0]["dropped"])
        self.assertNotIn(Flag.NO_MATCH.value, results[0]["flags"])
        self.assertIn(Flag.NO_ACCEPTED_NAME.value, results[0]["flags"])
        self.assertTrue(results[0]["annotations"]["aphia"] == 22747)


if __name__ == "__main__":
    unittest.main()