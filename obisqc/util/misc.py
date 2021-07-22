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


def do_xylookup(results):
    import pyxylookup
    output = [None] * len(results)
    indices = []
    coordinates = []
    for i in range(len(results)):
        result = results[i]
        if "decimalLongitude" in result["annotations"] and "decimalLatitude" in result["annotations"]:
            indices.append(i)
            coordinates.append([result["annotations"]["decimalLongitude"], result["annotations"]["decimalLatitude"]])
    if len(coordinates) > 0:
        xy = pyxylookup.lookup(coordinates, shoredistance=True, grids=True, areas=True)
        for i in range(len(indices)):
            output[indices[i]] = xy[i]
    return output


def trim_whitespace(d):
    return {k: (v.strip() if isinstance(v, str) else v) for k, v in d.items()}
