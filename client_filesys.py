from collections import deque

from NFS.proc import NFSPROC
from NFS.fattr import FileAttribute
from NFS.fhandle import FileHandle
from NFS.stat import Stat
from server import Server
from request import Request


class ClientFileSystem:
    """
    I/O operations exposed to a client. Every instance of a ClientFileSystem
    also holds a pointer to a NFS file server that it should interface with.

    Every I/O operation here is implemented as a coroutine. This is because
    an outer "simulation" class would control the order of execution of each
    thread's NFS procedures, so the controlling thread must be able to
    "interrupt" processes when they are about to perform an NFS procedure.
    Using generators allows us to do that naturally - at the time of yield,
    control is automatically transferred to the controlling thread.
    """

    MAX_FILES = 100  # Maximum number of files

    class File:
        """
        Represents each individual file. The file system also keeps track of
        the last written position of every given file.
        """
        def __init__(self, fd, fhandle: FileHandle):
            self.fd = fd
            self.offset = 0  # Last accessed position
            self.fhandle = fhandle

    def __init__(self, server: Server):
        self.server = server
        self.file_descriptors = {}
        self.available_fds = deque(range(ClientFileSystem.MAX_FILES))
        self.attribute_cache = {}

    def open(self, fname: str) -> int:
        """
        Open a file
        :param fname: file name of the file to open
        :return: -1 if the filenmame is not found, otherwise a file descriptor
        """
        empty_fhandle = FileHandle([])
        req = Request(Request.Type.LOOKUP, self.server.lookup, empty_fhandle, fname)
        resp = yield req

        if len(resp) == 1:  # The file is not found
            assert(resp[0] == Stat.NFSERR_NOENT)
            return -1  # Invalid file descriptor

        _, fhandle, fattr = resp

        if not len(self.available_fds):
            return -1  # All file descriptors used up
        new_fd = self.available_fds.popleft()
        new_file = self.File(new_fd, fhandle)

        self.file_descriptors[new_fd] = new_file
        self.attribute_cache[new_fd] = fattr  # Fills in the attribute cache

        return new_fd

    def close(self, fd: int) -> bool:
        """
        Closes the file given by the file descriptor fd
        :param fd: The file descriptor of the file to be closed.
        :return True if succeeds, false otherwise
        """
        if fd not in self.file_descriptors:
            return False

        self.available_fds.appendleft(fd)
        del self.file_descriptors[fd]
        del self.attribute_cache[fd]
        return True

    def read(self, fd: int, count: int) -> str:
        """
        Reads count bytes from the file referred to by file descriptor fd,
        starting from the last accessed position of the file.
        :param fd: File descriptor of the file to be read from
        :param count: Number of bytes to read
        :return: The content read, represented as a string. If the read is
        invalid, returns an empty string
        """
        if fd not in self.file_descriptors:
            return ''

        fhandle = FileHandle([])
        file = self.file_descriptors[fd]
        offset = file.offset

        req = Request(Request.Type.READ, self.server.read, fhandle, offset, count)
        resp = yield req

        if len(resp) == 1:
            assert(resp[0] == Stat.NFSERR_NOENT)
            return ''

        _, fattr, res = resp
        file.offset += len(res)
        self.attribute_cache[fd] = fattr

        return res

    def write(self, fd, s) -> bool:
        """
        Writes to the file given by the file descriptor fd
        :param fd: File descriptor of the file to be written
        :param s: String representation of the write content
        :return: True if the write is successful, and false otherwise
        """
        if fd not in self.file_descriptors:
            return False

        file = self.file_descriptors[fd]
        fhandle = file.fhandle
        offset = file.offset

        req = Request(Request.Type.WRITE, self.server.write, fhandle, offset, s)
        resp = yield req

        if len(resp) == 1:
            assert(resp[0] == Stat.NFSERR_NOENT)
            return ''

        _, fattr = resp
        file.offset += len(s)
        self.attribute_cache[fd] = fattr

    def append(self, fd, s) -> bool:
        """
        Appends s to the end of the file referenced by fd
        :param fd: File descriptor of the file on which s is to be appended
        :param s: String representation of the append content
        :return: True if the append is successful, and false otherwise
        """
        if fd not in self.file_descriptors:
            return False

        # Here we stipulate that our implementation is aggressive in avoiding
        # stale cache, in that upon every operation that involves the attribute
        # of the file, we will do a new GETATTR instead of using the cached
        # attributes of the file.
        file = self.file_descriptors[fd]

        req = Request(Request.Type.GETATTR, self.server.getattr, file.fhandle)
        resp = yield req

        if len(resp) == 1:
            assert(resp[0] == Stat.NFSERR_NOENT)
            return False

        _, fattr = resp
        self.attribute_cache[fd] = fattr

        # Just asked the server for the latest file length. Append by writing
        # to the end of file.
        fhandle = file.handle
        offset = fattr.size

        req = Request(Request.Type.WRITE, self.server.write, fhandle, offset, s)
        resp = yield req

        if len(resp) == 1:
            assert(resp[0] == Stat.NFSERR_NOENT)
            return False

        _, fattr = resp
        self.attribute_cache[fd] = fattr

        return True
