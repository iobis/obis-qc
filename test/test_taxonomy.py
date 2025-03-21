import unittest
from obisqc import taxonomy
import logging
from obisqc.util.flags import Flag
from obisqc.model import Record


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%H:%M:%S")
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("obisqc.util.aphia").setLevel(logging.INFO)


class TestTaxonomy(unittest.TestCase):

    def test_sqlite(self): 
        records = [
            Record(data={"scientificName": "Abra alba"}),
            Record(data={"scientificName": "Abra alba (W. Wood 1802)"}),
            Record(data={"scientificName": "Abra alba W. Wood 1802"}),
            Record(data={"scientificName": "Abra (Abra) Lamarck, 1818"}),
            Record(data={"scientificName": "Abra Lamarck, 1818"}),
            Record(data={"scientificName": "Abra alva"}),
            Record(data={"scientificName": "Larus dominicanus dominicanus"}),
            Record(data={"scientificName": "Skeletonema menzellii"}),
            Record(data={"scientificName": "Paridotea munda"}),
            Record(data={"scientificName": "Paridotea munda Hale, 1924"}),
            Record(data={"scientificName": "Paridotea munda Nunomura, 1988"}),
            Record(data={"scientificName": "Ulva lactuca"})
        ]
        taxonomy.check(records)
        self.assertNotIn(Flag.NO_MATCH, records[0].flags)
        self.assertNotIn(Flag.NO_MATCH, records[1].flags)
        self.assertIn(Flag.NO_MATCH, records[2].flags)
        self.assertNotIn(Flag.NO_MATCH, records[3].flags)
        self.assertNotIn(Flag.NO_MATCH, records[4].flags)
        self.assertIn(Flag.NO_MATCH, records[5].flags)
        self.assertIn(Flag.NO_MATCH, records[6].flags)
        self.assertIn(Flag.NO_MATCH, records[7].flags)
        self.assertIn(Flag.NO_MATCH, records[8].flags)
        self.assertNotIn(Flag.NO_MATCH, records[9].flags)
        self.assertNotIn(Flag.NO_MATCH, records[10].flags)
        self.assertNotIn(Flag.NO_MATCH, records[11].flags)

    def test_sqlite_dev(self):
        records = [
            Record(scientificName = "Punctum minutissimum"),
            Record(scientificName = "Helicodiscus parallelus")
        ]
        taxonomy.check(records)
        self.assertNotIn(Flag.NO_MATCH, records[0].flags)
        self.assertNotIn(Flag.NO_MATCH, records[1].flags)

    def test_parallel(self):
        records = [
            Record(data={"scientificName": "Abra1 alba"}),
            Record(data={"scientificName": "Abra2 alba"}),
            Record(data={"scientificName": "Abra3 alba"}),
            Record(data={"scientificName": "Abra alba"})
        ]
        taxonomy.check(records)
        self.assertIn(Flag.NO_MATCH, records[0].flags)
        self.assertIn(Flag.NO_MATCH, records[1].flags)
        self.assertIn(Flag.NO_MATCH, records[2].flags)
        self.assertNotIn(Flag.NO_MATCH, records[3].flags)

    def test_annotations(self):
        records = [
            Record(data={"scientificName": "NA", "scientificNameID": "NA", "phylum": "Ciliophora", "class": "Ciliatea", "order": "NA", "family": "NA", "genus": "NA"}),
            Record(data={"scientificName": "**non-current code** Antennarius sp.", "scientificNameID": None, "phylum": "Chordata", "class": "Actinopterygii", "order": "Lophiiformes", "family": "Antennariidae", "genus": "Antennarius"}),
            Record(data={"scientificName": "Vinundu guellemei", "scientificNameID": None, "phylum": None, "class": None, "order": None, "family": None, "genus": None}),
            Record(scientificName="unknown fish [, 1998]")
        ]
        taxonomy.check(records)
        self.assertIn(Flag.WORMS_ANNOTATION_UNRESOLVABLE, records[0].flags)
        self.assertIsNone(records[0].get_interpreted("aphiaid"))
        self.assertIn(Flag.WORMS_ANNOTATION_REJECT_AMBIGUOUS, records[1].flags)
        self.assertIsNone(records[1].get_interpreted("aphiaid"))
        self.assertIn(Flag.WORMS_ANNOTATION_RESOLVABLE, records[2].flags)
        self.assertEqual(records[2].get_interpreted("aphiaid"), 1060834)
        self.assertIn(Flag.WORMS_ANNOTATION_RESOLVABLE_LOSS, records[3].flags)
        self.assertEqual(records[3].get_interpreted("aphiaid"), 11676)

    def test_annotations_resolvable(self):
        records = [
            Record(data={"scientificName": "Hyalinia crystallina Muller, 1774", "phylum": "Mollusca", "class": "Gastropoda Cuvier, 1797", "order": "Stylommatophora", "family": "Zonitidae Mörch, 1864", "genus": "Hyalinia Agassiz, 1837"})
        ]
        taxonomy.check(records)
        self.assertIn(Flag.WORMS_ANNOTATION_RESOLVABLE, records[0].flags)
        self.assertIsNotNone(records[0].get_interpreted("aphiaid"))

    def test_name_valid(self):
        records = [
            Record(scientificName="Abra alba")
        ]
        taxonomy.check(records)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 141433)
        self.assertIsNone(records[0].get_interpreted("unaccepted"))
        self.assertFalse(records[0].dropped)
        self.assertFalse(records[0].is_missing("scientificName"))
        self.assertTrue(records[0].is_missing("scientificNameID"))
        self.assertTrue(len(records[0].flags) == 0)

    def test_external(self):
        records = [
            Record(scientificNameID="ncbi:399303"),
            Record(scientificNameID="ITIS:TSN:81306"),
            Record(scientificNameID="BOLD:642814")
        ]
        taxonomy.check(records)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 141433)
        self.assertFalse(records[0].dropped)
        self.assertFalse(records[0].is_invalid("scientificNameID"))
        self.assertFalse(records[0].is_missing("scientificNameID"))
        self.assertTrue(records[1].get_interpreted("aphiaid") == 141433)
        self.assertFalse(records[1].dropped)
        self.assertFalse(records[1].is_invalid("scientificNameID"))
        self.assertFalse(records[1].is_missing("scientificNameID"))
        self.assertTrue(records[2].get_interpreted("aphiaid") == 141433)
        self.assertFalse(records[2].dropped)
        self.assertFalse(records[2].is_invalid("scientificNameID"))
        self.assertFalse(records[2].is_missing("scientificNameID"))

    def test_name_synonym(self):
        records = [
            Record(scientificName="Orca gladiator")
        ]
        taxonomy.check(records)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 137102)
        self.assertTrue(records[0].get_interpreted("unaccepted") == 384046)
        self.assertFalse(records[0].dropped)
        self.assertFalse(records[0].is_missing("scientificName"))
        self.assertTrue(records[0].is_missing("scientificNameID"))
        self.assertTrue(len(records[0].flags) == 0)

    def test_id_valid(self):
        records = [
            Record(scientificNameID="urn:lsid:marinespecies.org:taxname:141433")
        ]
        taxonomy.check(records)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 141433)
        self.assertIsNone(records[0].get_interpreted("unaccepted"))
        self.assertFalse(records[0].dropped)
        self.assertFalse(records[0].is_missing("scientificNameID"))
        self.assertTrue(records[0].is_missing("scientificName"))
        self.assertTrue(len(records[0].flags) == 0)

    def test_id_synonym(self):
        records = [
            Record(scientificNameID="urn:lsid:marinespecies.org:taxname:384046")
        ]
        taxonomy.check(records)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 137102)
        self.assertTrue(records[0].get_interpreted("unaccepted") == 384046)
        self.assertFalse(records[0].dropped)
        self.assertFalse(records[0].is_missing("scientificNameID"))
        self.assertTrue(records[0].is_missing("scientificName"))
        self.assertTrue(len(records[0].flags) == 0)

    def test_name_invalid(self):
        records = [
            Record(scientificName="Bivalve")
        ]
        taxonomy.check(records)
        self.assertTrue(records[0].is_missing("scientificNameID"))
        self.assertFalse(records[0].is_missing("scientificName"))
        self.assertTrue(records[0].dropped)
        self.assertIn(Flag.NO_MATCH, records[0].flags)
        self.assertIsNone(records[0].get_interpreted("aphiaid"))
        self.assertIsNone(records[0].get_interpreted("unaccepted"))

    def test_id_invalid(self):
        records = [
            Record(scientificNameID="urn:lsid:itis.gov:itis_tsn:28726")
        ]
        taxonomy.check(records)
        self.assertFalse(records[0].is_missing("scientificNameID"))
        self.assertTrue(records[0].is_missing("scientificName"))
        self.assertTrue(records[0].dropped)
        self.assertIn(Flag.NO_MATCH, records[0].flags)
        self.assertTrue(records[0].is_invalid("scientificNameID"))
        self.assertIsNone(records[0].get_interpreted("aphiaid"))
        self.assertIsNone(records[0].get_interpreted("unaccepted"))

    def test_id_non_existing(self):
        records = [
            Record(scientificNameID="urn:lsid:marinespecies.org:taxname:99999999")
        ]
        taxonomy.check(records)
        self.assertFalse(records[0].is_missing("scientificNameID"))
        self.assertTrue(records[0].is_missing("scientificName"))
        self.assertTrue(records[0].dropped)
        self.assertIn(Flag.NO_MATCH, records[0].flags)
        self.assertTrue(records[0].is_invalid("scientificNameID"))
        self.assertIsNone(records[0].get_interpreted("aphiaid"))
        self.assertIsNone(records[0].get_interpreted("unaccepted"))

    def test_name_not_marine(self):
        records = [
            Record(scientificName="Ardea cinerea")
        ]
        taxonomy.check(records)
        self.assertTrue(records[0].is_missing("scientificNameID"))
        self.assertFalse(records[0].is_missing("scientificName"))
        self.assertTrue(records[0].dropped)
        self.assertIn(Flag.NOT_MARINE, records[0].flags)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 212668)
        self.assertFalse(records[0].get_interpreted("marine"))
        self.assertFalse(records[0].get_interpreted("brackish"))
        self.assertIsNone(records[0].get_interpreted("unaccepted"))

    def test_name_synonym_accepted_marine_unsure(self):
        records = [
            Record(scientificName="Brockmanniella brockmannii")
        ]
        taxonomy.check(records)
        self.assertTrue(records[0].is_missing("scientificNameID"))
        self.assertFalse(records[0].is_missing("scientificName"))
        self.assertFalse(records[0].dropped)
        self.assertIn(Flag.MARINE_UNSURE, records[0].flags)
        self.assertIsNone(records[0].get_interpreted("marine"))
        self.assertIsNone(records[0].get_interpreted("brackish"))
        self.assertTrue(records[0].get_interpreted("aphiaid") == 971564)

    def test_nomen_nudum(self):
        records = [
            Record(scientificNameID="urn:lsid:marinespecies.org:taxname:152230", scientificName="Coelenterata tissue")
        ]
        taxonomy.check(records)
        self.assertFalse(records[0].is_missing("scientificName"))
        self.assertFalse(records[0].is_missing("scientificNameID"))
        self.assertFalse(records[0].dropped)
        self.assertNotIn(Flag.NO_MATCH, records[0].flags)
        self.assertIn(Flag.MARINE_UNSURE, records[0].flags)
        self.assertIn(Flag.NO_ACCEPTED_NAME, records[0].flags)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 152230)

    def test_aphiaid_zero(self):
        records = [
            Record(scientificName="Phytoplankton color", scientificNameID="urn:lsid:marinespecies.org:taxname:0")
        ]
        taxonomy.check(records)
        self.assertFalse(records[0].is_missing("scientificName"))
        self.assertFalse(records[0].is_missing("scientificNameID"))
        self.assertTrue(records[0].dropped)
        self.assertIn(Flag.NO_MATCH, records[0].flags)

    def test_paraphyletic(self):
        records = [
            Record(scientificNameID="urn:lsid:marinespecies.org:taxname:794", scientificName="Turbellaria")
        ]
        taxonomy.check(records)
        self.assertFalse(records[0].is_missing("scientificName"))
        self.assertFalse(records[0].is_missing("scientificNameID"))
        self.assertFalse(records[0].dropped)
        self.assertNotIn(Flag.NO_MATCH, records[0].flags)
        self.assertIn(Flag.NO_ACCEPTED_NAME, records[0].flags)
        self.assertNotIn(Flag.MARINE_UNSURE, records[0].flags)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 794)

    # def test_uncertain(self):
    #     records = [
    #         Record(scientificNameID="urn:lsid:marinespecies.org:taxname:835694", scientificName="Operculodinium centrocarpum")
    #     ]
    #     taxonomy.check(records)
    #     self.assertFalse(records[0].is_missing("scientificName"))
    #     self.assertFalse(records[0].is_missing("scientificNameID"))
    #     self.assertFalse(records[0].dropped)
    #     self.assertNotIn(Flag.NO_MATCH, records[0].flags)
    #     self.assertIn(Flag.NO_ACCEPTED_NAME, records[0].flags)
    #     self.assertIn(Flag.MARINE_UNSURE, records[0].flags)
    #     self.assertTrue(records[0].get_interpreted("aphiaid") == 835694)

    def test_uncertain_2(self):
        records = [
            Record(scientificName="Dactyliosolen flexuosus")
        ]
        taxonomy.check(records)
        self.assertFalse(records[0].is_missing("scientificName"))
        self.assertTrue(records[0].is_missing("scientificNameID"))
        self.assertFalse(records[0].dropped)
        self.assertNotIn(Flag.NO_MATCH, records[0].flags)
        self.assertIn(Flag.NO_ACCEPTED_NAME, records[0].flags)
        self.assertNotIn(Flag.MARINE_UNSURE, records[0].flags)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 637279)

    def test_unaccepted(self):
        records = [
            Record(scientificName="Dactyliosolen flexuosus")
        ]
        taxonomy.check(records)
        self.assertFalse(records[0].is_missing("scientificName"))
        self.assertTrue(records[0].is_missing("scientificNameID"))
        self.assertFalse(records[0].dropped)
        self.assertNotIn(Flag.NO_MATCH, records[0].flags)
        self.assertIn(Flag.NO_ACCEPTED_NAME, records[0].flags)
        self.assertNotIn(Flag.MARINE_UNSURE, records[0].flags)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 637279)

    # def test_nomen_dubium(self):
    #     records = [
    #         Record(scientificNameID="urn:lsid:marinespecies.org:taxname:130270", scientificName="Magelona minuta")
    #     ]
    #     taxonomy.check(records)
    #     self.assertFalse(records[0].is_missing("scientificName"))
    #     self.assertFalse(records[0].is_missing("scientificNameID"))
    #     self.assertFalse(records[0].dropped)
    #     self.assertNotIn(Flag.NO_MATCH, records[0].flags)
    #     self.assertIn(Flag.NO_ACCEPTED_NAME, records[0].flags)
    #     self.assertNotIn(Flag.MARINE_UNSURE, records[0].flags)
    #     self.assertTrue(records[0].get_interpreted("aphiaid") == 130270)

    def test_taxon_inquirendum(self):
        records = [
            Record(scientificNameID="urn:lsid:marinespecies.org:taxname:133144")
        ]
        taxonomy.check(records)
        self.assertFalse(records[0].is_missing("scientificNameID"))
        self.assertFalse(records[0].dropped)
        self.assertNotIn(Flag.NO_MATCH, records[0].flags)
        self.assertIn(Flag.NO_ACCEPTED_NAME, records[0].flags)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 133144)

    # def test_interim_unpublished(self):
    #     records = [
    #         Record(scientificNameID="urn:lsid:marinespecies.org:taxname:1057043")
    #     ]
    #     taxonomy.check(records)
    #     self.assertFalse(records[0].is_missing("scientificNameID"))
    #     self.assertFalse(records[0].dropped)
    #     self.assertNotIn(Flag.NO_MATCH, records[0].flags)
    #     self.assertIn(Flag.NO_ACCEPTED_NAME, records[0].flags)
    #     self.assertTrue(records[0].get_interpreted("aphiaid") == 1057043)

    # def test_interim_quarantined(self):
    #     records = [
    #         Record(scientificNameID="urn:lsid:marinespecies.org:taxname:493822")
    #     ]
    #     taxonomy.check(records)
    #     self.assertFalse(records[0].is_missing("scientificNameID"))
    #     self.assertFalse(records[0].dropped)
    #     self.assertNotIn(Flag.NO_MATCH, records[0].flags)
    #     self.assertIn(Flag.NO_ACCEPTED_NAME, records[0].flags)
    #     self.assertTrue(records[0].get_interpreted("aphiaid") == 493822)

    # def test_interim_deleted(self):
    #     records = [
    #         Record(scientificNameID="urn:lsid:marinespecies.org:taxname:22747")
    #     ]
    #     taxonomy.check(records)
    #     self.assertFalse(records[0].is_missing("scientificNameID"))
    #     self.assertFalse(records[0].dropped)
    #     self.assertNotIn(Flag.NO_MATCH, records[0].flags)
    #     self.assertIn(Flag.NO_ACCEPTED_NAME, records[0].flags)
    #     self.assertTrue(records[0].get_interpreted("aphiaid") == 22747)

    def test_whitespace(self):
        records = [
            Record(scientificName="Illex illecebrosus", scientificNameID="urn:lsid:marinespecies.org:taxname:153087 ")
        ]
        taxonomy.check(records)
        self.assertFalse(records[0].is_missing("scientificNameID"))
        self.assertFalse(records[0].dropped)
        self.assertNotIn(Flag.NO_MATCH, records[0].flags)
        self.assertNotIn(Flag.NO_ACCEPTED_NAME, records[0].flags)
        self.assertTrue(records[0].get_interpreted("aphiaid") == 153087)


if __name__ == "__main__":
    unittest.main()
