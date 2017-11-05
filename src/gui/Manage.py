from multiprocessing import Queue
from src.sync.sync import filesystem_main
from threading import Thread


class Manage:
    def __init__(self):
        self.mounted = []

    def get_local_mounted(self):
        return [x['path_local'] for x in self.mounted]

    def get_remote_mounted(self):
        return [x['path_remoto'] for x in self.mounted]

    def mount(self, local, remote, password):
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

    def unmount(self, local):
        for i in range(0, len(self.mounted)):
            if self.mounted[i]['path_local'] == local:
                self.mounted[i]['queue'].put(1)
                self.mounted[i]['thread'].join()
                del self.mounted[i]
                return True
        return False

    def destroy(self):
        for i in self.mounted:
            self.unmount(i['path_local'])
