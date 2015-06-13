
from importlib import import_module


class Plugins:
    """Plugin-module loader."""

    def __init__(self, package=None):
        """Constructor.

        Args:
          package (str): Dotted name of the base package containing
            the plugin modules. If omitted, all plugin specs must be
            fully-qualified.
        """
        self.package = package
        if self.package:
            import_module(self.package)

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.package)

    def __getitem__(self, name):
        """Get the plugin `name`."""
        if self.package:
            name = "." + name
        return import_module(name, package=self.package)
