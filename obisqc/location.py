from obisqc.util import util
import logging
from obisqc.util.flags import Flag
logger = logging.getLogger(__name__)


def check_record(record):
    """Check location related fields."""

    result = {
        "id": record["id"],
        "missing": [],
        "invalid": [],
        "flags": [],
        "annotations": {},
        "dropped": False
    }

    # coordinates

    if "decimalLongitude" in record:
        lon_check = util.check_float(record["decimalLongitude"], [-180, 180])
        if not lon_check["valid"]:
            result["invalid"].append("decimalLongitude")
            if not lon_check["in_range"]:
                result["flags"].append(Flag.LON_OUT_OF_RANGE.value)
        else:
            result["annotations"]["decimalLongitude"] = lon_check["float"]
    else:
        result["missing"].append("decimalLongitude")

    if "decimalLatitude" in record:
        lat_check = util.check_float(record["decimalLatitude"], [-90, 90])
        if not lat_check["valid"]:
            result["invalid"].append("decimalLatitude")
            if not lat_check["in_range"]:
                result["flags"].append(Flag.LAT_OUT_OF_RANGE.value)
        else:
            result["annotations"]["decimalLatitude"] = lat_check["float"]
    else:
        result["missing"].append("decimalLatitude")

    if (not "decimalLongitude" in result["annotations"]) or (not "decimalLatitude" in result["annotations"]):
        result["flags"].append(Flag.NO_COORD.value)
        result["dropped"] = True

    if "decimalLongitude" in result["annotations"] and "decimalLatitude" in result["annotations"]:
        if result["annotations"]["decimalLongitude"] == 0 and result["annotations"]["decimalLatitude"] == 0:
            result["flags"].append(Flag.ZERO_COORD.value)
            result["dropped"] = True

    # depth

    if "minimumDepthInMeters" in record:
        min_check = util.check_float(record["minimumDepthInMeters"], [-100000, 11000])
        if not min_check["valid"]:
            result["invalid"].append("minimumDepthInMeters")
            if not min_check["in_range"]:
                result["flags"].append(Flag.DEPTH_OUT_OF_RANGE.value)
        else:
            result["annotations"]["minimumDepthInMeters"] = min_check["float"]
    else:
        result["missing"].append("minimumDepthInMeters")

    if "maximumDepthInMeters" in record:
        max_check = util.check_float(record["maximumDepthInMeters"], [-100000, 11000])
        if not max_check["valid"]:
            result["invalid"].append("maximumDepthInMeters")
            if not max_check["in_range"]:
                result["flags"].append(Flag.DEPTH_OUT_OF_RANGE.value)
        else:
            result["annotations"]["maximumDepthInMeters"] = max_check["float"]
    else:
        result["missing"].append("maximumDepthInMeters")

    if (not "minimumDepthInMeters" in result["annotations"]) and (not "maximumDepthInMeters" in result["annotations"]):
        result["flags"].append(Flag.NO_DEPTH.value)

    if "minimumDepthInMeters" in result["annotations"] and "maximumDepthInMeters" in result["annotations"]:
        if result["annotations"]["minimumDepthInMeters"] > result["annotations"]["maximumDepthInMeters"]:
            result["flags"].append(Flag.MIN_DEPTH_EXCEEDS_MAX.value)

    return result


def check_xy(result, xy):
    """Perform checks using results from the xylookup service."""

    # depth

    depth_exceeds_bath = False
    if "minimumDepthInMeters" in result["annotations"] and "bathymetry" in xy["grids"]:
        if result["annotations"]["minimumDepthInMeters"] > xy["grids"]["bathymetry"]:
            depth_exceeds_bath = True
    if "maximumDepthInMeters" in result["annotations"] and "bathymetry" in xy["grids"]:
        if result["annotations"]["maximumDepthInMeters"] > xy["grids"]["bathymetry"]:
            depth_exceeds_bath = True
    if depth_exceeds_bath:
        result["flags"].append(Flag.DEPTH_EXCEEDS_BATH.value)

    # shoredistance

    result["annotations"]["shoredistance"] = xy["shoredistance"]
    if xy["shoredistance"] < 0:
        result["flags"].append(Flag.ON_LAND.value)

    # areas

    areas = []
    for key in xy["areas"]:
        for area in xy["areas"][key]:
            areas.append(area["id"])
    result["annotations"]["areas"] = areas

    # grids

    if "sstemperature" in xy["grids"]:
        result["annotations"]["sst"] = round(xy["grids"]["sstemperature"], 2)
    if "sssalinity" in xy["grids"]:
        result["annotations"]["sss"] = round(xy["grids"]["sssalinity"], 2)
    if "bathymetry" in xy["grids"]:
        result["annotations"]["bathymetry"] = round(xy["grids"]["bathymetry"], 2)


def check(records, xylookup=False):
    results = [check_record(record) for record in records]
    if xylookup:
        xy = util.do_xylookup(results)
        assert(len(xy) == len(results))
        for i in range(len(results)):
            check_xy(results[i], xy[i])

    return results
