from fs.base import FS
from fs.info import Info
from fs.errors import ResourceNotFound, ResourceReadOnly, Unsupported
from fs.path import basename
from typing import Dict

class FileFS(FS):
    """
    A custom filesystem that allows mounting files from other filesystems.
    """
    _meta = {
        "virtual": True,
        "read_only": False,
        "case_insensitive": False,
    }

    def __init__(self):
        super().__init__()
        self._files: Dict[str, tuple[FS, str]] = {}

    def add_file(self, path: str, fs: FS, name=None):
        """
        Mount a file from another filesystem.
        """
        if fs.isdir(path):
            raise Unsupported(path)
        self._files[name or basename(path)] = (fs, path)

    def remove_file(self, name):
        if name in self._files:
            del self._files[name]

    def listdir(self, path):
        if path != "/":
            raise ResourceNotFound(path)
        return list(self._files.keys())

    def openbin(self, path, mode="r", **kwargs):
        if path not in self._files:
            raise ResourceNotFound(path)
        fs, dst_path = self._files[path]
        return fs.openbin(dst_path, mode=mode, **kwargs)

    def getinfo(self, path, namespaces=None):
        if path not in self._files:
            raise ResourceNotFound(path)
        fs, dst_path = self._files[path]
        return fs.getinfo(dst_path, namespaces)

    def setinfo(self, path, info):
        if path not in self._files:
            raise ResourceNotFound(path)
        fs, dst_path = self._files[path]
        return fs.setinfo(dst_path, info)

    def makedir(self, path, permissions=None, recreate=False):
        raise Unsupported(path)

    def remove(self, path):
        raise Unsupported(path)

    def removedir(self, path):
        raise Unsupported(path)