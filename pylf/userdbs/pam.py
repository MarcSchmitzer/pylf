"""User database based on system accounts."""

import pwd
import simplepam

from functools import lru_cache

__plugin__ = "PamUserDB"


class PamUserDB:
    @classmethod
    def from_config(cls, _cfg):
        return cls()

    @lru_cache()
    def authenticate(self, login, password):
        if simplepam.authenticate(login, password):
            account = pwd.getpwnam(login)
            return {
                "name": account.pw_gecos,
            }
        return None
    

if __name__ == "__main__":
    from getpass import getpass
    userdb = PamUserDB()
    login = input("Login: ")
    password = getpass()
    print(userdb.authenticate(login, password))
