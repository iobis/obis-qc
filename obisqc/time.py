from isodateparser import ISODateParser
import datetime
import logging
from obisqc.util.flags import Flag
from obisqc.model import Record
from typing import List

logger = logging.getLogger(__name__)


def date_to_millis(d) -> int:
    """Convert a date to milliseconds."""
    return int((d - datetime.date(1970, 1, 1)).total_seconds() * 1000)


def check_record(record: Record, min_year: int = 1582):
    """Check the eventDate."""

    if record.get("eventDate") is not None:
        try:
            parser = ISODateParser(record.get("eventDate"))

            if parser.dates["start"].year < min_year:
                # year precedes minimum year in settings
                record.set_flag(Flag.DATE_BEFORE_MIN)
                raise ValueError

            ms_start = date_to_millis(parser.dates["start"])
            ms_mid = date_to_millis(parser.dates["mid"])
            ms_end = date_to_millis(parser.dates["end"])
            year = datetime.datetime.fromtimestamp(ms_mid / 1000).year

            if ms_end > date_to_millis(datetime.date.today()):
                # date in the future
                record.set_flag(Flag.DATE_IN_FUTURE)
                raise ValueError

            record.set_interpreted("date_start", ms_start)
            record.set_interpreted("date_mid", ms_mid)
            record.set_interpreted("date_end", ms_end)
            record.set_interpreted("date_year", year)

        except ValueError:
            record.set_invalid("eventDate")
        except:
            logger.error("Error processing date " + record.get("eventDate"))
            raise
    else:
        record.set_missing("eventDate")


def check(records: List[Record], min_year: int = 1582):
    return [check_record(record, min_year) for record in records]
