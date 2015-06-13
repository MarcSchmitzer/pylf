"""User database with accounts specified in the config file."""

import hashlib

from base64 import b64decode
from json import loads


__plugin__ = "InlineUserDB"


class InlineUserDB(dict):
    @classmethod
    def from_config(cls, cfg):
        return cls(loads(cfg["users"]))

    def authenticate(self, login, password):
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
