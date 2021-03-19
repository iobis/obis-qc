import unittest
from obisqc import mof_fields


class TestMofFields(unittest.TestCase):

    def test_measurementtype(self):
        records = [
            {},
            {"measurementType": "biomass"},
            {"measurementTypeID": "http://vocab.nerc.ac.uk/collection/P01/current/OWETBM01"}
        ]
        results = mof_fields.check(records)
        self.assertIn("measurementType", results[0]["missing"])
        self.assertIn("measurementTypeID", results[0]["missing"])
        self.assertNotIn("measurementType", results[1]["missing"])
        self.assertIn("measurementTypeID", results[1]["missing"])
        self.assertIn("measurementType", results[2]["missing"])
        self.assertNotIn("measurementTypeID", results[2]["missing"])


if __name__ == "__main__":
    unittest.main()