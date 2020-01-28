import unittest
from obisqc import fields


class TestFields(unittest.TestCase):

    def test_basisofrecord(self):
        records = [
            { "id": 0 },
            { "id": 1, "basisOfRecord": "HumanObservation" },
            { "id": 2, "basisOfRecord": "humanobservation" },
            { "id": 3, "basisOfRecord": "human observation" }
        ]
        results = fields.check(records)
        self.assertIn("basisOfRecord", results[0]["missing"])
        self.assertNotIn("basisOfRecord", results[1]["missing"])
        self.assertNotIn("basisOfRecord", results[2]["missing"])
        self.assertIn("basisOfRecord", results[3]["invalid"])


if __name__ == "__main__":
    unittest.main()