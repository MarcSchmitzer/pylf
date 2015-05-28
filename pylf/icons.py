
import os


class Icons:
    @classmethod
    def from_settings(cls, settings):
        return cls(
            path=settings.get("icons_path", ""),
        )

    def __init__(self, path):
        self.path = path
        self.mimetypes = load_mimetypes(path)

    def for_mimetype(self, mtype):
        mtype = tuple(mtype.split("/", 1))
        mimetypes = self.mimetypes
        return (
            mimetypes.get(mtype)
            or mimetypes.get((mtype[0], "x-generic"))
            or mimetypes.get(("unknown", None))
        )


def load_mimetypes(path):
    res = {}
    for entry in os.listdir(path):
        epath = os.path.join(path, entry)
        if entry.endswith(".png") and os.path.isfile(epath):
            basename = entry[:-4]
            if "-" in basename:
                mtype = tuple(basename.split("-", 1))
            else:
                mtype = (basename, None)
            res[mtype] = entry
    return res


def includeme(config):
    icons = Icons.from_settings(config.get_settings())
    config.add_static_view('icons', icons.path)

    def icon_path(request, mimetype):
        mimetype, encoding = mimetype
        if mimetype:
            fname = icons.for_mimetype(mimetype)
        else:
            fname = "unknown.png"
        return request.route_path("__icons/", subpath=fname)
    
    config.add_request_method(icon_path)
