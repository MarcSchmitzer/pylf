
from pyramid.request import Request
from pyramid.interfaces import IRequestExtensions

from pytest import fixture, mark

import pylf.icons


MIMETYPES = [
    ("text", "plain", "text-plain.png"),
    ("image", "jpeg", "image-jpeg.png"),
    ("inode", "directory", "inode-directory.png"),
    ("audio", "x-generic", "audio-x-generic.png"),
    ("unknown", None, "unknown.png"),
]


@fixture
def icons_dir(tmpdir):
    for mtype, subtype, fname in MIMETYPES:
        with tmpdir.join(fname).open("w"):
            pass
    return tmpdir


def test_load_mimetypes(icons_dir):
    res = pylf.icons.load_mimetypes(str(icons_dir))
    for mtype, subtype, fname in MIMETYPES:
        assert (mtype, subtype) in res
        assert res[(mtype, subtype)] == fname
    assert len(res) == len(MIMETYPES)


def test_from_settins(icons_dir):
    settings = {
        "icons_path": str(icons_dir),
    }
    cut = pylf.icons.Icons.from_settings(settings)
    assert cut.path == str(icons_dir)


@mark.parametrize(
    ("mtype", "expected"),
    [
        ("text/plain", "text-plain.png"),
        ("audio/vorbis", "audio-x-generic.png"),
        ("video/ogg", "unknown.png"),
    ],
)
def test_for_mimetype(icons_dir, mtype, expected):
    cut = pylf.icons.Icons(str(icons_dir))
    assert cut.for_mimetype(mtype) == expected


def test_includeme(testconfig, icons_dir):
    testconfig.get_settings()["icons_path"] = str(icons_dir)
    testconfig.include(pylf.icons)
    testconfig.commit()
    req_exts = testconfig.registry.queryUtility(IRequestExtensions)
    req = Request({})
    req._set_extensions(req_exts)
    assert hasattr(req, "icon_path")
    icon_path = req.icon_path
    assert icon_path((None, None)) == "/icons/unknown.png"
    assert icon_path(("text/plain", None)) == "/icons/text-plain.png"
