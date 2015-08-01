"""User database class."""

from .authn.util import check_password, make_hashdict


class UserDB(dict):
    def __init__(self, authenticator):
        dict.__init__(self)
        self.authenticator = authenticator

    def authenticate(self, login, password):
        if login in self:
            account = self[login]
            if not check_password(account["password"], password):
                return None
        else:
            account = self.authenticator(login, password)
            if account:
                self.store(login, password, account)

        return account

    def store(self, login, password, account):
        if "password" not in account:
            account["password"] = make_hashdict(password)
        self[login] = account
