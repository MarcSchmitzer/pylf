"""User authenticator based on system accounts."""

import pwd
import simplepam

__plugin__ = "PamAuthenticator"


class PamAuthenticator:
    @classmethod
    def from_config(cls, _cfg):
        return cls()

    def __call__(self, login, password):
        if simplepam.authenticate(login, password):
            account = pwd.getpwnam(login)
            return {
                "name": account.pw_gecos,
            }
        return None
