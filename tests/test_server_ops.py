import unittest
from NFS.proc import NFSPROC
from NFS.fattr import FileAttribute
from NFS.fhandle import FileHandle
from server import Server


class ServerFileOperations(unittest.TestCase):
    def setUp(self):
        self.server = Server()

    def test_invalid_lookup(self):
        with self.assertRaises(FileNotFoundError):
            self.server.lookup(FileHandle([]), 'bar.txt')
            self.server.lookup(FileHandle(['/']), 'foo.txt')

    def test_append(self):
        fhandle, fattr = self.server.lookup(FileHandle([]), 'foo.txt')
        self.server.write(fhandle, 0, "Hello, world!")
        fattr, res = self.server.read(fhandle, 0, 100)

        self.assertEqual(fattr.size, len("Hello, world!"), "File length mismatch")
        self.assertEqual(res, "Hello, world!", "File content mismatch")

    def test_overwite(self):
        fhandle, fattr = self.server.lookup(FileHandle([]), 'foo.txt')
        self.server.write(fhandle, 0, "Hello, world!")
        self.server.write(fhandle, 2, "abcdefg")
        fattr, res = self.server.read(fhandle, 0, 100)

        self.assertEqual(fattr.size, len("Heabcdefgrld!"), "File length mismatch")
        self.assertEqual(res, "Heabcdefgrld!", "File content mismatch")

    def test_long_append(self):
        fhandle, fattr = self.server.lookup(FileHandle([]), 'foo.txt')
        self.server.write(fhandle, 0, "a")
        self.server.write(fhandle, 9, "b")
        fattr, res = self.server.read(fhandle, 0, 100)

        self.assertEqual(fattr.size, 10, "File length mismatch")
        self.assertEqual(res, "a\0\0\0\0\0\0\0\0b", "File content mismatch")

if __name__ == '__main__':
    unittest.main()
