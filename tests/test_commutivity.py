import unittest
from sim.request import Request
from sim.server import Server
from NFS.fhandle import FileHandle


class TestCommutivity(unittest.TestCase):
    def setUp(self) -> None:
        self.file_ops_type1 = [
            Request.Type.GETATTR, Request.Type.READ, Request.Type.WRITE
        ]
        self.file_ops_type2 = [
            Request.Type.LOOKUP, Request.Type.CREATE, Request.Type.REMOVE
        ]
        self.dir_ops = [
            Request.Type.MKDIR, Request.Type.RMDIR
        ]

    def foo(self):
        pass

    def test_different_files(self):
        for s_type in [*self.file_ops_type1, *self.file_ops_type2]:
            if s_type in self.file_ops_type1:
                s = Request(s_type, self.foo, FileHandle(['dir', 'file1.txt']))
            else:
                s = Request(s_type, self.foo, FileHandle(['dir']), 'file1.txt')

            for r_type in [*self.file_ops_type1, *self.file_ops_type2]:
                if r_type in self.file_ops_type1:
                    r = Request(r_type, self.foo, FileHandle(['dir', 'file2.txt']))
                else:
                    r = Request(r_type, self.foo, FileHandle(['dir']), 'file2.txt')

                self.assertTrue(s.commutes_with(r))
                self.assertTrue(r.commutes_with(s))

    def test_same_file(self):
        for s_type in [*self.file_ops_type1, *self.file_ops_type2]:
            if s_type in self.file_ops_type1:
                s = Request(s_type, self.foo, FileHandle(['dir', 'file1.txt']))
            else:
                s = Request(s_type, self.foo, FileHandle(['dir']), 'file1.txt')

            for r_type in [*self.file_ops_type1, *self.file_ops_type2]:
                if r_type in self.file_ops_type1:
                    r = Request(r_type, self.foo, FileHandle(['dir', 'file1.txt']))
                else:
                    r = Request(r_type, self.foo, FileHandle(['dir']), 'file1.txt')

                commuting_group = {Request.Type.GETATTR, Request.Type.LOOKUP,
                                   Request.Type.READ}
                if s_type in commuting_group and r_type in commuting_group:
                    self.assertTrue(s.commutes_with(r))
                    self.assertTrue(r.commutes_with(s))
                else:
                    self.assertFalse(s.commutes_with(r))
                    self.assertFalse(r.commutes_with(s))

    def test_dir_ops(self):
        for s_type in [*self.file_ops_type1, *self.file_ops_type2]:
            if s_type in self.file_ops_type1:
                s = Request(s_type, self.foo, FileHandle(['dir', 'file1.txt']))
            else:
                s = Request(s_type, self.foo, FileHandle(['dir']), 'file1.txt')

            for r_type in self.dir_ops:
                r = Request(r_type, self.foo, FileHandle([]), 'bar')
                self.assertTrue(s.commutes_with(r))
                self.assertTrue(r.commutes_with(s))

                r = Request(r_type, self.foo, FileHandle([]), 'dir')
                # print(s_type.name, r_type.name, '...', end='', flush=True)
                self.assertFalse(s.commutes_with(r))
                self.assertFalse(r.commutes_with(s))
                # print('Passed', flush=True)



if __name__ == '__main__':
    unittest.main()
