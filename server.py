from NFS.proc import NFSPROC
from NFS.fattr import FileAttribute
from NFS.fhandle import FileHandle


class Server(NFSPROC):
    """
    The NFS file server in our simulation. It holds information of its files
    in memory as char arrays and also implements the server-side NFS protocol.
    """

    def __init__(self):
        self.files = {'foo.txt': []}

    def getattr(self, fhandle: FileHandle):
        file = self.parse_fhandle(fhandle)

        fattr = FileAttribute()
        fattr.size = len(file)
        return fattr

    def lookup(self, fhandle: FileHandle, filename: str):
        if len(fhandle.path) > 0:
            raise FileNotFoundError("The requested file handle is invalid.")

        if filename not in self.files:
            raise FileNotFoundError("The requested file cannot be found.")

        fhandle = FileHandle([filename])
        return fhandle, self.getattr(fhandle)

    def read(self, fhandle: FileHandle, offset: int, count: int):
        file = self.parse_fhandle(fhandle)
        return self.getattr(fhandle), ''.join(file[offset:min(offset+count, len(file))])

    def write(self, fhandle: FileHandle, offset: int, data: str):
        file = self.parse_fhandle(fhandle)

        # Keep appending the null character to the file until the file is large
        # enough to fit all the write
        while len(file) < offset + len(data):
            file.append('\0')

        for i in range(len(data)):
            file[i+offset] = data[i]

        return self.getattr(fhandle)

    def parse_fhandle(self, fhandle: FileHandle):
        if len(fhandle.path) != 1:
            raise FileNotFoundError("The requested file handle is invalid.")

        filename = fhandle.path[0]
        if filename not in self.files:
            raise FileNotFoundError("The requested file cannot be found.")

        return self.files[filename]  # Returns a reference to the content of the file
