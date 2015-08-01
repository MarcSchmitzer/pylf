"""User authenticator with accounts specified in the config file."""

from json import loads

from .util import check_password


__plugin__ = "InlineAuthenticator"


class InlineAuthenticator(dict):
    @classmethod
    def from_config(cls, cfg):
        return cls(loads(cfg["users"]))

    def __call__(self, login, password):
        try:
            account = self[login]
        except KeyError:
            return None

        if check_password(account["password"], password):
            return account
        return None
