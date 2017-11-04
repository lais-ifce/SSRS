from multiprocessing import Queue
from src.sync.sync import filesystem_main
from threading import Thread


class Manage:
    def __init__(self):
        self.mounted = []

    def add_mount_point(self, local, remote, password):
        cmd = Queue()
        fs = Thread(target=filesystem_main, args=(cmd, local, password))
        self.mounted.append({
            "path_local": local,
            "path_remoto": remote,
            "queue": cmd,
            "thread": fs
        })
        fs.start()
        return fs.is_alive()

    def rem_mount_point(self, local):
        for i in self.mounted:
            if i['path_local'] == local:
                i['queue'].put(1)
                i['thread'].join()
                return True
        return False

    def destroy(self):
        for i in self.mounted:
            self.rem_mount_point(i['path_local'])
