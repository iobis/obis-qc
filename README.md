![tests](https://github.com/iobis/obis-qc/workflows/tests/badge.svg)

# obis-qc
### Install

```
pip install git+https://github.com/iobis/isodateparser.git
pip install git+https://github.com/iobis/pyxylookup.git
pip install git+https://github.com/iobis/pyworms.git
python setup.py install
```

### Run tests

```
nosetests --with-coverage --cover-package=obisqc --cover-html
```

### Quality checks

The following checks are performed on each occurrence record in order to add quality flags, tag as absence data, or drop records from the main index:

| Check                                                        | Fields                                | Flags        | Absence | Dropped | [Vandepitte et al.](https://www.ncbi.nlm.nih.gov/pubmed/25632106) flag number |
| :----------------------------------------------------------- | :------------------------------------ | :----------- | :------ | :------ | :----------------------------------------------------------- |
| `occurrenceStatus` should be present.                        | `occurrenceStatus`                    |              |         |         |                                                              |
| `occurrenceStatus` should be `absent` or `present`.          | `occurrenceStatus`                    |              | x       |         |                                                              |
| If `individualCount` equals 0, record is absence.            | `individualCount`                     |              | x       |         |                                                              |
| `eventDate` should be present.                               | `eventDate`                           |              |         |         | 7, 11, 12, 13                                                |
| `eventDate` should conform to ISO 8601.                      | `eventDate`                           |              |         |         |                                                              |
| `eventDate` should not be in the future.                     | `eventDate`                           |              |         |         |                                                              |
| `decimalLongitude` should be present                         | `decimalLongitude`                    | `no_coord`   |         | x       |                                                              |
| `decimalLatitude` should be present                          | `decimalLatitude`                     | `no_coord`   |         | x       |                                                              |
| `decimalLatitude` and `decimalLongitude` should not be zero  | `decimalLongitude`, `decimalLatitude` | `zero_coord` |         | x       | 4                                                            |
| `decimalLatitude` and `decimalLongitude` should be within range | `decimalLongitude`, `decimalLatitude` | `no_coord`   |         | x       | 5                                                            |
| `coordinateUncertaintyInMeters` should be present.           | `coordinateUncertaintyInMeters`       |              |         |         |                                                              |
| `minimumDepthInMeters` should be present.                    | `minimumDepthInMeters`                |              |         |         |                                                              |
| `maximumDepthInMeters` should be present.                    | `minimumDepthInMeters`                |              |         |         |                                                              |
| `minimumDepthInMeters` should be less than or equal to the bathymetric depth. | `minimumDepthInMeters`                | `bath_issue` |         |         | 19                                                           |
| `maximumDepthInMeters` should be less than or equal to the bathymetric depth. | `maximumDepthInMeters`                | `bath_issue` |         |         | 19                                                           |
| Is the occurrence located on land?                           | `decimalLongitude`, `decimalLatitude` |              |         |         | 6                                                            |
| `scientificName` should be present.                          | `scientificName`                      |              |         |         |                                                              |
| `scientificNameID` should be present.                        | `scientificNameID`                    |              |         |         |                                                              |
| `scientificNameID` should be valid WoRMS LSID.               | `scientificNameID`                    |              |         |         | 2                                                            |
| Taxon should unambiguously match with WoRMS.                 | `scientificName`, `scientificNameID`  |              |         | x       |                                                              |
| Taxon should not be exclusively freshwater or terrestrial according to WoRMS. | `scientificName`, `scientificNameID`  |              |         | x       |                                                              |

[Vandepitte et al.](https://www.ncbi.nlm.nih.gov/pubmed/25632106) flags not implemented: 3, 9, 14, 15, 16, 10, 17, 21-30.

