from isodateparser import ISODateParser
import datetime
import logging
from .util.flags import Flag
logger = logging.getLogger(__name__)


def date_to_millis(d):
    """Convert a date to milliseconds."""
    return int((d - datetime.date(1970, 1, 1)).total_seconds() * 1000)


def check_record(record, min_year=0):
    """Check the eventDate."""

    result = {
        "id": record["id"],
        "missing": [],
        "invalid": [],
        "flags": [],
        "annotations": {},
        "dropped": False
    }
    if "eventDate" in record and record["eventDate"] is not None:
        try:
            parser = ISODateParser(record["eventDate"])
            if parser.dates["mid"].year < min_year:
                # year precedes minimum year in settings
                result["flags"].append(Flag.DATE_BEFORE_MIN.value)
                raise ValueError
            ms_start = date_to_millis(parser.dates["start"])
            ms_mid = date_to_millis(parser.dates["mid"])
            ms_end = date_to_millis(parser.dates["end"])
            if ms_start > date_to_millis(datetime.date.today()):
                # date in the future
                result["flags"].append(Flag.DATE_IN_FUTURE.value)
                raise ValueError
            result["annotations"]["date_start"] = ms_start
            result["annotations"]["date_mid"] = ms_mid
            result["annotations"]["date_end"] = ms_end
        except ValueError:
            result["invalid"].append("eventDate")
        except:
            logger.error("Error processing date " + record["eventDate"])
            raise
    else:
        result["missing"].append("eventDate")
    return result


def check(records, min_year=0):
    return [check_record(record, min_year) for record in records]
