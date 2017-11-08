class FileInfo:
    def __init__(self, path, cipher, modified=False):
        self.path = path
        self.cipher = cipher
        self.modified = modified
        self.written = False
        self.ref = 0
