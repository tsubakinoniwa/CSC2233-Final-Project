from typing import List


class FileHandle:
    """
    File handle struct in the NFSv2 protocol. In the original specification
    of NFSv2 (RFC 1094), file handle is defined as an opaque sequence of bytes,
    meaning the implementation can use these bytes as see fit.

    Although our server only has a single root directory right now so every file
    is identifiable by name, we leave the file handle general by storing a path
    from the root directory for potential future expansion.
    """

    def __init__(self, path: List[str]):
        self.path = path.copy()
