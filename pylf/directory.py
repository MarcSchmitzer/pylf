"""Directory-level of the hierarchy.

Provides the `Directory` resource and its subtype `Mount` and a
corresponding view.
"""

from pathlib import PurePath as Path

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
            raise KeyError(key)

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

    def get_children(self):
        return self.dentry.listdir()

    def get_child(self, name):
        return self.dentry.get_child(name)

    def make_child(self, name, directory=False):
        return self.dentry.make_child(name, directory=directory)


def directory(context, request):
    """Directory view.

    If the request path does not end in a slash, this redirects to the
    fixed path. This should not happen normally, though.
    """
    if not request.path.endswith("/"):
        url = urlmod(request.url, path=request.path + "/")
        raise httpexceptions.HTTPSeeOther(url)

    parents = []
    parent_parts = [
        context.mount.name,
    ]
    parent_parts.extend(context.path.parts[:-1])
    num_parents = len(parent_parts)
    for lvl, part in enumerate(parent_parts):
        parents.append((part, (num_parents-lvl)*"../"))

    children = sorted(
        context.get_children(),
        key=lambda dentry: request.collator.getSortKey(str(dentry.path)),
    )

    return {
        'parents': parents,
        'children': children,
        'show_hidden': asbool(request.params.get('show_hidden')),
    }


def upload_file(context, request):
    dstname = request.params["filename"]
    if not dstname:
        dstname = request.params['content'].filename
    try:
        dentry = context.get_child(dstname)
    except FileNotFoundError:
        dentry = context.make_child(dstname)
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
