import unittest
from obisqc import absence


class TestAbsence(unittest.TestCase):

    def test_occurrencestatus(self):
        records = [
            { "id": 0 },
            { "id": 1, "occurrenceStatus": "present" },
            { "id": 2, "occurrenceStatus": "Present" },
            { "id": 3, "occurrenceStatus": "absent" },
            { "id": 4, "occurrenceStatus": "is present"}
        ]
        results = absence.check(records)
        self.assertFalse(results[0]["absence"])
        self.assertFalse(results[1]["absence"])
        self.assertFalse(results[2]["absence"])
        self.assertTrue(results[3]["absence"])
        self.assertFalse(results[4]["absence"])
        self.assertIn("occurrenceStatus", results[4]["invalid"])


if __name__ == "__main__":
    unittest.main()