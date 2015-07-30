"""Provides the `Mount` class."""
import os

from configparser import SafeConfigParser

from .plugins import Plugins
from .userdb import UserDB


class Mount:
    """Represents a single configured mount."""

    backends = Plugins("pylf.backends")
    authenticators = Plugins("pylf.authn")

    @classmethod
    def from_file(cls, path):
        """Create an instance based on the configuration file at `path`."""
        name = os.path.basename(path).split(".", 1)[0]
        cfg = SafeConfigParser()
        cfg.read([path])
        return cls.from_config(name, cfg)

    @classmethod
    def from_config(cls, name, cfg):
        backend_cfg = cfg["backend"]
        backend_cls = cls.backends[backend_cfg["type"]]
        backend = backend_cls.from_config(backend_cfg)

        authn_cfg = cfg["authentication"]
        authr_cls = cls.authenticators[authn_cfg["type"]]
        userdb = UserDB(authr_cls.from_config(authn_cfg))

        return cls(
            name,
            backend=backend,
            userdb=userdb,
            auth_realm=cfg["auth"]["realm"],
        )

    def __init__(self, name, backend, userdb, auth_realm):
        self.name = name
        self.backend = backend
        self.userdb = userdb
        self.auth_realm = auth_realm

    def __repr__(self):
        return "{}({!r}, backend={!r})".format(
            type(self).__name__,
            self.name,
            self.backend,
        )
