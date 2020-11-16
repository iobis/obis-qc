import unittest
from obisqc import location
from obisqc.util.flags import Flag


class TestLocation(unittest.TestCase):

    def test_location_parsing(self):
        records = [
            { "id": 0, "decimalLongitude": "2.1", "decimalLatitude": "51.3" },
            { "id": 1, "decimalLongitude": 2.1, "decimalLatitude": 51.3 }
        ]
        results = location.check(records)
        self.assertEqual(results[0]["annotations"]["decimalLongitude"], 2.1)
        self.assertEqual(results[0]["annotations"]["decimalLatitude"], 51.3)
        self.assertNotIn(Flag.NO_COORD.value, results[0]["flags"])
        self.assertFalse(results[0]["dropped"])
        self.assertEqual(results[1]["annotations"]["decimalLongitude"], 2.1)
        self.assertEqual(results[1]["annotations"]["decimalLatitude"], 51.3)
        self.assertNotIn(Flag.NO_COORD.value, results[1]["flags"])
        self.assertFalse(results[1]["dropped"])

    def test_missing_coordinates(self):
        records = [
            { "id": 0, "decimalLatitude": 51.3 },
            { "id": 1, "decimalLongitude": 2.1 },
            { "id": 2 }
        ]
        results = location.check(records)
        self.assertEqual(results[0]["annotations"]["decimalLatitude"], 51.3)
        self.assertIn("decimalLongitude", results[0]["missing"])
        self.assertIn(Flag.NO_COORD.value, results[0]["flags"])
        self.assertTrue(results[0]["dropped"])
        self.assertEqual(results[1]["annotations"]["decimalLongitude"], 2.1)
        self.assertIn(Flag.NO_COORD.value, results[1]["flags"])
        self.assertTrue(results[1]["dropped"])
        self.assertIn("decimalLatitude", results[1]["missing"])
        self.assertIn(Flag.NO_COORD.value, results[2]["flags"])
        self.assertTrue(results[2]["dropped"])
        self.assertIn("decimalLongitude", results[2]["missing"])
        self.assertIn("decimalLatitude", results[2]["missing"])

    def test_invalid_coordinates(self):
        records = [
            { "id": 0, "decimalLongitude": 2.1, "decimalLatitude": "abc" }
        ]
        results = location.check(records)
        self.assertEqual(results[0]["annotations"]["decimalLongitude"], 2.1)
        self.assertIn("decimalLatitude", results[0]["invalid"])
        self.assertIn(Flag.NO_COORD.value, results[0]["flags"])
        self.assertTrue(results[0]["dropped"])

    def test_coordinates_out_of_range(self):
        records = [
            { "id": 0, "decimalLongitude": -200, "decimalLatitude": 100 }
        ]
        results = location.check(records)
        self.assertNotIn("decimalLongitude", results[0]["annotations"])
        self.assertNotIn("decimalLatitude", results[0]["annotations"])
        self.assertIn("decimalLongitude", results[0]["invalid"])
        self.assertIn("decimalLatitude", results[0]["invalid"])
        self.assertIn(Flag.NO_COORD.value, results[0]["flags"])
        self.assertIn(Flag.LON_OUT_OF_RANGE.value, results[0]["flags"])
        self.assertIn(Flag.LAT_OUT_OF_RANGE.value, results[0]["flags"])
        self.assertTrue(results[0]["dropped"])

    def test_zero_coordinates(self):
        records = [
            { "id": 0, "decimalLongitude": 0, "decimalLatitude": 0 },
            { "id": 1, "decimalLongitude": 1, "decimalLatitude": 0 }
        ]
        results = location.check(records)
        self.assertIn(Flag.ZERO_COORD.value, results[0]["flags"])
        self.assertNotIn(Flag.ZERO_COORD.value, results[1]["flags"])

    def test_uncertainty(self):
        records = [
            { "id": 0, "coordinateUncertaintyInMeters": 100, "decimalLongitude": 1, "decimalLatitude": 0 },
            { "id": 1, "decimalLongitude": 1, "decimalLatitude": 0 }
        ]
        results = location.check(records)
        self.assertNotIn("coordinateUncertaintyInMeters", results[0]["missing"])
        self.assertTrue(results[0]["annotations"]["coordinateUncertaintyInMeters"] == 100)
        self.assertIn("coordinateUncertaintyInMeters", results[1]["missing"])

    def test_depth_parsing(self):
        records = [
            { "id": 0, "minimumDepthInMeters": "2", "maximumDepthInMeters": "10" },
            { "id": 1, "minimumDepthInMeters": 2, "maximumDepthInMeters": 10 }
        ]
        results = location.check(records)
        self.assertEqual(results[0]["annotations"]["minimumDepthInMeters"], 2)
        self.assertEqual(results[0]["annotations"]["maximumDepthInMeters"], 10)
        self.assertNotIn(Flag.NO_DEPTH.value, results[0]["flags"])
        self.assertEqual(results[1]["annotations"]["minimumDepthInMeters"], 2)
        self.assertEqual(results[1]["annotations"]["maximumDepthInMeters"], 10)
        self.assertNotIn(Flag.NO_DEPTH.value, results[1]["flags"])

    def test_depth_exceeds_bath(self):
        records = [
            { "id": 0, "decimalLongitude": 2.1, "decimalLatitude": 51.3, "minimumDepthInMeters": 1000 },
            { "id": 1, "decimalLongitude": 2.1, "decimalLatitude": 51.3, "minimumDepthInMeters": 10 },
            { "id": 2, "decimalLongitude": 2.1, "decimalLatitude": 51.3, "minimumDepthInMeters": 10, "maximumDepthInMeters": 1000 },
            {"id": 1, "decimalLongitude": 2.1, "decimalLatitude": 51.3, "minimumDepthInMeters": -10}
        ]
        results = location.check(records, xylookup=True)
        self.assertEqual(results[0]["annotations"]["minimumDepthInMeters"], 1000)
        self.assertNotIn(Flag.NO_DEPTH.value, results[0]["flags"])
        self.assertIn(Flag.DEPTH_EXCEEDS_BATH.value, results[0]["flags"])
        self.assertEqual(results[1]["annotations"]["minimumDepthInMeters"], 10)
        self.assertNotIn(Flag.NO_DEPTH.value, results[1]["flags"])
        self.assertNotIn(Flag.DEPTH_EXCEEDS_BATH.value, results[1]["flags"])
        self.assertEqual(results[2]["annotations"]["minimumDepthInMeters"], 10)
        self.assertNotIn(Flag.NO_DEPTH.value, results[2]["flags"])
        self.assertIn(Flag.DEPTH_EXCEEDS_BATH.value, results[2]["flags"])
        self.assertEqual(results[3]["annotations"]["minimumDepthInMeters"], -10)
        self.assertNotIn(Flag.NO_DEPTH.value, results[3]["flags"])
        self.assertNotIn(Flag.DEPTH_EXCEEDS_BATH.value, results[3]["flags"])

    def test_depth_min_max(self):
        records = [
            { "id": 0, "minimumDepthInMeters": 10, "maximumDepthInMeters": 2 }
        ]
        results = location.check(records)
        self.assertEqual(results[0]["annotations"]["minimumDepthInMeters"], 10)
        self.assertEqual(results[0]["annotations"]["maximumDepthInMeters"], 2)
        self.assertNotIn(Flag.NO_DEPTH.value, results[0]["flags"])
        self.assertIn(Flag.MIN_DEPTH_EXCEEDS_MAX.value, results[0]["flags"])

    def test_depth_out_of_range(self):
        records = [
            { "id": 0, "minimumDepthInMeters": 12000, "maximumDepthInMeters": 12000 }
        ]
        results = location.check(records)
        self.assertNotIn("minimumDepthInMeters", results[0]["annotations"])
        self.assertNotIn("maximumDepthInMeters", results[0]["annotations"])
        self.assertIn(Flag.NO_DEPTH.value, results[0]["flags"])
        self.assertIn(Flag.DEPTH_OUT_OF_RANGE.value, results[0]["flags"])
        self.assertIn(Flag.DEPTH_OUT_OF_RANGE.value, results[0]["flags"])
        self.assertIn("minimumDepthInMeters", results[0]["invalid"])
        self.assertIn("maximumDepthInMeters", results[0]["invalid"])

    def test_depth_out_of_range_invalid(self):
        records = [
            { "id": 0, "minimumDepthInMeters": "NA" }
        ]
        results = location.check(records)
        self.assertNotIn("minimumDepthInMeters", results[0]["annotations"])
        self.assertIn(Flag.NO_DEPTH.value, results[0]["flags"])
        self.assertNotIn(Flag.DEPTH_OUT_OF_RANGE.value, results[0]["flags"])
        self.assertIn("minimumDepthInMeters", results[0]["invalid"])

    def test_shoredistance(self):
        records = [
            { "id": 0, "decimalLongitude": 2.1, "decimalLatitude": 51.3 },
            { "id": 0, "decimalLongitude": 7.3, "decimalLatitude": 50.3 }
        ]
        results = location.check(records, xylookup=True)
        self.assertIn("shoredistance", results[0]["annotations"])
        self.assertTrue(results[0]["annotations"]["shoredistance"] > 0)
        self.assertIn("shoredistance", results[1]["annotations"])
        self.assertTrue(results[1]["annotations"]["shoredistance"] < 0)
        self.assertIn(Flag.ON_LAND.value, results[1]["flags"])

    def test_areas(self):
        records = [
            { "id": 0, "decimalLongitude": 2.1, "decimalLatitude": 51.3 },
            { "id": 0, "decimalLongitude": 7.3, "decimalLatitude": 50.3 }
        ]
        results = location.check(records, xylookup=True)
        self.assertTrue(len(results[0]["annotations"]["areas"]) > 0)
        self.assertTrue(len(results[1]["annotations"]["areas"]) == 0)

    def test_grids(self):
        records = [
            {"id": 0, "decimalLongitude": 2.1, "decimalLatitude": 51.3}
        ]
        results = location.check(records, xylookup=True)
        self.assertIn("bathymetry", results[0]["annotations"])
        self.assertIn("sst", results[0]["annotations"])
        self.assertIn("sss", results[0]["annotations"])


if __name__ == "__main__":
    unittest.main()