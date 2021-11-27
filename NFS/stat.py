from enum import Enum


class Stat(Enum):
    """
    Enum of a subset of all the error codes defined in NFSv2 that are relevant
    for our purpose.
    """

    NFS_OK       = 0
    NFSERR_NOENT = 2
