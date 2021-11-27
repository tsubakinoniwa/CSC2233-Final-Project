from typing import Tuple

from .fattr import FileAttribute
from .fhandle import FileHandle


class NFSPROC:
    """
    NFS Procedures in the simplified NFS protocol. This class only serves
    as an interface, and the procedures defined here are meant to be
    overwritten by an actual implementation.

    For reference, see the original specification (RFC 1094) of the NFSv2
    protocol. According to "NFS Illustrated" (O'Reilly Media), some parameters
    of these functions were unused and removed from NFSv3. We omit the unused
    parameters here.
    """

    def getattr(self, fhandle: FileHandle) -> FileAttribute:
        pass

    def lookup(self, fhandle: FileHandle, filename: str) \
            -> Tuple[FileHandle, FileAttribute]:
        pass

    def read(self, fhandle: FileHandle, offset: int, count: int) \
            -> Tuple[FileAttribute, str]:
        pass

    def write(self, fhandle: FileHandle, offset: int, data: str) \
            -> FileAttribute:
        pass
