import unittest
from NFS.fhandle import FileHandle
from NFS.stat import Stat
from sim.server import Server


class ServerFileOperations(unittest.TestCase):
    def setUp(self):
        self.server = Server()

    def test_invalid_lookup(self):
        resp = self.server.lookup(FileHandle([]), 'bar.txt')
        self.assertEqual(len(resp), 1, "Returning more than expected")
        self.assertEqual(resp[0], Stat.NFSERR_NOENT)

        resp = self.server.lookup(FileHandle(['/']), 'foo.txt')
        self.assertEqual(len(resp), 1, "Returning more than expected")
        self.assertEqual(resp[0], Stat.NFSERR_NOENT)

    def test_append(self):
        resp = self.server.lookup(FileHandle([]), 'foo.txt')
        self.assertEqual(len(resp), 3, "Returning less than expected")

        _, fhandle, fattr = resp
        self.server.write(fhandle, 0, "Hello, world!")

        resp = self.server.read(fhandle, 0, 100)
        self.assertEqual(len(resp), 3, "Returning less than expected")
        _, fattr, res = resp

        self.assertEqual(fattr.size, len("Hello, world!"), "File length mismatch")
        self.assertEqual(res, "Hello, world!", "File content mismatch")

    def test_overwrite(self):
        resp = self.server.lookup(FileHandle([]), 'foo.txt')
        self.assertEqual(len(resp), 3, "Returning less than expected")

        _, fhandle, fattr = resp
        self.server.write(fhandle, 0, "Hello, world!")
        self.server.write(fhandle, 2, "abcdefg")

        resp = self.server.read(fhandle, 0, 100)
        self.assertEqual(len(resp), 3, "Returning less than expected")

        _, fattr, res = resp
        self.assertEqual(fattr.size, len("Heabcdefgrld!"), "File length mismatch")
        self.assertEqual(res, "Heabcdefgrld!", "File content mismatch")

    def test_long_append(self):
        resp = self.server.lookup(FileHandle([]), 'foo.txt')
        self.assertEqual(len(resp), 3, "Returning less than expected")

        _, fhandle, fattr = resp
        self.server.write(fhandle, 0, "a")
        self.server.write(fhandle, 9, "b")

        resp = self.server.read(fhandle, 0, 100)
        self.assertEqual(len(resp), 3, "Returning less than expected")

        _, fattr, res = resp
        self.assertEqual(fattr.size, 10, "File length mismatch")
        self.assertEqual(res, "a\0\0\0\0\0\0\0\0b", "File content mismatch")


if __name__ == '__main__':
    unittest.main()
