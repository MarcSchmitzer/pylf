"""User authenticator based on an IMAP server."""

import imaplib
import logging

from pyramid.settings import asbool


__plugin__ = "IMAPAuthenticator"


class IMAPAuthenticator:
    @classmethod
    def from_config(cls, cfg):
        return cls(
            cfg["host"],
            int(cfg.get("port", 0)),
            asbool(cfg.get("ssl")),
        )

    def __init__(self, host, port, ssl):
        self.host = host
        if ssl:
            self.imap_cls = imaplib.IMAP4_SSL
            self.port = port or imaplib.IMAP4_SSL_PORT
        else:
            self.imap_cls = imaplib.IMAP4
            self.port = port or imaplib.IMAP4_PORT
        self.log = logging.getLogger("{}({!r})".format(
            type(self).__name__,
            self.host,
        ))

    def __call__(self, login, password):
        imap = self.imap_cls(self.host, self.port)
        try:
            imap.login(login, password)
        except imap.error as err:
            self.log.debug("Login failed: {}".format(err))
            return None
        return { "name": login }

