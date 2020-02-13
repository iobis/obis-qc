from enum import Enum

class Status(Enum):
    ACCEPTED = "accepted"
    UNACCEPTED = "unaccepted"
    NOMEN_NUDUM = "nomen nudum"
    NOMEN_DUBIUM = "nomen dubium"
    UNCERTAIN = "uncertain"
