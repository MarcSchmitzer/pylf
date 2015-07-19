"""User database class."""

import hashlib
import random

from base64 import b64decode, b64encode


class UserDB(dict):
    def __init__(self, authenticator):
        self.authenticator = authenticator

    def authenticate(self, login, password):
        if login in self:
            account = self[login]
            if not self.check_password(account, password):
                return None
        else:
            account = self.authenticator(login, password)
            if account:
                self.store(login, password, account)

        return account

    def check_password(self, account, password):
        pw = account["password"]
        digest = hashlib.new(pw["type"])
        digest.update(b64decode(pw["salt"]))
        digest.update(password.encode("utf8"))
        if digest.digest() != b64decode(pw["hash"]):
            return None
        return account

    def store(self, login, password, account):
        if "password" not in account:
            salt_len = 8
            dig_type = "sha512"
            salt = random.getrandbits(salt_len * 8)
            salt = salt.to_bytes(salt_len, "little")
            digest = hashlib.new(dig_type)
            digest.update(salt)
            digest.update(password.encode("utf8"))
            account["password"] = {
                "type": dig_type,
                "salt": b64encode(salt),
                "hash": b64encode(digest.digest()),
            }
        self[login] = account

            
if __name__ == "__main__":
    import getpass, sys, configparser
    from plugins import Plugins
    cfg = configparser.ConfigParser()
    cfg.read(sys.argv[1])
    cfg = cfg["authentication"]
    authn_plugins = Plugins("authn")
    Authn = authn_plugins[cfg["type"]]
    authn = Authn.from_config(cfg)
    userdb = UserDB(authn)
    login, password = input("Login: "), getpass.getpass()
    print("Authenticate:", userdb.authenticate(login, password))
    print("DB:",  userdb)
    print("Re-authenticate:", userdb.authenticate(login, password))
    
