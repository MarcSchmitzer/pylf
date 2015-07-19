
from pylf.userdb import UserDB


class DummyAuthenticator:
    def __init__(self, accounts):
        self.accounts = accounts

    def __call__(self, login, password):
        if login not in self.accounts:
            return None

        account, real_pw = self.accounts[login]
        if password == real_pw:
            return account

        return None


ACCOUNTS = {
    "marc": ({"name": "Marc Schmitzer"}, "test1234"),
}


def test_authenticate_ok():
    login = "marc"
    authr = DummyAuthenticator(ACCOUNTS)
    db = UserDB(authr)
    account, real_pw = ACCOUNTS[login]
    assert db.authenticate(login, real_pw) == account


def test_authenticate_fail():
    authr = DummyAuthenticator({})
    db = UserDB(authr)
    assert db.authenticate("marc", "test4321") is None


def test_reauthenticate_ok():
    login = "marc"
    authr = DummyAuthenticator(ACCOUNTS)
    db = UserDB(authr)
    account, real_pw = ACCOUNTS[login]
    assert db.authenticate(login, real_pw) == account
    # Re-authentication should not hit the authenticator.
    authr.accounts = {}
    assert db.authenticate(login, real_pw) == account


def test_reauthenticate_fail():
    login = "marc"
    authr = DummyAuthenticator(ACCOUNTS)
    db = UserDB(authr)
    account, real_pw = ACCOUNTS[login]
    assert db.authenticate(login, real_pw) == account
    # Re-authentication should not hit the authenticator.
    authr.accounts = {}
    assert db.authenticate(login, "wrong_pw") is None

