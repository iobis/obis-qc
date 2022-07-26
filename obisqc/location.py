from typing import Dict, List
from obisqc.model import Record
from obisqc.util import misc
import logging
from obisqc.util.flags import Flag
import numpy

logger = logging.getLogger(__name__)


def check_record(record: Record) -> None:
    """Check location related fields."""

    # coordinate uncertainty

    if record.get("coordinateUncertaintyInMeters") is not None:
        unc_check = misc.check_float(record.get("coordinateUncertaintyInMeters"), [0, 10000000])
        if not unc_check["valid"]:
            record.set_invalid("coordinateUncertaintyInMeters")
        else:
            record.set_interpreted("coordinateUncertaintyInMeters", unc_check["float"])
    else:
        record.set_missing("coordinateUncertaintyInMeters")

    # coordinates

    if record.get("decimalLongitude") is not None:
        lon_check = misc.check_float(record.get("decimalLongitude"), [-180, 180])
        if not lon_check["valid"]:
            record.set_invalid("decimalLongitude")
            if not lon_check["in_range"]:
                record.set_flag(Flag.LON_OUT_OF_RANGE)
        else:
            record.set_interpreted("decimalLongitude", lon_check["float"])
    else:
        record.set_missing("decimalLongitude")

    if record.get("decimalLatitude") is not None:
        lat_check = misc.check_float(record.get("decimalLatitude"), [-90, 90])
        if not lat_check["valid"]:
            record.set_invalid("decimalLatitude")
            if not lat_check["in_range"]:
                record.set_flag(Flag.LAT_OUT_OF_RANGE)
        else:
            record.set_interpreted("decimalLatitude", lat_check["float"])
    else:
        record.set_missing("decimalLatitude")

    if record.get_interpreted("decimalLongitude") is None or record.get_interpreted("decimalLatitude") is None:
        record.set_flag(Flag.NO_COORD)
        record.dropped = True

    if record.get_interpreted("decimalLongitude") == 0 and record.get_interpreted("decimalLatitude") == 0:
        record.set_flag(Flag.ZERO_COORD)
        record.dropped = True

    # depth

    depths = []

    if record.get("minimumDepthInMeters") is not None:
        min_check = misc.check_float(record.get("minimumDepthInMeters"), [-100000, 11000])
        if not min_check["valid"]:
            record.set_invalid("minimumDepthInMeters")
            if min_check["in_range"] is False:
                record.set_flag(Flag.DEPTH_OUT_OF_RANGE)
        else:
            record.set_interpreted("minimumDepthInMeters", min_check["float"])
            depths.append(min_check["float"])
    else:
        record.set_missing("minimumDepthInMeters")

    if record.get("maximumDepthInMeters") is not None:
        max_check = misc.check_float(record.get("maximumDepthInMeters"), [-100000, 11000])
        if not max_check["valid"]:
            record.set_invalid("maximumDepthInMeters")
            if max_check["in_range"] is False:
                record.set_flag(Flag.DEPTH_OUT_OF_RANGE)
        else:
            record.set_interpreted("maximumDepthInMeters", max_check["float"])
            depths.append(max_check["float"])
    else:
        record.set_missing("maximumDepthInMeters")

    if record.get_interpreted("maximumDepthInMeters") is None and record.get_interpreted("minimumDepthInMeters") is None:
        record.set_flag(Flag.NO_DEPTH)

    if record.get_interpreted("maximumDepthInMeters") is not None and record.get_interpreted("minimumDepthInMeters") is not None:
        if record.get_interpreted("minimumDepthInMeters") > record.get_interpreted("maximumDepthInMeters"):
            record.set_flag(Flag.MIN_DEPTH_EXCEEDS_MAX)

    if len(depths) > 0:
        record.set_interpreted("depth", numpy.mean(depths))


def check_xy(record: Record, xy: Dict) -> None:
    """Perform checks using results from the xylookup service."""

    # depth

    intercept = 50
    slope = 1.1

    depth_exceeds_bath = False

    for depth_field in ["minimumDepthInMeters", "maximumDepthInMeters"]:
        if record.get_interpreted(depth_field) is not None and "bathymetry" in xy["grids"]:
            if xy["grids"]["bathymetry"] < 0:
                if record.get_interpreted(depth_field) > intercept + xy["grids"]["bathymetry"]:
                    depth_exceeds_bath = True
            else:
                if record.get_interpreted(depth_field) > intercept + xy["grids"]["bathymetry"] * slope:
                    depth_exceeds_bath = True

    if depth_exceeds_bath:
        record.set_flag(Flag.DEPTH_EXCEEDS_BATH)

    # shoredistance

    record.set_interpreted("shoredistance", xy["shoredistance"])
    if xy["shoredistance"] < 0:
        record.set_flag(Flag.ON_LAND)

    # areas

    areas = []
    for key in xy["areas"]:
        for area in xy["areas"][key]:
            areas.append(area["id"])
    record.set_interpreted("areas", areas)

    # grids

    if "sstemperature" in xy["grids"]:
        record.set_interpreted("sst", round(xy["grids"]["sstemperature"], 2))
    if "sssalinity" in xy["grids"]:
        record.set_interpreted("sss", round(xy["grids"]["sssalinity"], 2))
    if "bathymetry" in xy["grids"]:
        record.set_interpreted("bathymetry", round(xy["grids"]["bathymetry"], 2))


def check(records: List[Record], xylookup=False) -> None:
    for record in records:
        check_record(record)
    if xylookup:
        xy = misc.do_xylookup(records)
        assert(len(xy) == len(records))
        for i in range(len(records)):
            if xy[i] is not None:
                check_xy(records[i], xy[i])
            else:
                logger.warning("No xylookup result for record")
