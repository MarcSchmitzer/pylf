
from pathlib import Path

from pytest import fixture, raises

from pylf.backends.fs import FSBackend
from pylf.dentry import DirectoryDentry
from pylf.file import File
from pylf.mount import Mount
from pylf.directory import Directory
from pylf.userdb import UserDB


def dummy_auth(login, password):
    return { "name": "Dummy User" }


@fixture
def mount(tmpdir):
    backend = FSBackend(Path(str(tmpdir)))
    userdb = UserDB(dummy_auth)
    return Mount(
        "dummy",
        backend=backend,
        userdb=userdb,
    )
    

def test_directory_basic(mount):
    root = Path(mount.backend.root)
    path = Path("foo/bar")
    dentry = DirectoryDentry(mount, path)
    directory = Directory(dentry)
    (root / path).mkdir(parents=True)
    assert not directory.is_root
    assert str(path) in repr(directory)
    assert directory.dentry is dentry
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
    assert child.dentry.mount is mount
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
    assert child.dentry.mount is mount
    assert child.dentry.path == path / child_name


def test_directory_getitem_notfound(mount):
    root = Path(mount.backend.root)
    path = Path("foo/bar")
    dentry = DirectoryDentry(mount, path)
    child_name = "frob"
    (root / path).mkdir(parents=True)
    directory = Directory(dentry)
    with raises(KeyError):
        directory[child_name]
