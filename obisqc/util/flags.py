from enum import Enum

class Flag(Enum):
    DATE_BEFORE_MIN = "date_before_min"
    DATE_IN_FUTURE = "date_in_future"
    LON_OUT_OF_RANGE = "lon_out_of_range"
    LAT_OUT_OF_RANGE = "lat_out_of_range"
    NO_COORD = "no_coord"
    ZERO_COORD = "zero_coord"
    DEPTH_OUT_OF_RANGE = "depth_out_of_range"
    NO_DEPTH = "no_depth"
    MIN_DEPTH_EXCEEDS_MAX = "min_depth_exceeds_max"
    DEPTH_EXCEEDS_BATH = "depth_exceeds_bath"
    ON_LAND = "on_land"
    NO_MATCH = "no_match"
    NOT_MARINE = "not_marine"
    NO_ACCEPTED_NAME = "no_accepted_name"
    MARINE_UNSURE = "marine_unsure"