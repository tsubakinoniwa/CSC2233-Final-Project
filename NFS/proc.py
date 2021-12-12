from typing import Tuple, Optional, Union

from .fattr import FileAttribute
from .fhandle import FileHandle
from .stat import Stat


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

    # Aliases for the return type of each procedure
    GETATTR_RET_TYPE = Tuple[Stat, Optional[FileAttribute]]
    LOOKUP_RET_TYPE = Tuple[Stat, Optional[FileHandle], Optional[FileAttribute]]
    READ_RET_TYPE = Tuple[Stat, Optional[FileAttribute], Optional[str]]
    WRITE_RET_TYPE = Tuple[Stat, Optional[FileAttribute]]
    CREATE_RET_TYPE = Tuple[Stat, Optional[FileHandle], Optional[FileAttribute]]
    REMOVE_RET_TYPE = Stat
    MKDIR_RET_TYPE = Tuple[Stat, Optional[FileHandle], Optional[FileAttribute]]
    RMDIR_RET_TYPE = Stat

    def getattr(self, fhandle: FileHandle) -> GETATTR_RET_TYPE:
        pass

    def lookup(self, fhandle: FileHandle, filename: str) -> LOOKUP_RET_TYPE:
        pass

    def read(self, fhandle: FileHandle, offset: int, count: int) \
            -> READ_RET_TYPE:
        pass

    def write(self, fhandle: FileHandle, offset: int, data: str) \
            -> WRITE_RET_TYPE:
        pass

    def create(self, fhandle: FileHandle, name: str) -> CREATE_RET_TYPE:
        pass

    def remove(self, fhandle: FileHandle, name: str) -> REMOVE_RET_TYPE:
        pass

    def mkdir(self) -> MKDIR_RET_TYPE:
        pass

    def rmdir(self) -> RMDIR_RET_TYPE:
        pass

