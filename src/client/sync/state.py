import pickle

from client.sync.file import FileInfo


class State:
    """
    This class manages the filesystem state.
    It processes events coming from the driver and updates the state accordingly.
    This state will then be used by the sync service when synchronizing with remotes.
    """
    def __init__(self, change_queue):
        """
        Construct an empty filesystem state.
        The change queue is used to inform about file changes.
        :param change_queue:
        """
        self.files = {}
        self.lookup = {}
        self.change_queue = change_queue

    def update_node(self, path, cipher):
        """
        Update a node in the state.
        If the node does not exist, it will be created.
        :param path:
        :param cipher:
        :return:
        """
        file = self.files.get(path)
        if file is None:
            file = FileInfo(path, cipher)
            self.files[file.path] = file
            self.lookup[file.lookup] = file
        return file

    def open(self, path, cipher):
        """
        Process the opening of a file.
        :param path:
        :param cipher:
        :return:
        """
        f = self.update_node(path, cipher)
        # print('File', fi.path, 'of cipher', fi.cipher, 'opened')
        f.ref = f.ref + 1

    def write(self, path):
        """
        Process the write event for a file.
        :param path:
        :return:
        """
        try:
            fi = self.files[path]
            # print('File',file.path,'written')
            fi.written = True
            fi.modified = True
        except KeyError:
            print('Invalid file', path, 'for write operation')

    def close(self, path):
        """
        Process the release of a file descriptor.
        :param path:
        :return:
        """
        try:
            fi = self.files[path]
            fi.ref = fi.ref - 1
            if fi.ref == 0 and fi.written is True:
                # print('File',path,'of cipher',f.path_cipher,'closed')
                self.change_queue.put((2, fi.path, fi.lookup,))
                fi.written = False
        except KeyError:
            print('Invalid file for close operation')

    def unlink(self, path):
        """
        Process the unlink/deletion of a file.
        :param path:
        :return:
        """
        try:
            f = self.files.pop(path)
            self.lookup.pop(f.cipher)
        except KeyError:
            print('Invalid file for unlink operation')

    def load(self, path):
        """
        Restore the filesystem state from the :path file.
        :param path:
        :return:
        """
        try:
            with open(path, 'rb') as f:
                self.files = pickle.load(f)
                for file in self.files.values():
                    self.lookup[file.lookup] = file
        except FileNotFoundError:
            # state does not exist yet, create one
            self.freeze(path)

    def freeze(self, path):
        """
        Save the current state to a file specified by :path.
        :param path:
        :return:
        """
        with open(path, 'wb+') as f:
            pickle.dump(self.files, f)
