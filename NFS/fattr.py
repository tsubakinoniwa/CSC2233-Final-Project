class FileAttribute:
    """
    File attribute struct in the NFSv2 protocol. The original protocol
    (https://datatracker.ietf.org/doc/html/rfc1094#section-2.3.5) specified
    more fields, but most are unnecessary for our simplified server.
    """

    def __init__(self):
        self.size = 0    # File size
