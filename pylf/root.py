"""Route of the resource tree.

Provides the `Root` resource and matching view. The root view itself
redirects to the "mounts" resource.
"""

from pyramid.httpexceptions import HTTPSeeOther

from .mounts import Mounts


class Root(dict):
    """Root of the resource tree.

    Children:
      * Mounts - configured mount points.
    """
    __name__ = ""

    def __init__(self, settings):
        dict.__init__(
            self,
            mounts=Mounts.from_settings(settings),
        )


def root(request):
    """Root view.

    Redirects to the "mounts" view.
    """
    url = request.resource_url(request.root, "mounts", "")
    return HTTPSeeOther(url)


def includeme(config):
    r = Root(config.get_settings())
    config.set_root_factory(lambda _request: r)
    config.add_view(
        root,
        context=Root, 
    )
