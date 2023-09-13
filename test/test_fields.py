import unittest
from obisqc import fields
from obisqc.model import Record


class TestFields(unittest.TestCase):

    def test_basisofrecord(self):
        records = [
            Record(),
            Record(basisOfRecord="HumanObservation"),
            Record(basisOfRecord="humanobservation"),
            Record(basisOfRecord="human observation"),
            Record(basisOfRecord="MaterialCitation")
        ]
        fields.check(records)
        self.assertTrue(records[0].is_missing("basisOfRecord"))
        self.assertFalse(records[1].is_missing("basisOfRecord"))
        self.assertFalse(records[2].is_missing("basisOfRecord"))
        self.assertTrue(records[3].is_invalid("basisOfRecord"))
        self.assertFalse(records[4].is_invalid("basisOfRecord"))


if __name__ == "__main__":
    unittest.main()
