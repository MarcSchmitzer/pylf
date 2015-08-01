
from pathlib import Path
from tempfile import TemporaryFile

from pyramid.httpexceptions import HTTPConflict, HTTPForbidden, HTTPSeeOther
from pyramid.testing import DummyRequest, DummySecurityPolicy
from pytest import fixture, raises

import pyramid.testing as testing

from pylf.backends.fs import FSBackend
from pylf.dentry import DirectoryDentry
from pylf.file import File
from pylf.mount import Mount
from pylf.directory import Directory
from pylf.directory import directory as directory_view
from pylf.directory import upload_file as upload_file_view
from pylf.userdb import UserDB


def dummy_auth(login, password):
    return { "name": "Dummy User" }


@fixture
def testconfig(request):
    config = testing.setUp()
    request.addfinalizer(testing.tearDown)
    return config


@fixture
def mount(tmpdir):
    backend = FSBackend(Path(str(tmpdir)))
    userdb = UserDB(dummy_auth)
    return Mount(
        "dummy",
        backend=backend,
        userdb=userdb,
        auth_realm="AUTH_REALM",
    )


def test_directory_basic(mount):
    root = Path(mount.backend.root)
    path = Path("foo/bar")
    dentry = DirectoryDentry(mount, path)
    directory = Directory(dentry)
    (root / path).mkdir(parents=True)
    assert not directory.is_root
    assert str(path) in repr(directory)
    assert directory.name == dentry.path.name
    assert directory.mount is mount
    assert directory.path == path


def test_directory_getitem_dir(mount):
    root = Path(mount.backend.root)
    path = Path("foo/bar")
    dentry = DirectoryDentry(mount, path)
    child_name = "frob"
    child_path = (root / path / child_name)
    child_path.mkdir(parents=True)
    directory = Directory(dentry)
    child = directory[child_name]
    assert isinstance(child, Directory)
    assert child.mount is mount
    assert child.path == path / child_name
    

def test_directory_getitem_file(mount):
    root = Path(mount.backend.root)
    path = Path("foo/bar")
    dentry = DirectoryDentry(mount, path)
    child_name = "frob"
    child_path = (root / path / child_name)
    (root / path).mkdir(parents=True)
    with child_path.open("w") as f:
        pass
    directory = Directory(dentry)
    child = directory[child_name]
    assert isinstance(child, File)
    assert child.mount is mount
    assert child.path == path / child_name


def test_directory_getitem_notfound(mount):
    root = Path(mount.backend.root)
    path = Path("foo/bar")
    dentry = DirectoryDentry(mount, path)
    child_name = "frob"
    (root / path).mkdir(parents=True)
    directory = Directory(dentry)
    with raises(KeyError):
        directory[child_name]


class DummyCollator:
    def getSortKey(self, s):
        return s


@fixture
def context(mount):
    root = Path(mount.backend.root)
    path = Path("foo/bar")
    (root / path).mkdir(parents=True)
    dentry = DirectoryDentry(mount, path)
    return Directory(dentry)
    

def test_view(mount, context):
    root = Path(mount.backend.root)
    path = context.path
    (root / path / "childdir").mkdir(parents=True)
    with (root / path / "childfile").open("w") as f:
        pass
    request = DummyRequest()
    request.collator = DummyCollator()
    resp = directory_view(context, request)
    assert not resp["show_hidden"]
    assert resp["parents"] == [
        (mount.name, "../../"),
        (path.parts[0], "../"),
    ]
    children = resp["children"]
    assert len(children) == 2
    child = children[0]
    assert child.name == "childdir"
    assert isinstance(child, Directory)

    child = children[1]
    assert child.name == "childfile"
    assert isinstance(child, File)


def test_view_redirect_trailing_slash(mount):
    request = DummyRequest(path="/foo/bar")
    with raises(HTTPSeeOther) as exc_info:
        directory_view(None, request)
    print(request.url)
    assert exc_info.value.location.endswith(request.path + "/")


class Upload:
    def __init__(self, filename, content):
        self.filename = filename
        self.file = TemporaryFile()
        self.file.write(content)
        self.file.seek(0)


def test_upload_file(mount, context):
    root = Path(mount.backend.root)
    path = context.path
    content = b"frob\n"
    fname = "baz"
    request = DummyRequest(
        params={
            "content": Upload(fname, content),
            "filename": "",
        }
    )
    resp = upload_file_view(context, request)
    assert isinstance(resp, HTTPSeeOther)
    respath = root / path / fname
    assert respath.is_file()
    with respath.open("rb") as f:
        assert f.read() == content


def test_upload_file_destname(mount, context):
    root = Path(mount.backend.root)
    path = context.path
    content = b"frob\n"
    fname = "baz"
    request = DummyRequest(
        params={
            "content": Upload("frob", content),
            "filename": fname,
        }
    )
    resp = upload_file_view(context, request)
    assert isinstance(resp, HTTPSeeOther)
    respath = root / path / fname
    assert respath.is_file()
    with respath.open("rb") as f:
        assert f.read() == content


def test_upload_file_conflict_directory(mount, context):
    root = Path(mount.backend.root)
    path = context.path
    fname = "baz"
    (root / path / fname).mkdir(parents=True)
    request = DummyRequest(
        params={
            "content": Upload("frob", b"frob\n"),
            "filename": fname,
        }
    )
    resp = upload_file_view(context, request)
    assert isinstance(resp, HTTPConflict)


def test_upload_file_replace_forbidden(testconfig, mount, context):
    sec_pol = DummySecurityPolicy(permissive=False)
    testconfig.set_authorization_policy(sec_pol)
    testconfig.set_authentication_policy(sec_pol)
    root = Path(mount.backend.root)
    path = context.path
    fname = "baz"
    respath = ( root / path / fname )
    with respath.open("w"):
        pass
    request = DummyRequest(
        params={
            "content": Upload("frob", b"frob\n"),
            "filename": fname,
        }
    )
    resp = upload_file_view(context, request)
    assert isinstance(resp, HTTPForbidden)


def test_includeme(testconfig):
    testconfig.include("pylf.directory")
