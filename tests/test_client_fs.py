import unittest
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

if __name__ == '__main__':
    unittest.main()
