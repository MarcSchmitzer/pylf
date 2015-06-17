"""Filesystem-backend.

Note that this has some limitations because all files are necessarily
owned by the user running the application.
"""

import os
import stat

from .. import dentry


def listdir(dentry):
    """Generates `Dentry` instances for the children of `path`.
    """
    for item in sorted(os.listdir(dentry.path), key=lambda s: s.lower()):
        yield get_dentry(os.path.join(dentry.path, item))


def get_child(dentry, name):
    return get_dentry(os.path.join(dentry.path, name))


def get_dentry(path):
    path = os.path.expanduser(path)
    stat_res = os.stat(path, follow_symlinks=False)
    if stat_res.st_mode & stat.S_IFDIR:
        return dentry.DirectoryDentry(path)
    return dentry.FileDentry(path, stat_res.st_size)
