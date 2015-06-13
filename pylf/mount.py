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
        cfg = {}
        for section in parser.sections():
            items = parser.items(section)
            if section == "general":
                cfg.update(items)
            else:
                cfg[section] = dict(items)
        return cls(name, cfg)

    def __init__(self, name, cfg):
        self.backend = self.backends[cfg["backend"]]
        self.config = cfg
        self.name = name
        self.root = self.backend.get_dentry(cfg["path"])
        userdb_cfg = cfg["userdb"]
        userdb_cls = self.userdbs[userdb_cfg["type"]]
        self.userdb = userdb_cls.from_config(userdb_cfg)
