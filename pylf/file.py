"""File handling.

Provides the `File` resource and corresponding view.
"""

from pyramid.response import FileResponse


class File:
    """Resource representing files."""
    def __init__(self, dentry, backend):
        self.dentry = dentry
        self.backend = backend


def file_(context, request):
    """View for file resources.

    Returns the contents of the file.
    """
    return FileResponse(context.dentry.path, request=request)


def includeme(config):
    """Setup function.

    Configures the file view.
    """
    config.add_view(
        file_,
        context=File,
    )
