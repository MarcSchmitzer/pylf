"""Utility functions."""

from jinja2 import Markup


_size_suffixes = ("B", "KB", "MB", "GB", "TB", "PB")


def fmt_size(sz):
    """Generate a human-readable representation of the bytes value `sz`.

    Converts the value to largest sensible unit and returns a string
    containing the value rounded to reasonable precision and the unit.

    Returns an empty string if `sz` is `None`.
    """
    if sz is None:
        return ""
    i = iter(_size_suffixes)
    sfx = next(i)
    while sz > 1024:
        sz /= 1024.0
        sfx = next(i)
    return Markup("{:g}&nbsp;{:s}".format(round(sz, 2), sfx))


def includeme(config):
    """Setup function.

    Registers:
      * `fmt_size` as a jinja filter
    """
    j2env = config.get_jinja2_environment()
    j2env.filters["fmt_size"] = fmt_size
