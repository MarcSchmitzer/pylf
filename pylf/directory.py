"""Directory-level of the hierarchy.

Provides the `Directory` resource and its subtype `Mount` and a
corresponding view.
"""

from urllib.parse import urlparse, ParseResult

from pyramid.httpexceptions import HTTPNotFound, HTTPSeeOther
from pyramid.settings import asbool

from .dentry import DirectoryDentry
from .file import File


class Directory:
    """Resource type for directories.

    Child resources are either instances of this class or `file.File`.
    """
    is_root = False

    def __init__(self, mount, dentry=None):
        self.mount = mount
        if not dentry:
            self.is_root = True
            dentry = mount.root
        self.dentry = dentry

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.dentry)

    def __getitem__(self, key):
        try:
            dentry = self.dentry.get_child(key)
        except FileNotFoundError:
            raise HTTPNotFound(key)

        if isinstance(dentry, DirectoryDentry):
            return Directory(self.mount, dentry)
        return File(self.mount, dentry)

    @property
    def path(self):
        """The path of the directory."""
        return self.dentry.path


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
        'dentries': context.mount.backend.listdir(context.path),
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
        permission="browse",
    )
