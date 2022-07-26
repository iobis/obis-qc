from typing import List
import pyxylookup

from obisqc.model import Record


def check_float(value, valid_range=None):
    result = { "valid": None, "float": None, "in_range": None }
    if value is not None:
        try:
            value_float = float(value)
            if valid_range is not None:
                result["in_range"] = valid_range[0] <= value_float <= valid_range[1]
                if result["in_range"]:
                    result["float"] = value_float
                    result["valid"] = True
                else:
                    result["valid"] = False
            else:
                result["float"] = value_float
                result["valid"] = True
        except ValueError:
            result["valid"] = False
    return result


def do_xylookup(records: List[Record]) -> None:
    output = [None] * len(records)
    indices = []
    coordinates = []
    for i in range(len(records)):
        record = records[i]
        if record.get_interpreted("decimalLongitude") is not None and record.get_interpreted("decimalLatitude") is not None:
            indices.append(i)
            coordinates.append([record.get_interpreted("decimalLongitude"), record.get_interpreted("decimalLatitude")])
    if len(coordinates) > 0:
        xy = pyxylookup.lookup(coordinates, shoredistance=True, grids=True, areas=True)
        for i in range(len(indices)):
            output[indices[i]] = xy[i]
    return output
