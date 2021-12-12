from typing import Union

from NFS.proc import NFSPROC
from NFS.fattr import FileAttribute
from NFS.fhandle import FileHandle
from NFS.stat import Stat


class File:
    def is_raw_file(self) -> bool:
        pass


class RawFile(File):
    """
    Models a simple non-directory file. Contains only raw bytes.
    """
    def __init__(self):
        self.bytes = []

    def is_raw_file(self) -> bool:
        return True


class Directory(File):
    """
    Models a directory on the server. Implements a nested directory tree.
    """
    def __init__(self):
        self.files = {}
        self.empty = True

    def is_raw_file(self) -> bool:
        return False


class Server(NFSPROC):
    """
    The NFS file server in our simulation. It holds information of its files
    in memory as char arrays and also implements the server-side NFS protocol.
    """

    def __init__(self):
        self.root = Directory()
        self.root.files['foo.txt'] = RawFile()  # Populate a foo.txt in root dir

    def getattr(self, fhandle: FileHandle) -> NFSPROC.GETATTR_RET_TYPE:
        try:
            file = self.__parse_fhandle(fhandle)
        except FileNotFoundError:
            return Stat.NFSERR_NOENT,

        if not file.is_raw_file():
            return Stat.NFSERR_ISDIR,
        assert(isinstance(file, RawFile))

        fattr = FileAttribute()
        fattr.size = len(file.bytes)
        return Stat.NFS_OK, fattr

    def lookup(self, fhandle: FileHandle, filename: str) \
            -> NFSPROC.LOOKUP_RET_TYPE:
        try:
            file = self.__parse_fhandle(fhandle)
        except FileNotFoundError:
            return Stat.NFSERR_NOENT,

        if file.is_raw_file():
            return Stat.NFSERR_NOTDIR,
        assert(isinstance(file, Directory))

        if filename not in file.files:
            return Stat.NFSERR_NOENT,

        fhandle = FileHandle([*fhandle.path, filename])
        return Stat.NFS_OK, fhandle, self.getattr(fhandle)[1]

    def read(self, fhandle: FileHandle, offset: int, count: int) \
            -> NFSPROC.READ_RET_TYPE:
        try:
            file = self.__parse_fhandle(fhandle)
        except FileNotFoundError:
            return Stat.NFSERR_NOENT,

        if not file.is_raw_file():
            return Stat.NFSERR_ISDIR,
        assert(isinstance(file, RawFile))

        content = ''.join(
            file.bytes[offset:min(offset + count, len(file.bytes))])

        return Stat.NFS_OK, self.getattr(fhandle)[1], content

    def write(self, fhandle: FileHandle, offset: int, data: str) \
            -> NFSPROC.WRITE_RET_TYPE:
        try:
            file = self.__parse_fhandle(fhandle)
        except FileNotFoundError:
            return Stat.NFSERR_NOENT,

        if not file.is_raw_file():
            return Stat.NFSERR_ISDIR,
        assert (isinstance(file, RawFile))

        # Keep appending the null character to the file until the file is large
        # enough to fit all the write
        while len(file.bytes) < offset + len(data):
            file.bytes.append('\0')

        for i in range(len(data)):
            file.bytes[i+offset] = data[i]

        return Stat.NFS_OK, self.getattr(fhandle)[1]

    def create(self, fhandle: FileHandle, name: str) -> NFSPROC.CREATE_RET_TYPE:
        pass

    def remove(self, fhandle: FileHandle, name: str) -> NFSPROC.REMOVE_RET_TYPE:
        pass

    def mkdir(self) -> NFSPROC.MKDIR_RET_TYPE:
        pass

    def rmdir(self) -> NFSPROC.RMDIR_RET_TYPE:
        pass

    def __parse_fhandle(self, fhandle: FileHandle) -> File:
        fptr = self.root
        for p in fhandle.path:
            if fptr.is_raw_file():
                # Is a raw file but we need to traverse
                raise FileNotFoundError

            if p in fptr.files:
                fptr = fptr.files[p]
            else:
                # The file is not found
                raise FileNotFoundError

        return fptr
