"""Directory-level of the hierarchy.

Provides the `Directory` resource and its subtype `Mount` and a
corresponding view.
"""

from pathlib import PurePath as Path
import stat

import pyramid.httpexceptions as httpexceptions
from pyramid.settings import asbool

from .file import File
from .util import str_to_id, urlmod


class Directory:
    """Resource type for directories.

    Child resources are either instances of this class or `file.File`.
    """
    mimetype = ("inode/directory", None)
    size = None

    @classmethod
    def make_root(cls, mount):
        return cls(mount, Path())

    def __init__(self, mount, path):
        self.mount = mount
        self.path = path
        self.is_root = (self.path == Path())

    def __repr__(self):
        return "{}({!r}, {!r})".format(
            type(self).__name__,
            self.mount,
            self.path,
        )

    def __getitem__(self, key):
        try:
            return self.get_child(key)
        except FileNotFoundError:
            raise KeyError(key)

    @property
    def name(self):
        return (
            self.mount.name
            if self.is_root
            else self.path.name
        )

    @property
    def relpath(self):
        return self.name + "/"

    @property
    def hidden(self):
        return self.name.startswith(".")

    def _make_dentry(self, path):
        stat_res = self.mount.backend.stat(path)
        if stat_res.st_mode & stat.S_IFDIR:
            return Directory(self.mount, path)
        return File(self.mount, path, stat_res=stat_res)

    def get_children(self):
        for path in self.mount.backend.listdir(self.path):
            yield self._make_dentry(path)

    def get_child(self, name):
        return self._make_dentry(self.path / name)

    def make_child(self, name, directory=False):
        path = self.path / name
        if directory:
            return Directory(self.mount, path)
        return File(self.mount, path, stat_res=None)


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
        child = context.get_child(dstname)
    except FileNotFoundError:
        child = context.make_child(dstname)
    else:
        if isinstance(child, Directory):
            return httpexceptions.HTTPConflict()
        if not request.has_permission("replace_file"):
            return httpexceptions.HTTPForbidden()
    child.write(request.params['content'].file)

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
