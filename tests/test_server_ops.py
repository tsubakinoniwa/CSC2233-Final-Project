import unittest
import json
from NFS.fhandle import FileHandle
from NFS.stat import Stat
from sim.server import Server


class ServerFileOperations(unittest.TestCase):
    def setUp(self):
        self.server = Server()

    def test_getattr(self):
        resp = self.server.getattr(FileHandle(['foo.txt']))
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0], Stat.NFS_OK)

    def test_invalid_lookup(self):
        resp = self.server.lookup(FileHandle([]), 'bar.txt')
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0], Stat.NFSERR_NOENT)

        resp = self.server.lookup(FileHandle(['/']), 'foo.txt')
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0], Stat.NFSERR_NOENT)

    def test_valid_lookup(self):
        resp = self.server.lookup(FileHandle([]), 'foo.txt')
        self.assertEqual(len(resp), 3)
        self.assertEqual(resp[0], Stat.NFS_OK)

    def test_append(self):
        resp = self.server.lookup(FileHandle([]), 'foo.txt')
        self.assertEqual(len(resp), 3)

        _, fhandle, fattr = resp
        self.server.write(fhandle, 0, "Hello, world!")

        resp = self.server.read(fhandle, 0, 100)
        self.assertEqual(len(resp), 3)
        _, fattr, res = resp

        self.assertEqual(fattr.size, len("Hello, world!"), "File length mismatch")
        self.assertEqual(res, "Hello, world!", "File content mismatch")

    def test_overwrite(self):
        resp = self.server.lookup(FileHandle([]), 'foo.txt')
        self.assertEqual(len(resp), 3)

        _, fhandle, fattr = resp
        self.server.write(fhandle, 0, "Hello, world!")
        self.server.write(fhandle, 2, "abcdefg")

        resp = self.server.read(fhandle, 0, 100)
        self.assertEqual(len(resp), 3)

        _, fattr, res = resp
        self.assertEqual(fattr.size, len("Heabcdefgrld!"), "File length mismatch")
        self.assertEqual(res, "Heabcdefgrld!", "File content mismatch")

    def test_long_append(self):
        resp = self.server.lookup(FileHandle([]), 'foo.txt')
        self.assertEqual(len(resp), 3)

        _, fhandle, fattr = resp
        self.server.write(fhandle, 0, "a")
        self.server.write(fhandle, 9, "b")

        resp = self.server.read(fhandle, 0, 100)
        self.assertEqual(len(resp), 3)

        _, fattr, res = resp
        self.assertEqual(fattr.size, 10, "File length mismatch")
        self.assertEqual(res, "a\0\0\0\0\0\0\0\0b", "File content mismatch")

    def test_invalid_create(self):
        resp = self.server.create(FileHandle([]), 'foo.txt')
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0], Stat.NFSERR_EXIST)

    def test_invalid_remove(self):
        resp = self.server.remove(FileHandle([]), 'bar.txt')
        self.assertEqual(resp, Stat.NFSERR_NOENT)

    def test_valid_flat_create(self):
        resp = self.server.create(FileHandle([]), 'bar.txt')
        self.assertEqual(len(resp), 3)
        self.assertEqual(resp[0], Stat.NFS_OK)

        _, fhandle, fattr = resp
        self.assertEqual(fhandle.path, ['bar.txt'])
        self.assertEqual(len(self.server.root.files), 2)

    def test_valid_flat_remove(self):
        resp = self.server.remove(FileHandle([]), 'foo.txt')
        self.assertEqual(resp, Stat.NFS_OK)
        self.assertEqual(len(self.server.root.files), 0)

    def test_valid_mkdir(self):
        resp = self.server.mkdir(FileHandle([]), 'dir')
        self.assertEqual(len(resp), 3)
        self.assertEqual(resp[0], Stat.NFS_OK)

        _, fhandle, fattr = resp
        self.assertEqual(fhandle.path, ['dir'])
        self.assertEqual(json.loads(self.server.to_json()),
                         {'dir': {}, 'foo.txt': ""})

    def test_complicated_create(self):
        resp = self.server.create(FileHandle([]), 'base1.txt')
        self.assertEqual(len(resp), 3)
        self.assertEqual(resp[0], Stat.NFS_OK)

        _, fhandle, fattr = resp
        self.assertEqual(fhandle.path, ['base1.txt'])

        resp = self.server.create(FileHandle([]), 'base2.txt')
        self.assertEqual(len(resp), 3)
        self.assertEqual(resp[0], Stat.NFS_OK)

        _, fhandle, fattr = resp
        self.assertEqual(fhandle.path, ['base2.txt'])
        self.assertEqual(json.loads(self.server.to_json()),
                         {'foo.txt': '', 'base1.txt': '', 'base2.txt': ''})


        resp = self.server.mkdir(FileHandle([]), 'dir')
        self.assertEqual(len(resp), 3)
        self.assertEqual(resp[0], Stat.NFS_OK)

        _, fhandle, fattr = resp
        self.assertEqual(fhandle.path, ['dir'])
        self.assertEqual(json.loads(self.server.to_json()),
                         {'dir': {}, 'foo.txt': '', 'base1.txt': '',
                          'base2.txt': ''})

        resp = self.server.create(FileHandle(['dir']), 'wow.txt')
        self.assertEqual(len(resp), 3)
        self.assertEqual(resp[0], Stat.NFS_OK)

        _, fhandle, fattr = resp
        self.assertEqual(fhandle.path, ['dir', 'wow.txt'])
        self.assertEqual(json.loads(self.server.to_json()),
                         {'dir': {'wow.txt': ''},'foo.txt': '',
                          'base1.txt': '', 'base2.txt': ''})

        resp = self.server.mkdir(FileHandle(['dir']), 'dirdir')
        self.assertEqual(len(resp), 3)
        self.assertEqual(resp[0], Stat.NFS_OK)

        _, fhandle, fattr = resp
        self.assertEqual(fhandle.path, ['dir', 'dirdir'])
        self.assertEqual(json.loads(self.server.to_json()),
                         {'dir': {'wow.txt': '', 'dirdir': {}},'foo.txt': '',
                          'base1.txt': '', 'base2.txt': ''})

    def test_complicated_remove(self):
        self.test_complicated_create()

        resp = self.server.rmdir(FileHandle(['dir', 'dirdir']), 'dirdirdir')
        self.assertEqual(resp, Stat.NFSERR_NOENT)

        resp = self.server.rmdir(FileHandle(['dir', 'wow.txt', 'a.txt']), 'base1.txt')
        self.assertEqual(resp, Stat.NFSERR_NOENT)

        resp = self.server.rmdir(FileHandle(['dir', 'wow.txt']), 'base1.txt')
        self.assertEqual(resp, Stat.NFSERR_NOTDIR)

        resp = self.server.rmdir(FileHandle(['dir']), 'wow.txt')
        self.assertEqual(resp, Stat.NFSERR_NOTDIR)

        resp = self.server.rmdir(FileHandle(['dir']), 'dirdir')
        self.assertEqual(resp, Stat.NFS_OK)
        self.assertEqual(json.loads(self.server.to_json()),
                         {'dir': {'wow.txt': ''},'foo.txt': '',
                          'base1.txt': '', 'base2.txt': ''})

        resp = self.server.rmdir(FileHandle([]), 'dir')
        self.assertEqual(resp, Stat.NFSERR_NOTEMPTY)

        resp = self.server.remove(FileHandle(['dir']), 'wow.txt')
        self.assertEqual(resp, Stat.NFS_OK)

        resp = self.server.remove(FileHandle([]), 'dir')
        self.assertEqual(resp, Stat.NFSERR_ISDIR)


    def test_dir_ops(self):
        self.test_valid_mkdir()
        resp = self.server.create(FileHandle(['dir']), 'bar.txt')
        self.assertEqual(len(resp), 3)
        self.assertEqual(resp[0], Stat.NFS_OK)

        _, fhandle, fattr = resp
        self.assertEqual(fhandle.path, ['dir', 'bar.txt'])
        self.assertEqual(json.loads(self.server.to_json()),
                         {'dir': {'bar.txt': ''}, 'foo.txt': ''})

        resp = self.server.mkdir(FileHandle([]), 'dirdir')
        self.assertEqual(len(resp), 3)
        self.assertEqual(resp[0], Stat.NFS_OK)

        _, fhandle, fattr = resp
        self.assertEqual(fhandle.path, ['dirdir'])
        self.assertEqual(json.loads(self.server.to_json()),
                         {'dir': {'bar.txt': ''}, 'foo.txt': '', 'dirdir': {}})

        resp = self.server.rmdir(FileHandle([]), 'dir')
        self.assertEqual(resp, Stat.NFSERR_NOTEMPTY)
        self.assertEqual(json.loads(self.server.to_json()),
                         {'dir': {'bar.txt': ''}, 'foo.txt': '', 'dirdir': {}})

        resp = self.server.rmdir(FileHandle([]), 'dirdir')
        self.assertEqual(resp, Stat.NFS_OK)
        self.assertEqual(json.loads(self.server.to_json()),
                         {'dir': {'bar.txt': ''}, 'foo.txt': ''})



if __name__ == '__main__':
    unittest.main()
