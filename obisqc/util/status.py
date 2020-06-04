from enum import Enum

class Status(Enum):
    ACCEPTED = "accepted"
    UNACCEPTED = "unaccepted"
    NOMEN_NUDUM = "nomen nudum"
    NOMEN_DUBIUM = "nomen dubium"
    UNCERTAIN = "uncertain"
    QUARANTINED = "quarantined"
    DELETED = "deleted"
    TAXON_INQUIRENDUM = "taxon inquirendum"
    INTERIM_UNPUBLISHED = "interim unpublished"
    TEMPORARY_NAME = "temporary name"
