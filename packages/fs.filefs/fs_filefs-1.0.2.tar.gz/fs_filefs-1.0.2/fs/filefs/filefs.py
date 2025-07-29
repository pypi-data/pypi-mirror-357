from fs.base import FS
from fs.info import Info
from fs.errors import ResourceNotFound, ResourceReadOnly, Unsupported
from fs.path import basename, normpath
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
        path = normpath(path)
        if fs.isdir(path):
            raise Unsupported(path)
        self._files[normpath(name or basename(path))] = (fs, path)

    def remove_file(self, name):
        if name in self._files:
            del self._files[normpath(name)]

    def listdir(self, path):
        if path != "/":
            raise ResourceNotFound(path)
        return list(self._files.keys())

    def _delegate(self, path) -> tuple[FS, str]:
        path = normpath(path)
        if path not in self._files:
            raise ResourceNotFound(path)
        return self._files[path]

    def openbin(self, path, mode="r", **kwargs):
        fs, dst_path = self._delegate(path)
        return fs.openbin(dst_path, mode=mode, **kwargs)

    def getinfo(self, path, namespaces=None):
        fs, dst_path = self._delegate(path)
        return fs.getinfo(dst_path, namespaces)

    def setinfo(self, path, info):
        fs, dst_path = self._delegate(path)
        return fs.setinfo(dst_path, info)

    def makedir(self, path, permissions=None, recreate=False):
        raise Unsupported(path)

    def remove(self, path):
        raise Unsupported(path)

    def removedir(self, path):
        raise Unsupported(path)