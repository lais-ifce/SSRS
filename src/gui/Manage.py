from src.sync.sync import filesystem_main, sync_index
from src.index.PersistentFilter import index_loop
from multiprocessing import Process, Queue


class Manage:
    def __init__(self):
        self.mounted = {}

    def get_local_mounted(self):
        return [self.mounted[x]['path'] for x in self.mounted.keys()]

    def get_remote_mounted(self):
        return [self.mounted[x]['remote'] for x in self.mounted.keys()]

    def mount(self, path, remote, password):
        command = Queue()
        event = Queue()
        query = Queue()

        fs = Process(target=filesystem_main, args=(command, event, query, path, remote, password))
        fs.start()

        key = event.get()

        index = Process(target=index_loop, args=(event, path, key))

        if path not in self.mounted:
            self.mounted[path] = {
                "path": path,
                "remote": remote,
                "cmd": command,
                "fs": fs,
                "index": index,
                "key": key,
                "q": query
            }
            index.start()
            return fs.is_alive() and index.is_alive()

    def unmount(self, path):
        mount = self.mounted.pop(path, None)
        if mount is None:
            return False
        mount['cmd'].put((1,))
        mount['fs'].join()
        mount['index'].join()
        return True

    def start_sync(self, local, remote):
        mount = self.mounted.get(local)
        if mount is None:
            return
        mount['cmd'].put((2,))

    def destroy(self):
        [self.unmount(x) for x in list(self.mounted.keys())]
