import unittest
from obisqc import time
from obisqc.util.flags import Flag
from obisqc.model import Record


class TestTime(unittest.TestCase):

    def test_time_parsing(self):
        records = [
            Record(eventDate="1970-01-01T00:00:00"),
            Record(eventDate="1971-01-01T00:00:00"),
            Record(eventDate="1970-01-01T00:00:00/1971-01-01T00:00:00")
        ]
        time.check(records)
        self.assertEqual(records[0].get_interpreted("date_start"), 0)
        self.assertEqual(records[0].get_interpreted("date_mid"), 0)
        self.assertEqual(records[0].get_interpreted("date_end"), 0)
        self.assertEqual(records[0].get_interpreted("date_year"), 1970)
        self.assertEqual(records[1].get_interpreted("date_start"), 31536000000)
        self.assertEqual(records[1].get_interpreted("date_mid"), 31536000000)
        self.assertEqual(records[1].get_interpreted("date_end"), 31536000000)
        self.assertEqual(records[1].get_interpreted("date_year"), 1971)
        self.assertEqual(records[2].get_interpreted("date_start"), 0)
        #self.assertEqual(results[2]["annotations"]["date_mid"], 15768000000) # todo: fix
        self.assertEqual(records[2].get_interpreted("date_end"), 31536000000)

    def test_min_date(self):
        records = [
            Record(eventDate="1870-01-01T00:00:00"),
        ]
        time.check(records, min_year=1900)
        self.assertTrue(records[0].get_interpreted("date_start") is None)
        self.assertTrue(records[0].get_interpreted("date_mid") is None)
        self.assertTrue(records[0].get_interpreted("date_end") is None)
        self.assertIn(Flag.DATE_BEFORE_MIN, records[0].flags)
        self.assertTrue(records[0].is_invalid("eventDate"))
        self.assertFalse(records[0].dropped)

        records = [
            Record(eventDate="0001-04-11"),
        ]
        time.check(records, min_year=1000)
        self.assertTrue(records[0].get_interpreted("date_start") is None)
        self.assertTrue(records[0].get_interpreted("date_mid") is None)
        self.assertTrue(records[0].get_interpreted("date_end") is None)
        self.assertIn(Flag.DATE_BEFORE_MIN, records[0].flags)
        self.assertTrue(records[0].is_invalid("eventDate"))
        self.assertFalse(records[0].dropped)

        records = [
            Record(eventDate="1590-04-11"),
        ]
        time.check(records)
        self.assertTrue(records[0].get_interpreted("date_start") is not None)
        self.assertTrue(records[0].get_interpreted("date_mid") is not None)
        self.assertTrue(records[0].get_interpreted("date_end") is not None)
        self.assertNotIn(Flag.DATE_BEFORE_MIN, records[0].flags)
        self.assertFalse(records[0].is_invalid("eventDate"))
        self.assertFalse(records[0].dropped)

    def test_future_date(self):
        records = [
            Record(eventDate="2300-01-01T00:00:00"),
            Record(eventDate="2006-01-29T11:49:00/2188-09-15T00:50:59")
        ]
        time.check(records)
        self.assertTrue(records[0].get_interpreted("date_start") is None)
        self.assertTrue(records[0].get_interpreted("date_mid") is None)
        self.assertTrue(records[0].get_interpreted("date_end") is None)
        self.assertIn(Flag.DATE_IN_FUTURE, records[0].flags)
        self.assertTrue(records[0].is_invalid("eventDate"))
        self.assertFalse(records[0].dropped)
        self.assertTrue(records[1].get_interpreted("date_start") is None)
        self.assertTrue(records[1].get_interpreted("date_mid") is None)
        self.assertTrue(records[1].get_interpreted("date_end") is None)
        self.assertIn(Flag.DATE_IN_FUTURE, records[1].flags)
        self.assertTrue(records[1].is_invalid("eventDate"))
        self.assertFalse(records[1].dropped)

    def test_year(self):
        records = [
            Record(eventDate="2010"),
            Record(eventDate="2010-01-01/2012-01-01")
        ]
        time.check(records, min_year=1900)
        self.assertEqual(records[0].get_interpreted("date_year"), 2010)
        self.assertEqual(records[1].get_interpreted("date_year"), 2011)

    def test_invalid_date_format(self):
        records = [
            Record(eventDate="12 January 1928")
        ]
        time.check(records)
        self.assertTrue(records[0].is_invalid("eventDate"))
        self.assertFalse(records[0].dropped)

    def test_missing_date(self):
        records = [
            Record()
        ]
        time.check(records)
        self.assertTrue(records[0].is_missing("eventDate"))
        self.assertFalse(records[0].dropped)

    # def test_bc_dates(self):
    #     records = [
    #         Record(eventDate="0000"),
    #         Record(eventDate="-0001-02-03")
    #     ]
    #     time.check(records)
    #     self.assertEqual(records[0].get_interpreted("date_year"), 0)
    #     self.assertEqual(records[1].get_interpreted("date_year"), -1)


if __name__ == "__main__":
    unittest.main()
