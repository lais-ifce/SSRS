from src.sync.file import FileInfo
import pickle


class State:
    def __init__(self, change):
        self.files = {}
        self.change_queue = change

    def open(self, path, cipher):
        fi = self.files.get(path)
        if fi is None:
            self.files[path] = fi = FileInfo(path, cipher)
        # print('File', fi.path, 'of cipher', fi.cipher, 'opened')
        fi.ref = fi.ref + 1

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
                self.change_queue.put((2, fi.path, fi.cipher, ))
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
        except FileNotFoundError:
            self.freeze(path)

    def freeze(self, path):
        with open(path, 'wb+') as f:
            pickle.dump(self.files, f)
