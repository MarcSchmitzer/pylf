
from pylf.authn.inline import InlineAuthenticator


from pytest import fixture

from pylf.authn.pam import PamAuthenticator


@fixture
def fake_account(monkeypatch):
    import simplepam, pwd, collections
    account = {
        "login": "marc",
        "name": "Marc Schmitzer",
        "password": "test1234",
    }
    AccountInfo = collections.namedtuple("AccountInfo", "pw_gecos")
    def authenticate(login, password):
        return login == account["login"] and password == account["password"]
    def getpwnam(login):
        if login == account["login"]:
            return AccountInfo(account["name"])
        raise KeyError(login)
    monkeypatch.setattr(simplepam, "authenticate", authenticate)
    monkeypatch.setattr(pwd, "getpwnam", getpwnam)
    return account


def test_from_config():
    PamAuthenticator.from_config({})


def test_authenticate_ok(fake_account):
    authr = PamAuthenticator()
    assert authr(fake_account["login"], fake_account["password"])


def test_authenticate_fail_password(fake_account):
    authr = PamAuthenticator()
    assert authr(fake_account["login"], "test4321") is None


def test_authenticate_fail_account(fake_account):
    authr = PamAuthenticator()
    assert authr("noone", "test4321") is None
