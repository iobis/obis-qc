import unittest
from obisqc import fields


class TestFields(unittest.TestCase):

    def test_basisofrecord(self):
        records = [
            {},
            {"basisOfRecord": "HumanObservation"},
            {"basisOfRecord": "humanobservation"},
            {"basisOfRecord": "human observation"}
        ]
        results = fields.check(records)
        self.assertIn("basisOfRecord", results[0]["missing"])
        self.assertNotIn("basisOfRecord", results[1]["missing"])
        self.assertNotIn("basisOfRecord", results[2]["missing"])
        self.assertIn("basisOfRecord", results[3]["invalid"])


if __name__ == "__main__":
    unittest.main()