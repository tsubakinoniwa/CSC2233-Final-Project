from enum import Enum

from NFS.fhandle import FileHandle


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
        LOOKUP = 1
        READ = 2
        WRITE = 3
        CREATE = 4
        REMOVE = 5
        MKDIR = 6
        RMDIR = 7

    def __init__(self, type: Type, func, *args):
        self.type = type
        self.func = func
        self.args = args
        self.ready = True
        self.resp = None

    def summarize(self):
        if self.ready:  # Hasn't executed yet
            raise Exception

        if self.type in {Request.Type.REMOVE, Request.Type.RMDIR}:
            return self.resp.name,
        elif self.type == Request.Type.READ:
            # return (self.resp[0].name,
            #         *[t.summarize() for t in self.resp[1:]])
            return self.resp[0].name, self.resp[-1]
        else:
            return self.resp[0].name,

    def serve(self):
        if self.ready:
            self.ready = False
            self.resp = self.func(*self.args)
            return self.resp

    def is_file_op(self):
        return self.type in {
            self.Type.GETATTR, self.Type.READ, self.Type.WRITE,
            self.type.CREATE, self.type.REMOVE, self.Type.LOOKUP
        }

    def _commutes_with(self, r: "Request"):
        # Debug placeholder to turn off pruning by ensuring all permutation
        # of events get explored.
        return False

    def commutes_with(self, r: "Request"):
        """
        Tests if two operations commute.
        :param r: Another request object
        :return: True if both commute, false otherwise
        """
        s = self  # Alias for self to save some typing ;)

        if s.is_file_op() and r.is_file_op():
            # Both r and s are file operations.
            if Request.__get_file(s) != Request.__get_file(r):
                # If operate on different files, then definitely commute
                return True
            else:
                commuting_group = {Request.Type.GETATTR, Request.Type.LOOKUP,
                                   Request.Type.READ}
                return s.type in commuting_group and r.type in commuting_group

        # From this point onwards, at least one of r and s is not a
        # file operation.

        if r.is_file_op():
            # s is a directory operation and r is a file operation.
            # Swap r and s and compute commutivity in the next case. This is
            # possible since commutivity is an equivalence relation.
            s, r = r, s

        if s.is_file_op():
            # s is a file operation and r is a directory operation.
            s_name = Request.__get_file(s)
            r_name = Request.__get_dir(r)
            if len(s_name) < len(r_name) or s_name[:len(r_name)] != r_name:
                # If the file s operates on does not contain the directory r
                # operates on as a prefix, then cannot commute
                return True
            else:
                # Will not commute regardless of whether r is MKDIR or RMDIR
                return False
        else:
            # Both r and s are directory operations
            s_name = Request.__get_dir(s)
            r_name = Request.__get_dir(r)
            return s_name != r_name  # Commute iff operate on different dirs

    @staticmethod
    def __get_file(r: "Request") -> str:
        """
        Gets the file on which request r operates on
        :param r: Request object for which r.is_file_op() is True
        :return: A string representing the absolute path of the file
        """
        assert(r.is_file_op())

        if r.type in {Request.Type.LOOKUP, Request.Type.CREATE,
                      Request.Type.REMOVE}:
            fhandle, fname = r.args
            assert(isinstance(fhandle, FileHandle))
            assert(isinstance(fname, str))

            if len(fhandle.path) > 0:
                return '/' + '/'.join(fhandle.path) + '/' + fname
            else:
                return '/' + fname
        else:
            fhandle = r.args[0]
            assert(isinstance(fhandle, FileHandle))

            return '/' + '/'.join(fhandle.path)

    @staticmethod
    def __get_dir(r: "Request") -> str:
        """
        Gets the directory on which request r operates on
        :param r: Request object for which r.is_file_op() is False
        :return: A string representing the absolute path of the directory
        """
        assert(not r.is_file_op())

        fhandle, dirname = r.args
        assert(isinstance(fhandle, FileHandle))
        assert(isinstance(dirname, str))

        if len(fhandle.path) > 0:
            return '/' + '/'.join(fhandle.path) + '/' + dirname
        else:
            return '/' + dirname
