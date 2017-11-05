from src.sync.sync import filesystem_main
from multiprocessing import Process, Queue


class Manage:
    def __init__(self):
        self.mounted = {}

    def get_local_mounted(self):
        return [self.mounted[x]['path'] for x in self.mounted.keys()]

    def get_remote_mounted(self):
        return [self.mounted[x]['remote'] for x in self.mounted.keys()]

    def mount(self, path, remote, password):
        cmd = Queue()
        fs = Process(target=filesystem_main, args=(cmd, path, password))
        if path not in self.mounted:
            self.mounted[path] = {
                "path": path,
                "remote": remote,
                "queue": cmd,
                "thread": fs
            }
            fs.start()
            return fs.is_alive()

    def unmount(self, path):
        mount = self.mounted.pop(path, None)
        if mount is None:
            return False
        mount['queue'].put(1)
        mount['thread'].join()
        return True

    def destroy(self):
        for (path, mount) in self.mounted.keys():
            self.unmount(path)
