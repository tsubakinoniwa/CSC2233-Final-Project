class FileHandle:
    """
    File handle struct in the NFSv2 protocol. In the original specification
    of NFSv2 (RFC 1094), file handle is defined as an opaque sequence of bytes,
    meaning the implementation can use these bytes as see fit.

    Since our server will only have one level of directory stored as a filename
    to char array map, we simply let the file handle be the key to our map
    """

    def __init__(self, filename):
        self.filename = filename
