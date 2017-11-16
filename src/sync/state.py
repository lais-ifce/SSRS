from src.sync.file import FileInfo
import pickle


class State:
    def __init__(self, change):
        self.files = {}
        self.lookup = {}
        self.change_queue = change

    def update_node(self, path, cipher):
        file = self.files.get(path)
        if file is None:
            file = FileInfo(path, cipher)
            self.files[file.path] = file
            self.lookup[file.cipher] = file
        return file

    def open(self, path, cipher):
        f = self.update_node(path, cipher)
        # print('File', fi.path, 'of cipher', fi.cipher, 'opened')
        f.ref = f.ref + 1

    def write(self, path):
        try:
            fi = self.files[path]
            # print('File',file.path,'written')
            fi.written = True
            fi.modified = True
        except KeyError:
            print('Invalid file', path, 'for write operation')

    def close(self, path):
        try:
            fi = self.files[path]
            fi.ref = fi.ref - 1
            if fi.ref == 0 and fi.written is True:
                # print('File',path,'of cipher',f.path_cipher,'closed')
                self.change_queue.put((2, fi.path, fi.cipher,))
                fi.written = False
        except KeyError:
            print('Invalid file for close operation')

    def unlink(self, path):
        # print('File', path, 'unlinked')
        self.files.pop(path, None)

    def load(self, path):
        try:
            with open(path, 'rb') as f:
                self.files = pickle.load(f)
                for file in self.files.values():
                    self.lookup[file.cipher] = file
        except FileNotFoundError:
            self.freeze(path)

    def freeze(self, path):
        with open(path, 'wb+') as f:
            pickle.dump(self.files, f)
