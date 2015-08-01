"""File handling.

Provides the `File` resource and corresponding view.
"""

from mimetypes import guess_type


class File:
    """Resource representing files."""
    _mimetype = None

    def __init__(self, dentry):
        self.mount = dentry.mount
        self.path = dentry.path
        self.stat_res = dentry.stat_res
    
    def make_response(self, request):
        return self.mount.backend.file_response(self.path, request)

    @property
    def name(self):
        return self.path.name

    @property
    def relpath(self):
        return self.name

    @property
    def size(self):
        return self.stat_res.st_size

    @property
    def hidden(self):
        return self.name.startswith(".")

    @property
    def mimetype(self):
        if self._mimetype is None:
            self._mimetype = guess_type(self.name, strict=False)
        return self._mimetype

    def write(self, fp):
        return self.mount.backend.write_file(self.path, fp)


def file_(context, request):
    """View for file resources.

    Returns the contents of the file.
    """
    return context.make_response(request)


def includeme(config):
    """Setup function.

    Configures the file view.
    """
    config.add_view(
        file_,
        context=File,
    )
