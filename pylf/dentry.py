
from mimetypes import guess_type


class Dentry:
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.path)


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
    size = None

    @property
    def relpath(self):
        return self.name + "/"
