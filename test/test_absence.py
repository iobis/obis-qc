import unittest
from obisqc import absence


class TestAbsence(unittest.TestCase):

    def test_occurrencestatus(self):
        records = [
            {},
            {"occurrenceStatus": "present"},
            {"occurrenceStatus": "Present"},
            {"occurrenceStatus": "absent"},
            {"occurrenceStatus": "is present"}
        ]
        results = absence.check(records)
        self.assertFalse(results[0]["absence"])
        self.assertFalse(results[1]["absence"])
        self.assertFalse(results[2]["absence"])
        self.assertTrue(results[3]["absence"])
        self.assertFalse(results[4]["absence"])
        self.assertIn("occurrenceStatus", results[4]["invalid"])

    def test_individualcount(self):
        records = [
            {},
            {"individualCount": "0"},
            {"individualCount": "0.0"},
            {"individualCount": 0},
            {"individualCount": 0.0},
            {"individualCount": 1}
        ]
        results = absence.check(records)
        self.assertFalse(results[0]["absence"])
        self.assertTrue(results[1]["absence"])
        self.assertTrue(results[2]["absence"])
        self.assertTrue(results[3]["absence"])
        self.assertTrue(results[4]["absence"])
        self.assertFalse(results[5]["absence"])

    def test_individualcount_invalid(self):
        records = [
            {"individualCount": "3 individuals"}
        ]
        results = absence.check(records)
        self.assertFalse(results[0]["absence"])
        self.assertIn("individualCount", results[0]["invalid"])


if __name__ == "__main__":
    unittest.main()