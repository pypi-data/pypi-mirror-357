import unittest
from fs.memoryfs import MemoryFS
from fs.filefs import FileFS
from fs.errors import ResourceNotFound, Unsupported

class TestFileFS(unittest.TestCase):
    def setUp(self):
        # Create an in-memory filesystem and files
        self.memfs = MemoryFS()
        self.memfs.writetext("foo.txt", "foo")
        self.memfs.makedir("foo")
        self.memfs.writetext("foo/bar.txt", "bar")
        self.memfs.writetext("log.txt", "")
        self.filefs = FileFS()
        self.filefs.add_file("foo.txt", self.memfs)
        self.filefs.add_file("foo/bar.txt", self.memfs, name="foobar.txt")
        self.filefs.add_file("log.txt", self.memfs)

    def tearDown(self):
        self.memfs.close()

    def test_listdir(self):
        self.assertListEqual(self.filefs.listdir("/"), ["foo.txt", "foobar.txt", "log.txt"])

    def test_getinfo(self):
        self.filefs.getinfo("foo.txt")
        self.filefs.getinfo("/foo.txt")

    def test_read_file(self):
        with self.filefs.openbin("foo.txt") as f:
            self.assertEqual(f.read(), b"foo")
        with self.filefs.openbin("foobar.txt") as f:
            self.assertEqual(f.read(), b"bar")

    def test_file_not_found(self):
        with self.assertRaises(ResourceNotFound):
            self.filefs.openbin("nofile.txt")

    def test_write_file(self):
        with self.filefs.openbin("log.txt", mode="wb") as f:
            f.write(b"new content")
        with self.memfs.openbin("log.txt") as f:
            self.assertEqual(f.read(), b"new content")

    def test_write_new_file(self):
        with self.assertRaises(ResourceNotFound):
            with self.filefs.openbin("new.txt", mode="wb") as f:
                f.write(b"new content")

    def test_add_dir(self):
        with self.assertRaises(Unsupported):
            self.filefs.add_file("foo", self.memfs)
    

if __name__ == "__main__":
    unittest.main()
