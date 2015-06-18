"""Filesystem-backend.

Note that this has some limitations because all files are necessarily
owned by the user running the application.
"""

from os.path import expanduser
from pathlib import Path

from pyramid.response import FileResponse


__plugin__ = "FSBackend"


class FSBackend:
    @classmethod
    def from_config(cls, cfg):
        return cls(Path(expanduser(cfg["path"])))

    def __init__(self, root):
        self.root = root

    def listdir(self, path):
        return (self.root / path).iterdir()

    def stat(self, path):
        return (self.root / path).stat()

    def file_response(self, path, request=None):
        return FileResponse(str(self.root / path), request=request)
