from enum import Enum


class Request:
    """
    Wrapper for a client request to the server that contains all the information
    necessary to complete the said NFS procedure. This class also has some extra
    utilities to allow checking whether two requests commute, which helps
    reducing the search space when exploring all the unique interleaving of
    client operations.
    """

    # Enumeration of all the NFS procedures defined in NFS.proc.
    # Used internally to compare whether two requests commute
    class Type(Enum):
        GETATTR = 0
        LOOKUP  = 1
        READ    = 2
        WRITE   = 3

    # Matrix of commutativity, where indices are operations converted to ints
    # as specified by the enumeration above.
    commute_mat = [
        [True, True, True, False],  # Whether GETATTR commutes with others
        [True, True, True, False],
        [True, True, True, False],
        [False, False, False, False],
    ]

    def __init__(self, type: Type, func, *args):
        self.type = type
        self.func = func
        self.args = args
        self.ready = True

    def serve(self):
        if self.ready:
            self.ready = False
            return self.func(*self.args)

    def commutes_with(self, r):
        return self.commute_mat[self.type.value][r.type.value]
