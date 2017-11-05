from src.sync.file import FileInfo
import pickle

class State:
    def __init__(self):
        self.files = {}

    def open(self, path, cipher):
        fi = self.files.get(path)
        if fi is None:
            self.files[path] = fi = FileInfo(path, cipher)
        print('File',fi.path,'of cipher',fi.cipher,'opened')
        fi.ref = fi.ref + 1

    def write(self, path):
        try:
            fi = self.files[path]
            # print('File',file.path,'modified')
            fi.modified = True
        except KeyError:
            print('Invalid file',path,'for write operation')

    def close(self, path):
        try:
            fi = self.files[path]
            fi.ref = fi.ref - 1
            if fi.ref == 0:
                # print('File',path,'of cipher',f.path_cipher,'closed')
                pass
        except KeyError:
            print('Invalid file for close operation')

    def unlink(self, path):
        print('File',path,'unlinked')
        self.files.pop(path, None)

    def load(self, path):
        try:
            with open(path, 'rb') as f:
                self.files = pickle.load(f)
        except FileNotFoundError:
            pass

    def freeze(self, path):
        with open(path, 'wb+') as f:
            pickle.dump(self.files, f)
