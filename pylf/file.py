"""File handling.

Provides the `File` resource and corresponding view.
"""

class File:
    """Resource representing files."""
    def __init__(self, dentry):
        self.dentry = dentry


def file_(context, request):
    """View for file resources.

    Returns the contents of the file.
    """
    return context.dentry.make_response(request)


def includeme(config):
    """Setup function.

    Configures the file view.
    """
    config.add_view(
        file_,
        context=File,
    )
