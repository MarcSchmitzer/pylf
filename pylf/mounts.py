"""Mounts level of the hierarchy.

Provides the `Mounts` resource type and matching view. The `Mounts`
resource is the top-level resource type (below the root) and contains
all configured mount-points.
"""

import os

from pyramid.settings import aslist

from .directory import Directory
from .mount import Mount


class Mounts:
    @classmethod
    def from_settings(cls, settings):
        res = {}
        for path in aslist(settings.get("mounts_directories", "")):
            for entry in os.listdir(path):
                epath = os.path.join(path, entry)
                if entry.endswith(".conf") and os.path.isfile(epath):
                    mount = Mount.from_file(epath)
                    res[mount.name] = mount
        return cls(res)

    def __init__(self, items):
        self._items = items

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self._items)

    def __getitem__(self, key):
        mount = self._items[key]
        return Directory.make_root(mount)

    def items(self):
        return self._items.items()


def mounts(request):
    return {
        "mounts": request.root["mounts"],
    }


def includeme(config):
    config.add_view(
        mounts,
        context=Mounts,
        renderer="templates/mounts.jinja2",
    )
