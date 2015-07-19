"""User authenticator with accounts specified in the config file."""

import hashlib

from base64 import b64decode
from json import loads


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

        pw = account["password"]
        digest = hashlib.new(pw["type"])
        digest.update(b64decode(pw["salt"]))
        digest.update(password.encode("utf8"))
        if digest.digest() != b64decode(pw["hash"]):
            return None
        return account


if __name__ == "__main__":
    import getpass, sys, configparser
    cfg = configparser.ConfigParser()
    cfg.read(sys.argv[1])
    cfg = cfg["authentication"]
    authn = InlineAuthenticator.from_config(cfg)
    login, password = input("Login: "), getpass.getpass()
    print(authn(login, password))