"""Mounts level of the hierarchy.

Provides the `Mounts` resource type and matching view. The `Mounts`
resource is the top-level resource type (below the root) and contains
all configured mount-points.
"""

import os

from pyramid.settings import aslist

from .directory import Mount

class Mounts(dict):
    @classmethod
    def from_settings(cls, settings):
        res = cls()
        for path in aslist(settings.get("mounts_directories", "")):
            for entry in os.listdir(path):
                epath = os.path.join(path, entry)
                if entry.endswith(".conf") and os.path.isfile(epath):
                    mount = Mount.from_file(epath)
                    res[mount.name] = mount
        return res


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
