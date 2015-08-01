"""File handling.

Provides the `File` resource and corresponding view.
"""

class File:
    """Resource representing files."""
    def __init__(self, dentry):
        self.mount = dentry.mount
        self.path = dentry.path
        self.stat_res = dentry.stat_res
    
    def make_response(self, request):
        return self.mount.backend.file_response(self.path, request)


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
