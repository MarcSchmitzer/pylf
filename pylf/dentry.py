
from mimetypes import guess_type


class Dentry:
    def __init__(self, path, size=None):
        self.path = path
        self.size = size

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.path)

    @property
    def name(self):
        return self.path.rsplit('/', 1)[-1]

    @property
    def hidden(self):
        return self.name.startswith(".")


class FileDentry(Dentry):
    _mimetype = None

    @property
    def relpath(self):
        return self.name

    @property
    def mimetype(self):
        if self._mimetype is None:
            self._mimetype = guess_type(self.name, strict=False)
        return self._mimetype


class DirectoryDentry(Dentry):
    mimetype = ("inode/directory", None)

    @property
    def relpath(self):
        return self.name + "/"
