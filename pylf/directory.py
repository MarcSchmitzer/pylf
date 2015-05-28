"""Directory-level of the hierarchy.

Provides the `Directory` resource and its subtype `Mount` and a
corresponding view.
"""

import os
import stat

from configparser import SafeConfigParser
from mimetypes import guess_type
from urllib.parse import urlparse, ParseResult

from pyramid.httpexceptions import HTTPNotFound, HTTPSeeOther
from pyramid.settings import asbool
from .file import File


class Directory(object):
    """Resource type for directories.
    
    Child resources are either instances of this class or `file.File`.
    """
    is_root = False

    def __init__(self, path):
        self.path = path

    def __getitem__(self, key):
        path = os.path.join(self.path, key)
        try:
            stat_res = os.stat(path, follow_symlinks=False)
        except FileNotFoundError:
            raise HTTPNotFound(path)

        if stat_res.st_mode & stat.S_IFDIR:
            return Directory(path)
        return File(path)


class Mount(Directory):
    """Resource type for the top-level directory of a mount.""" 
    is_root = True

    @classmethod
    def from_file(cls, path):
        name = os.path.basename(path).split(".", 1)[0]
        cfg = SafeConfigParser()
        cfg.read([path])
        return cls(name, dict(cfg.items("general")))
    
    def __init__(self, name, cfg):
        Directory.__init__(self, os.path.expanduser(cfg["path"]))
        self.name = name
        self.config = cfg


class Dentry(object):
    """Represents a directory entry during rendering of a
    directory."""
    
    def __init__(self, name, stat_result):
        self.name = name
        self.stat_result = stat_result

    @property
    def hidden(self):
        return self.name.startswith(".")

        
class FileDentry(Dentry):
    """Represents a file during rendering of a directory."""
    
    type = "file"

    _mimetype = None
    _size = None
    
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


class DirectoryDentry(Dentry):
    """Represents a subdirectory during rendering of a directory."""

    type = "directory"
    mimetype = ("inode/directory", None)
    size = None

    @property
    def relpath(self):
        return self.name + "/"


def dentries(path):
    """Generates `Dentry` instances for the children of `path`.
    """
    for item in sorted(os.listdir(path), key=lambda s: s.lower()):
        ipath = os.path.join(path, item)
        st = os.stat(ipath)
        if st.st_mode & stat.S_IFDIR:
            cls = DirectoryDentry
        else:
            cls = FileDentry

        yield cls(
            name=item,
            stat_result=st,
        )


def directory(context, request):
    """Directory view.

    If the request path does not end in a slash, this redirects to the
    fixed path. This should not happen normally, though.
    """
    if not request.path.endswith("/"):
        url = urlparse(request.url)
        url = ParseResult(
            url.scheme,
            url.netloc,
            url.path + "/",
            url.params,
            url.query,
            url.fragment,
        )
        raise HTTPSeeOther(url.geturl())
    return {
        'path': context.path,
        'dentries': dentries(context.path),
        'show_hidden': asbool(request.params.get('show_hidden')),
    }


def includeme(config):
    """Setup function.

    Adds the directory view.
    """
    config.add_view(
        directory,
        context=Directory,
        renderer="templates/directory.jinja2",
    )
