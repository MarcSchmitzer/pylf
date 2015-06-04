"""Directory-level of the hierarchy.

Provides the `Directory` resource and its subtype `Mount` and a
corresponding view.
"""

import os

from configparser import SafeConfigParser
from urllib.parse import urlparse, ParseResult

from pyramid.httpexceptions import HTTPNotFound, HTTPSeeOther
from pyramid.settings import asbool

from .dentry import DirectoryDentry
from .file import File
from .plugins import Plugins


class Directory:
    """Resource type for directories.

    Child resources are either instances of this class or `file.File`.
    """
    is_root = False

    def __init__(self, dentry, backend):
        self.dentry = dentry
        self.backend = backend

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.dentry)

    def __getitem__(self, key):
        try:
            dentry = self.dentry.get_child(key)
        except FileNotFoundError:
            raise HTTPNotFound(key)

        if isinstance(dentry, DirectoryDentry):
            return Directory(dentry, backend=self.backend)
        return File(dentry, backend=self.backend)

    @property
    def path(self):
        """The path of the directory."""
        return self.dentry.path


class Mount(Directory):
    """Resource type for the top-level directory of a mount."""
    is_root = True
    backends = Plugins("pylf.backends")

    @classmethod
    def from_file(cls, path):
        """Create an instance based on the configuration file at `path`."""
        name = os.path.basename(path).split(".", 1)[0]
        parser = SafeConfigParser()
        parser.read([path])
        cfg = {}
        for section in parser.sections():
            items = parser.items(section)
            if section == "general":
                cfg.update(items)
            else:
                cfg[section] = dict(items)
        return cls(name, cfg)

    def __init__(self, name, cfg):
        backend = self.backends[cfg["backend"]]
        Directory.__init__(
            self,
            backend.get_dentry(cfg["path"]),
            backend,
        )
        self.config = cfg
        self.name = name


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
        'dentries': context.backend.listdir(context.path),
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
