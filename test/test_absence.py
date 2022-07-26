import unittest
from obisqc import absence
from obisqc.model import Record


class TestAbsence(unittest.TestCase):

    def test_occurrencestatus(self):
        records = [
            Record(),
            Record(occurrenceStatus="present"),
            Record(occurrenceStatus="Present"),
            Record(occurrenceStatus="absent"),
            Record(occurrenceStatus="is present")
        ]
        absence.check(records)
        self.assertFalse(records[0].absence)
        self.assertFalse(records[1].absence)
        self.assertFalse(records[2].absence)
        self.assertTrue(records[3].absence)
        self.assertFalse(records[4].absence)
        self.assertTrue(records[4].is_invalid("occurrenceStatus"))

    def test_individualcount(self):
        records = [
            Record(),
            Record(individualCount="0"),
            Record(individualCount="0.0"),
            Record(individualCount=0),
            Record(individualCount=0.0),
            Record(individualCount=1)
        ]
        absence.check(records)
        self.assertFalse(records[0].absence)
        self.assertTrue(records[1].absence)
        self.assertTrue(records[2].absence)
        self.assertTrue(records[3].absence)
        self.assertTrue(records[4].absence)
        self.assertFalse(records[5].absence)

    def test_individualcount_invalid(self):
        records = [
            Record(individualCount="3 individuals")
        ]
        absence.check(records)
        self.assertFalse(records[0].absence)
        self.assertTrue(records[0].is_invalid("individualCount"))


if __name__ == "__main__":
    unittest.main()