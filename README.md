![tests](https://github.com/iobis/obis-qc/workflows/tests/badge.svg)

# obis-qc
### Installation

```
pip install -r requirements.txt
python setup.py install
```

### Usage

See [tests](https://github.com/iobis/obis-qc/tree/master/test).

#### Using a cache to speed up taxonomy checks

By default the taxonomy component fetches information from WoRMS the WoRMS API by AphiaID. If you have a local cache of WoRMS information, you can use that instead of the API connection by providing an object that implements the `fetch()` and `store()` methods. The WoRMS information objects provided to the cache are constructed like this:

```python
record = pyworms.aphiaRecordByAphiaID(aphiaid)
classification = pyworms.aphiaClassificationByAphiaID(aphiaid)
bold_id = pyworms.aphiaExternalIDByAphiaID(aphiaid, "bold")
ncbi_id = pyworms.aphiaExternalIDByAphiaID(aphiaid, "ncbi")
distribution = pyworms.aphiaDistributionsByAphiaID(aphiaid)
bold_id = bold_id[0] if bold_id is not None and isinstance(bold_id, list) and len(bold_id) > 0 else None
ncbi_id = ncbi_id[0] if ncbi_id is not None and isinstance(ncbi_id, list) and len(ncbi_id) > 0 else None
aphia_info = {
    "record": record,
    "classification": classification,
    "bold_id": bold_id,
    "ncbi_id": ncbi_id,
    "distribution": distribution
}
```

### Run tests

```
nosetests --with-coverage --cover-package=obisqc --cover-html
```

### Quality checks

The following checks are performed on each occurrence record in order to add quality flags, tag as absence data, or drop records from the main index:

| Check                                                        | Fields                                         | Flags                                              | Absence | Dropped                 | [Vandepitte et al.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4309024/pdf/bau125.pdf) flag number |
| :----------------------------------------------------------- | :--------------------------------------------- | :------------------------------------------------- | :------ | :---------------------- | :----------------------------------------------------------- |
| `occurrenceStatus` should be present.                        | `occurrenceStatus`                             |                                                    |         |                         |                                                              |
| `occurrenceStatus` should be `absent` or `present`.          | `occurrenceStatus`                             |                                                    | x       |                         |                                                              |
| If `individualCount` equals 0, record is absence.            | `individualCount`                              |                                                    | x       |                         |                                                              |
| `eventDate` should be present.                               | `eventDate`                                    |                                                    |         |                         | 7, 11, 12, 13                                                |
| `eventDate` should conform to ISO 8601.                      | `eventDate`                                    |                                                    |         |                         |                                                              |
| `eventDate` should not be in the future.                     | `eventDate`                                    | `date_in_future`                                   |         |                         |                                                              |
| `eventDate` should be later than the set minimum date.       | `eventDate`                                    | `date_before_min`                                  |         |                         |                                                              |
| `decimalLongitude` and `decimalLatitude` should be present.  | `decimalLongitude`, `decimalLatitude`          | `no_coord`                                         |         | x                       |                                                              |
| `decimalLatitude` and `decimalLongitude` should not be zero. | `decimalLongitude`, `decimalLatitude`          | `zero_coord`                                       |         | x                       | 4                                                            |
| `decimalLatitude` and `decimalLongitude` should be within range. | `decimalLongitude`, `decimalLatitude`          | `lon_out_of_range`, `lat_out_of_range`, `no_coord` |         | x                       | 5                                                            |
| `coordinateUncertaintyInMeters` should be present.           | `coordinateUncertaintyInMeters`                |                                                    |         |                         |                                                              |
| `minimumDepthInMeters` and `maximumDepthInMeters` should be present. | `minimumDepthInMeters`, `maximumDepthInMeters` |                                                    |         |                         |                                                              |
| `minimumDepthInMeters` and `maximumDepthInMeters` should be within range. | `minimumDepthInMeters`, `maximumDepthInMeters` | `depth_out_of_range`                               |         |                         |                                                              |
| `minimumDepthInMeters` and `maximumDepthInMeters` should be less than or equal to the bathymetric depth. | `minimumDepthInMeters`, `maximumDepthInMeters` | `depth_exceeds_bath`                               |         |                         | 19                                                           |
| Is the occurrence located on land?                           | `decimalLongitude`, `decimalLatitude`          | `on_land`                                          |         |                         | 6                                                            |
| `scientificName` should be present.                          | `scientificName`                               |                                                    |         |                         |                                                              |
| `scientificNameID` should be present.                        | `scientificNameID`                             |                                                    |         |                         |                                                              |
| `scientificNameID` should be valid WoRMS LSID.               | `scientificNameID`                             |                                                    |         |                         | 2                                                            |
| Taxon should unambiguously match with WoRMS.                 | `scientificName`, `scientificNameID`           | `no_match`                                         |         | x                       |                                                              |
| An accepted name should exist in WoRMS.                      | `scientificName`, `scientificNameID`           | `no_accepted_name`                                 |         |                         |                                                              |
| Taxon should not be exclusively freshwater or terrestrial according to WoRMS. | `scientificName`, `scientificNameID`           | `not_marine`, `marine_unsure`                      |         | in case of `not_marine` |                                                              |

[Vandepitte et al.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4309024/pdf/bau125.pdf) flags not implemented: 3, 9, 14, 15, 16, 10, 17, 21-30.

