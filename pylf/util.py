"""Utility functions."""

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


def includeme(config):
    """Setup function.

    Registers:
      * `fmt_size` as a jinja filter
    """
    j2env = config.get_jinja2_environment()
    j2env.filters["fmt_size"] = fmt_size
