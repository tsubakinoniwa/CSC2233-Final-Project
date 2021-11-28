from NFS.proc import NFSPROC
from NFS.fattr import FileAttribute
from NFS.fhandle import FileHandle
from NFS.stat import Stat


class Server(NFSPROC):
    """
    The NFS file server in our simulation. It holds information of its files
    in memory as char arrays and also implements the server-side NFS protocol.
    """

    def __init__(self):
        self.files = {'foo.txt': []}

    def getattr(self, fhandle: FileHandle) -> NFSPROC.GETATTR_RET_TYPE:
        try:
            file = self.parse_fhandle(fhandle)
        except FileNotFoundError:
            return Stat.NFSERR_NOENT,

        fattr = FileAttribute()
        fattr.size = len(file)
        return Stat.NFS_OK, fattr

    def lookup(self, fhandle: FileHandle, filename: str) \
            -> NFSPROC.LOOKUP_RET_TYPE:
        if len(fhandle.path) > 0 or filename not in self.files:
            return Stat.NFSERR_NOENT,

        fhandle = FileHandle([filename])
        return Stat.NFS_OK, fhandle, self.getattr(fhandle)

    def read(self, fhandle: FileHandle, offset: int, count: int) \
            -> NFSPROC.READ_RET_TYPE:
        try:
            file = self.parse_fhandle(fhandle)
        except FileNotFoundError:
            return Stat.NFSERR_NOENT,
        content = ''.join(file[offset:min(offset + count, len(file))])

        return Stat.NFS_OK, self.getattr(fhandle), content

    def write(self, fhandle: FileHandle, offset: int, data: str) \
            -> NFSPROC.WRITE_RET_TYPE:
        try:
            file = self.parse_fhandle(fhandle)
        except FileNotFoundError:
            return Stat.NFSERR_NOENT,

        # Keep appending the null character to the file until the file is large
        # enough to fit all the write
        while len(file) < offset + len(data):
            file.append('\0')

        for i in range(len(data)):
            file[i+offset] = data[i]

        return Stat.NFS_OK, self.getattr(fhandle)

    def parse_fhandle(self, fhandle: FileHandle):
        if len(fhandle.path) != 1:
            raise FileNotFoundError()

        filename = fhandle.path[0]
        if filename not in self.files:
            raise FileNotFoundError()

        return self.files[filename]  # Returns a reference to the content of the file
