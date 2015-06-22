"""Directory-level of the hierarchy.

Provides the `Directory` resource and its subtype `Mount` and a
corresponding view.
"""

from pathlib import PurePath as Path
from urllib.parse import urlparse, ParseResult

import pyramid.httpexceptions as httpexceptions
from pyramid.settings import asbool

from .dentry import DirectoryDentry
from .file import File
from .util import str_to_id, urlmod


class Directory:
    """Resource type for directories.

    Child resources are either instances of this class or `file.File`.
    """
    def __init__(self, dentry):
        self.dentry = dentry
        self.is_root = (self.dentry.path == Path())

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.dentry)

    def __getitem__(self, key):
        try:
            dentry = self.dentry.get_child(key)
        except FileNotFoundError:
            return httpexceptions.HTTPNotFound(key)

        if isinstance(dentry, DirectoryDentry):
            return Directory(dentry)
        return File(dentry)

    @property
    def name(self):
        return (
            self.dentry.mount.name
            if self.is_root
            else self.dentry.path.name
        )

    @property
    def mount(self):
        return self.dentry.mount

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
        raise httpexceptions.HTTPSeeOther(url.geturl())

    parents = []
    parent_parts = [
        context.dentry.mount.name
    ]
    parent_parts.extend(context.dentry.path.parts[:-1])
    num_parents = len(parent_parts)
    for lvl, part in enumerate(parent_parts):
        parents.append((part, (num_parents-lvl)*"../"))

    return {
        'dentry': context.dentry,
        'parents': parents,
        'children': context.dentry.listdir(),
        'show_hidden': asbool(request.params.get('show_hidden')),
    }


def upload_file(context, request):
    dstname = request.params["filename"]
    if not dstname:
        dstname = request.params['content'].filename
    try:
        dentry = context.dentry.get_child(dstname)
    except FileNotFoundError:
        dentry = context.dentry.make_child(dstname)
    else:
        if isinstance(dentry, DirectoryDentry):
            return httpexceptions.HTTPConflict()
        if not request.has_permission("replace_file"):
            return httpexceptions.HTTPForbidden()
    dentry.write(request.params['content'].file)

    url = urlmod(request.url, fragment=str_to_id(dstname))
    return httpexceptions.HTTPSeeOther(url)  # Map to GET


def includeme(config):
    """Setup function.

    Adds the directory view.
    """
    config.add_view(
        directory,
        context=Directory,
        request_method="GET",
        renderer="templates/directory.jinja2",
        permission="browse",
    )
    config.add_view(
        upload_file,
        context=Directory,
        request_method="POST",
        renderer="templates/directory.jinja2",
        permission="create_file",
    )
