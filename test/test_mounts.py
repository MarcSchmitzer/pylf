
from pyramid.testing import DummyRequest

from pytest import fixture

import pylf.mounts
from pylf.directory import Directory
from pylf.mount import Mount


CONFIG = """
[backend]
type = fs
path = {root}

[authentication]
type = inline
users = {{}}

[auth]
realm = AUTH_REALM
"""


@fixture
def environ(tmpdir):
    confpath = tmpdir.join("mounts.d")
    confpath.ensure_dir()
    
    root = tmpdir.join("root")
    root.ensure_dir()

    mount_name = "test"
    with confpath.join("{}.conf".format(mount_name)).open("w") as f:
        f.write(CONFIG.format(
            root=root,
        ))

    settings = {
        "mounts_directories": str(confpath),
    }
    
    return {
        "mount_name": mount_name,
        "confpath": confpath,
        "root": root,
        "settings": settings,
    }


def test_from_settings(environ):
    cut = pylf.mounts.Mounts.from_settings(environ["settings"])
    mount_name = environ["mount_name"]
    assert mount_name in repr(cut)
    child = cut[mount_name]
    assert isinstance(child, Directory)
    assert child.name == mount_name
    
    items = list(cut.items())
    assert len(items) == 1
    assert items[0][0] == mount_name
    mount = items[0][1]
    assert isinstance(mount, Mount)
    assert mount.name == mount_name


def test_view():
    mounts = object()
    req = DummyRequest(root={
        "mounts": mounts,
    })
    resp = pylf.mounts.mounts(req)
    assert resp["mounts"] is mounts


def test_includeme(testconfig):
    testconfig.include(pylf.mounts)
