
import stat

from mimetypes import guess_type
from pathlib import PurePosixPath as Path

class Dentry:
    def __init__(self, mount, path):
        if isinstance(path, str):
            path = Path(path)
        self.mount = mount
        self.path = path

    def __repr__(self):
        return "{}({!r}, {!r})".format(
            type(self).__name__,
            self.mount,
            self.path,
        )

    @property
    def name(self):
        return self.path.name

    @property
    def hidden(self):
        return self.name.startswith(".")


class FileDentry(Dentry):
    _mimetype = None

    def __init__(self, mount, path, stat_res):
        Dentry.__init__(self, mount, path)
        self.stat_res = stat_res

    @property
    def relpath(self):
        return self.name

    @property
    def size(self):
        return self.stat_res.st_size

    @property
    def mimetype(self):
        if self._mimetype is None:
            self._mimetype = guess_type(self.name, strict=False)
        return self._mimetype

    def make_response(self, request):
        return self.mount.backend.file_response(self.path, request)

    def write(self, fp):
        return self.mount.backend.write_file(self.path, fp)


class DirectoryDentry(Dentry):
    mimetype = ("inode/directory", None)
    size = None

    @property
    def relpath(self):
        return self.name + "/"

    def _make_dentry(self, path):
        stat_res = self.mount.backend.stat(path)
        if stat_res.st_mode & stat.S_IFDIR:
            return DirectoryDentry(self.mount, path)
        return FileDentry(self.mount, path, stat_res=stat_res)

    def listdir(self):
        for path in self.mount.backend.listdir(self.path):
            yield self._make_dentry(path)

    def get_child(self, name):
        """Get a `Dentry` instance for a child of this directory.

        Raises `FileNotFoundError` if the child does not exist.
        """
        return self._make_dentry(self.path / name)

    def make_child(self, name, directory=False):
        """Create a `Dentry` instance for a child of this directory.

        This will work regardless of whether the child or this
        directory exists.

        Args:
          directory (bool): `True` if the child is supposed to
          be a directory.
        """
        if directory:
            return DirectoryDentry(self.mount, self.path / name)
        return FileDentry(self.mount, self.path / name, stat_res=None)


def make_root(mount):
    return DirectoryDentry(mount, Path())
