"""Provides the `Mount` class."""
import os

from configparser import SafeConfigParser

from .plugins import Plugins


class Mount:
    """Represents a single configured mount."""

    backends = Plugins("pylf.backends")
    userdbs = Plugins("pylf.userdbs")

    @classmethod
    def from_file(cls, path):
        """Create an instance based on the configuration file at `path`."""
        name = os.path.basename(path).split(".", 1)[0]
        parser = SafeConfigParser()
        parser.read([path])
        cfg = {
            section: dict(parser.items(section))
            for section in parser.sections()
        }
        return cls(name, cfg)

    def __init__(self, name, cfg):
        self.name = name

        backend_cfg = cfg["backend"]
        backend_cls = self.backends[backend_cfg["type"]]
        self.backend = backend_cls.from_config(backend_cfg)

        self.auth_realm = cfg["auth"]["realm"]

        userdb_cfg = cfg["userdb"]
        userdb_cls = self.userdbs[userdb_cfg["type"]]
        self.userdb = userdb_cls.from_config(userdb_cfg)

    def __repr__(self):
        return "{}({!r}, backend={!r})".format(
            type(self).__name__,
            self.name,
            self.backend,
        )
