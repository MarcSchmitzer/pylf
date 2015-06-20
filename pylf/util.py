"""Utility functions."""

from urllib.parse import urlparse

from jinja2 import Markup


_SIZE_SUFFIXES = ("B", "KB", "MB", "GB", "TB", "PB")


def fmt_size(size):
    """Generate a human-readable representation of the bytes value `size`.

    Converts the value to largest sensible unit and returns a string
    containing the value rounded to reasonable precision and the unit.

    Returns an empty string if `size` is `None`.
    """
    if size is None:
        return ""
    i = iter(_SIZE_SUFFIXES)
    sfx = next(i)
    while size > 1024:
        size /= 1024.0
        sfx = next(i)
    return Markup("{:g}&nbsp;{:s}".format(round(size, 2), sfx))


def rel_path(request, abspath):
    """Return a path relative to the current request location for abspath.
    """
    app_path = urlparse(request.application_url).path
    req_path = request.path[len(app_path):].rstrip("/").split("/")
    dst_path = abspath.split("/")

    # get rid of a common prefix
    while req_path and dst_path and req_path[0] == dst_path[0]:
        req_path.pop(0)
        dst_path.pop(0)

    res_path = "/".join([".."] * len(req_path) + dst_path)
    return res_path


def includeme(config):
    """Setup function.

    Registers:
      * `fmt_size` as a jinja filter
      * `rel_path` as a request method
    """
    config.add_request_method(rel_path)
    j2env = config.get_jinja2_environment()
    j2env.filters["fmt_size"] = fmt_size
