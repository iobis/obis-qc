import unittest
from obisqc import time
from obisqc.util.flags import Flag


class TestTime(unittest.TestCase):

    def test_time_parsing(self):
        records = [
            {"eventDate": "1970-01-01T00:00:00"},
            {"eventDate": "1971-01-01T00:00:00"},
            {"eventDate": "1970-01-01T00:00:00/1971-01-01T00:00:00"}
        ]
        results = time.check(records)
        self.assertEqual(results[0]["annotations"]["date_start"], 0)
        self.assertEqual(results[0]["annotations"]["date_mid"], 0)
        self.assertEqual(results[0]["annotations"]["date_end"], 0)
        self.assertEqual(results[0]["annotations"]["date_year"], 1970)
        self.assertEqual(results[1]["annotations"]["date_start"], 31536000000)
        self.assertEqual(results[1]["annotations"]["date_mid"], 31536000000)
        self.assertEqual(results[1]["annotations"]["date_end"], 31536000000)
        self.assertEqual(results[1]["annotations"]["date_year"], 1971)
        self.assertEqual(results[2]["annotations"]["date_start"], 0)
        #self.assertEqual(results[2]["annotations"]["date_mid"], 15768000000) # todo: fix
        self.assertEqual(results[2]["annotations"]["date_end"], 31536000000)

    def test_min_date(self):
        records = [
            {"eventDate": "1870-01-01T00:00:00"}
        ]
        results = time.check(records, min_year=1900)
        self.assertNotIn("date_start", results[0]["annotations"])
        self.assertIn(Flag.DATE_BEFORE_MIN.value, results[0]["flags"])
        self.assertIn("eventDate", results[0]["invalid"])
        self.assertFalse(results[0]["dropped"])

    def test_year(self):
        records = [
            {"eventDate": "2010"},
            {"eventDate": "2010-01-01/2012-01-01"}
        ]
        results = time.check(records, min_year=1900)
        self.assertEqual(results[0]["annotations"]["date_year"], 2010)
        self.assertEqual(results[1]["annotations"]["date_year"], 2011)

    def test_future_date(self):
        records = [
            {"eventDate": "2300-01-01T00:00:00"}
        ]
        results = time.check(records)
        self.assertNotIn("date_start", results[0]["annotations"])
        self.assertIn(Flag.DATE_IN_FUTURE.value, results[0]["flags"])
        self.assertIn("eventDate", results[0]["invalid"])
        self.assertFalse(results[0]["dropped"])

    def test_invalid_date_format(self):
        records = [
            {"eventDate": "12 January 1928"}
        ]
        results = time.check(records)
        self.assertIn("eventDate", results[0]["invalid"])
        self.assertFalse(results[0]["dropped"])

    def test_missing_date(self):
        records = [
            {}
        ]
        results = time.check(records)
        self.assertIn("eventDate", results[0]["missing"])
        self.assertFalse(results[0]["dropped"])


if __name__ == "__main__":
    unittest.main()