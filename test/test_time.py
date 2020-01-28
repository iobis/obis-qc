import unittest
from obisqc import time


class TestTime(unittest.TestCase):

    def test_time_parsing(self):
        records = [
            { "id": 1, "eventDate": "1970-01-01T00:00:00" },
            { "id": 2, "eventDate": "1971-01-01T00:00:00" },
            { "id": 3, "eventDate": "1970-01-01T00:00:00/1971-01-01T00:00:00" }
        ]
        results = time.check(records)
        self.assertEqual(results[0]["annotations"]["date_start"], 0)
        self.assertEqual(results[0]["annotations"]["date_mid"], 0)
        self.assertEqual(results[0]["annotations"]["date_end"], 0)
        self.assertEqual(results[1]["annotations"]["date_start"], 31536000000)
        self.assertEqual(results[1]["annotations"]["date_mid"], 31536000000)
        self.assertEqual(results[1]["annotations"]["date_end"], 31536000000)
        self.assertEqual(results[2]["annotations"]["date_start"], 0)
        #self.assertEqual(results[2]["annotations"]["date_mid"], 15768000000)
        self.assertEqual(results[2]["annotations"]["date_end"], 31536000000)

    def test_min_date(self):
        records = [
            { "id": 1, "eventDate": "1870-01-01T00:00:00" }
        ]
        results = time.check(records, min_year=1900)
        self.assertNotIn("date_start", results[0]["annotations"])
        self.assertIn("date_before_min", results[0]["flags"])
        self.assertIn("eventDate", results[0]["invalid"])
        self.assertFalse(results[0]["dropped"])

    def test_future_date(self):
        records = [
            { "id": 1, "eventDate": "2300-01-01T00:00:00" }
        ]
        results = time.check(records)
        self.assertNotIn("date_start", results[0]["annotations"])
        self.assertIn("date_in_future", results[0]["flags"])
        self.assertIn("eventDate", results[0]["invalid"])
        self.assertFalse(results[0]["dropped"])

    def test_invalid_date_format(self):
        records = [
            { "id": 1, "eventDate": "12 January 1928" }
        ]
        results = time.check(records)
        self.assertIn("eventDate", results[0]["invalid"])
        self.assertFalse(results[0]["dropped"])

    def test_missing_date(self):
        records = [
            {"id": 1}
        ]
        results = time.check(records)
        self.assertIn("eventDate", results[0]["missing"])
        self.assertFalse(results[0]["dropped"])


if __name__ == "__main__":
    unittest.main()