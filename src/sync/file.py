from hashlib import md5


class FileInfo:
    """
    Represents the state of a file.
    """
    def __init__(self, path, cipher):
        """
        Construct a new file state.
        :param path:
        :param cipher:
        """
        self.path = path
        self.cipher = cipher
        self.modified = False
        self.written = False
        self.ref = 0
        self.hash = None
        self.lookup = md5(self.cipher.encode()).hexdigest()
