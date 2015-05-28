"""Filesystem-backend.

Note that this has some limitations because all files are necessarily
owned by the user running the application.
"""

import os
import stat

from mimetypes import guess_type

from .. import dentry


class FSDentryMixin:
    @property
    def name(self):
        return os.path.split(self.path)[1]

    @property
    def hidden(self):
        return self.name.startswith(".")


class FileDentry(dentry.FileDentry, FSDentryMixin):
    """Represents a file during rendering of a directory."""

    _mimetype = None

    def __init__(self, path, stat_result):
        dentry.FileDentry.__init__(self, path)
        self.stat_result = stat_result

    @property
    def relpath(self):
        return self.name

    @property
    def mimetype(self):
        if self._mimetype is None:
            self._mimetype = guess_type(self.name, strict=False)
        return self._mimetype

    @property
    def size(self):
        return self.stat_result.st_size


class DirectoryDentry(dentry.DirectoryDentry, FSDentryMixin):
    """Represents a subdirectory during rendering of a directory."""

    @property
    def relpath(self):
        return self.name + "/"

    def get_child(self, name):
        return get_dentry(os.path.join(self.path, name))


def listdir(path):
    """Generates `Dentry` instances for the children of `path`.
    """
    for item in sorted(os.listdir(path), key=lambda s: s.lower()):
        yield get_dentry(os.path.join(path, item))


def get_dentry(path):
    path = os.path.expanduser(path)
    stat_res = os.stat(path, follow_symlinks=False)
    if stat_res.st_mode & stat.S_IFDIR:
        return DirectoryDentry(path)
    return FileDentry(path, stat_res)
