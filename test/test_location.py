import unittest
from obisqc import location
from obisqc.util.flags import Flag
from obisqc.model import Record


class TestLocation(unittest.TestCase):

    def test_location_parsing(self):
        records = [
            Record(decimalLongitude="2.1", decimalLatitude="51.3"),
            Record(decimalLongitude=2.1, decimalLatitude=51.3)
        ]
        location.check(records)
        self.assertEqual(records[0].get_interpreted("decimalLongitude"), 2.1)
        self.assertEqual(records[0].get_interpreted("decimalLatitude"), 51.3)
        self.assertNotIn(Flag.NO_COORD, records[0].flags)
        self.assertFalse(records[0].dropped)
        self.assertEqual(records[1].get_interpreted("decimalLongitude"), 2.1)
        self.assertEqual(records[1].get_interpreted("decimalLatitude"), 51.3)
        self.assertNotIn(Flag.NO_COORD, records[1].flags)
        self.assertFalse(records[1].dropped)

    def test_missing_coordinates(self):
        records = [
            Record(decimalLatitude=51.3),
            Record(decimalLongitude=2.1),
            Record()
        ]
        location.check(records)
        self.assertEqual(records[0].get_interpreted("decimalLatitude"), 51.3)
        self.assertTrue(records[0].is_missing("decimalLongitude"))
        self.assertIn(Flag.NO_COORD, records[0].flags)
        self.assertTrue(records[0].dropped)
        self.assertEqual(records[1].get_interpreted("decimalLongitude"), 2.1)
        self.assertIn(Flag.NO_COORD, records[1].flags)
        self.assertTrue(records[1].dropped)
        self.assertTrue(records[1].is_missing("decimalLatitude"))
        self.assertIn(Flag.NO_COORD, records[2].flags)
        self.assertTrue(records[2].dropped)
        self.assertTrue(records[2].is_missing("decimalLongitude"))
        self.assertTrue(records[2].is_missing("decimalLatitude"))

    def test_invalid_coordinates(self):
        records = [
            Record(decimalLongitude=2.1, decimalLatitude="abc")
        ]
        location.check(records)
        self.assertEqual(records[0].get_interpreted("decimalLongitude"), 2.1)
        self.assertTrue(records[0].is_invalid("decimalLatitude"))
        self.assertIn(Flag.NO_COORD, records[0].flags)
        self.assertTrue(records[0].dropped)

    def test_coordinates_out_of_range(self):
        records = [
            Record(decimalLongitude=-200, decimalLatitude=100)
        ]
        location.check(records)
        self.assertTrue(records[0].get_interpreted("decimalLongitude") is None)
        self.assertTrue(records[0].get_interpreted("decimalLatitude") is None)
        self.assertTrue(records[0].is_invalid("decimalLongitude"))
        self.assertTrue(records[0].is_invalid("decimalLatitude"))
        self.assertIn(Flag.NO_COORD, records[0].flags)
        self.assertIn(Flag.LON_OUT_OF_RANGE, records[0].flags)
        self.assertIn(Flag.LAT_OUT_OF_RANGE, records[0].flags)
        self.assertTrue(records[0].dropped)

    def test_zero_coordinates(self):
        records = [
            Record(decimalLongitude=0, decimalLatitude=0),
            Record(decimalLongitude=1, decimalLatitude=0)
        ]
        location.check(records)
        self.assertIn(Flag.ZERO_COORD, records[0].flags)
        self.assertNotIn(Flag.ZERO_COORD, records[1].flags)

    def test_uncertainty(self):
        records = [
            Record(coordinateUncertaintyInMeters=100, decimalLongitude=1, decimalLatitude=0),
            Record(decimalLongitude=1, decimalLatitude=0)
        ]
        location.check(records)
        self.assertFalse(records[0].is_missing("coordinateUncertaintyInMeters"))
        self.assertTrue(records[0].get_interpreted("coordinateUncertaintyInMeters") == 100)
        self.assertTrue(records[1].is_missing("coordinateUncertaintyInMeters"))

    def test_depth_parsing(self):
        records = [
            Record(minimumDepthInMeters="2", maximumDepthInMeters="10"),
            Record(minimumDepthInMeters=2, maximumDepthInMeters=10)
        ]
        location.check(records)
        self.assertEqual(records[0].get_interpreted("minimumDepthInMeters"), 2)
        self.assertEqual(records[0].get_interpreted("maximumDepthInMeters"), 10)
        self.assertNotIn(Flag.NO_DEPTH, records[0].flags)
        self.assertEqual(records[1].get_interpreted("minimumDepthInMeters"), 2)
        self.assertEqual(records[1].get_interpreted("maximumDepthInMeters"), 10)
        self.assertNotIn(Flag.NO_DEPTH, records[1].flags)

    def test_depth_calculation(self):
        records = [
            Record(minimumDepthInMeters=2, maximumDepthInMeters=10),
            Record(minimumDepthInMeters=2)
        ]
        location.check(records)
        self.assertEqual(records[0].get_interpreted("depth"), 6)
        self.assertEqual(records[1].get_interpreted("depth"), 2)

    def test_depth_exceeds_bath(self):
        records = [
            Record(decimalLongitude=2.1, decimalLatitude=51.3, minimumDepthInMeters=1000),
            Record(decimalLongitude=2.1, decimalLatitude=51.3, minimumDepthInMeters=10),
            Record(decimalLongitude=2.1, decimalLatitude=51.3, minimumDepthInMeters=10, maximumDepthInMeters=1000),
            Record(decimalLongitude=2.1, decimalLatitude=51.3, minimumDepthInMeters=-10)
        ]
        location.check(records, xylookup=True)
        self.assertEqual(records[0].get_interpreted("minimumDepthInMeters"), 1000)
        self.assertNotIn(Flag.NO_DEPTH, records[0].flags)
        self.assertIn(Flag.DEPTH_EXCEEDS_BATH, records[0].flags)
        self.assertEqual(records[1].get_interpreted("minimumDepthInMeters"), 10)
        self.assertNotIn(Flag.NO_DEPTH, records[1].flags)
        self.assertNotIn(Flag.DEPTH_EXCEEDS_BATH, records[1].flags)
        self.assertEqual(records[2].get_interpreted("minimumDepthInMeters"), 10)
        self.assertNotIn(Flag.NO_DEPTH, records[2].flags)
        self.assertIn(Flag.DEPTH_EXCEEDS_BATH, records[2].flags)
        self.assertEqual(records[3].get_interpreted("minimumDepthInMeters"), -10)
        self.assertNotIn(Flag.NO_DEPTH, records[3].flags)
        self.assertNotIn(Flag.DEPTH_EXCEEDS_BATH, records[3].flags)

    def test_depth_min_max(self):
        records = [
            Record(minimumDepthInMeters=10, maximumDepthInMeters=2)
        ]
        location.check(records)
        self.assertEqual(records[0].get_interpreted("minimumDepthInMeters"), 10)
        self.assertEqual(records[0].get_interpreted("maximumDepthInMeters"), 2)
        self.assertNotIn(Flag.NO_DEPTH, records[0].flags)
        self.assertIn(Flag.MIN_DEPTH_EXCEEDS_MAX, records[0].flags)

    def test_depth_out_of_range(self):
        records = [
            Record(minimumDepthInMeters=12000, maximumDepthInMeters=12000)
        ]
        location.check(records)
        self.assertTrue(records[0].get_interpreted("minimumDepthInMeters") is None)
        self.assertTrue(records[0].get_interpreted("maximumDepthInMeters") is None)
        self.assertIn(Flag.NO_DEPTH, records[0].flags)
        self.assertIn(Flag.DEPTH_OUT_OF_RANGE, records[0].flags)
        self.assertIn(Flag.DEPTH_OUT_OF_RANGE, records[0].flags)
        self.assertTrue(records[0].is_invalid("minimumDepthInMeters"))
        self.assertTrue(records[0].is_invalid("maximumDepthInMeters"))

    def test_depth_out_of_range_invalid(self):
        records = [
            Record(minimumDepthInMeters="NA")
        ]
        location.check(records)
        self.assertTrue(records[0].get_interpreted("minimumDepthInMeters") is None)
        self.assertIn(Flag.NO_DEPTH, records[0].flags)
        self.assertNotIn(Flag.DEPTH_OUT_OF_RANGE, records[0].flags)
        self.assertTrue(records[0].is_invalid("minimumDepthInMeters"))

    def test_shoredistance(self):
        records = [
            Record(decimalLongitude=2.1, decimalLatitude=51.3),
            Record(decimalLongitude=7.3, decimalLatitude=50.3)
        ]
        location.check(records, xylookup=True)
        self.assertTrue(records[0].get_interpreted("shoredistance") is not None)
        self.assertTrue(records[0].get_interpreted("shoredistance") > 0)
        self.assertTrue(records[1].get_interpreted("shoredistance") is not None)
        self.assertTrue(records[1].get_interpreted("shoredistance") < 0)
        self.assertIn(Flag.ON_LAND, records[1].flags)

    def test_areas(self):
        records = [
            Record(decimalLongitude=2.1, decimalLatitude=51.3),
            Record(decimalLongitude=7.3, decimalLatitude=50.3)
        ]
        location.check(records, xylookup=True)
        self.assertTrue(len(records[0].get_interpreted("areas")) > 0)
        self.assertTrue(len(records[1].get_interpreted("areas")) == 0)

    def test_grids(self):
        records = [
            Record(decimalLongitude=2.1, decimalLatitude=51.3)
        ]
        location.check(records, xylookup=True)
        self.assertTrue(records[0].get_interpreted("bathymetry") is not None)
        self.assertTrue(records[0].get_interpreted("sst") is not None)
        self.assertTrue(records[0].get_interpreted("sss") is not None)


if __name__ == "__main__":
    unittest.main()