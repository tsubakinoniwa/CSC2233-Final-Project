import json
import unittest
from NFS.stat import Stat
from sim.server import Server
from sim.client_filesys import ClientFileSystem


class ClientFileSystemOperations(unittest.TestCase):
    def setUp(self):
        self.server = Server()
        self.fs = ClientFileSystem(self.server)

    def test_open_invalid_file(self):
        gen = self.fs.open('/bar.txt')

        req = next(gen)
        resp = req.serve()

        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)

        fd = cm.exception.value
        self.assertEqual(fd, -1)

    def test_open_valid_file(self):
        gen = self.fs.open('/foo.txt')

        req = next(gen)
        resp = req.serve()

        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)

        fd = cm.exception.value
        self.assertNotEqual(fd, -1)

        return fd

    def test_write(self, fd=-1, s=None, test=True):
        if s is None:
            s = "Hello, world!"

        if fd == -1:
            fd = self.test_open_valid_file()
        gen = self.fs.write(fd, s)

        req = next(gen)
        resp = req.serve()
        self.assertEqual(len(resp), 2)

        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)
        self.assertTrue(cm.exception.value)

        if test:
            bytes = self.server.root.files['foo.txt'].bytes
            self.assertEqual(s, ''.join(bytes))

    def test_consecutive_write(self):
        fd = self.test_open_valid_file()
        self.test_write(fd=fd, s="abc", test=True)
        self.test_write(fd=fd, s="def", test=False)

        bytes = self.server.root.files['foo.txt'].bytes
        self.assertEqual("abcdef", ''.join(bytes))

    def test_read(self):
        s = "testing read"
        self.test_write(s=s)

        fd = self.test_open_valid_file()
        gen = self.fs.read(fd, 100)
        req = next(gen)
        resp = req.serve()

        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)
        self.assertEqual(cm.exception.value, s)

    def test_append(self):
        s1 = "abc"
        s2 = "Hello, world!"
        self.test_write(s=s1)

        fd = self.test_open_valid_file()
        gen = self.fs.append(fd, s2)

        req = next(gen)
        resp = req.serve()
        self.assertEqual(len(resp), 2)

        req = gen.send(resp)
        resp = req.serve()
        self.assertEqual(len(resp), 2)
        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)
        self.assertTrue(cm.exception.value)

        bytes = self.server.root.files['foo.txt'].bytes
        self.assertEqual(s1+s2, ''.join(bytes))

    def test_mkdir(self):
        gen = self.fs.mkdir("/dir")

        req = next(gen)
        resp = req.serve()
        self.assertEqual(len(resp), 3)
        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)
        self.assertTrue(cm.exception.value)
        self.assertEqual(json.loads(self.server.to_json()), {
            'foo.txt': '', 'dir': {}
        })

        gen = self.fs.mkdir("/foo.txt")

        req = next(gen)
        resp = req.serve()
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0], Stat.NFSERR_EXIST)
        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)
        self.assertFalse(cm.exception.value)
        self.assertEqual(json.loads(self.server.to_json()), {
            'foo.txt': '', 'dir': {}
        })

        gen = self.fs.mkdir("/dir/dirdir")

        req = next(gen)
        resp = req.serve()
        self.assertEqual(len(resp), 3)
        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)
        self.assertTrue(cm.exception.value)
        self.assertEqual(json.loads(self.server.to_json()), {
            'foo.txt': '', 'dir': {'dirdir': {}}
        })

    def test_rmdir(self):
        self.test_mkdir()
        gen = self.fs.rmdir("/dir")

        req = next(gen)
        resp = req.serve()
        self.assertEqual(resp, Stat.NFSERR_NOTEMPTY)
        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)
        self.assertFalse(cm.exception.value)
        self.assertEqual(json.loads(self.server.to_json()), {
            'foo.txt': '', 'dir': {'dirdir': {}}
        })

        gen = self.fs.rmdir("/dirdir")

        req = next(gen)
        resp = req.serve()
        self.assertEqual(resp, Stat.NFSERR_NOENT)
        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)
        self.assertFalse(cm.exception.value)
        self.assertEqual(json.loads(self.server.to_json()), {
            'foo.txt': '', 'dir': {'dirdir': {}}
        })

        gen = self.fs.rmdir("/dir/dirdir")

        req = next(gen)
        resp = req.serve()
        self.assertEqual(resp, Stat.NFS_OK)
        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)
        self.assertTrue(cm.exception.value)
        self.assertEqual(json.loads(self.server.to_json()), {
            'foo.txt': '', 'dir': {}
        })

    def test_create(self):
        gen = self.fs.create('foo.txt')
        req = next(gen)
        resp = req.serve()

        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0], Stat.NFSERR_EXIST)
        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)
        self.assertEqual(cm.exception.value, -1)
        self.assertEqual(json.loads(self.server.to_json()), {
            'foo.txt': ''
        })

        gen = self.fs.create('bar.txt')
        req = next(gen)
        resp = req.serve()

        self.assertEqual(len(resp), 3)
        self.assertEqual(resp[0], Stat.NFS_OK)
        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)
        self.assertEqual(cm.exception.value, 0)
        self.assertEqual(json.loads(self.server.to_json()), {
            'foo.txt': '', 'bar.txt': ''
        })

    def test_remove(self):
        self.test_create()

        gen = self.fs.remove(2)
        with self.assertRaises(StopIteration) as cm:
            next(gen)
        self.assertFalse(cm.exception.value)
        self.assertEqual(json.loads(self.server.to_json()), {
            'foo.txt': '', 'bar.txt': ''
        })

        gen = self.fs.remove(0)
        req = next(gen)
        resp = req.serve()
        self.assertEqual(resp, Stat.NFS_OK)
        with self.assertRaises(StopIteration) as cm:
            gen.send(resp)
        self.assertTrue(cm.exception.value)
        self.assertEqual(json.loads(self.server.to_json()), {
            'foo.txt': ''
        })

if __name__ == '__main__':
    unittest.main()
