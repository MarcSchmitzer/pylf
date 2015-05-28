

class Dentry:
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.path)


class FileDentry(Dentry):
    pass


class DirectoryDentry(Dentry):
    mimetype = ("inode/directory", None)
    size = None
