"""User database class."""

import hashlib
import random

from base64 import b64decode, b64encode

from .authn.util import check_password, make_hashdict


class UserDB(dict):
    def __init__(self, authenticator):
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
