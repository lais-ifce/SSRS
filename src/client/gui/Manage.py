from multiprocessing import Process, Queue

from client.index.PersistentFilter import index_loop
from client.sync.sync import filesystem_main


class Manage:
    """
    Class to manage the mounted file systems
    """
    def __init__(self):
        self.mounted = {}

    def get_local_mounted(self):
        """
        Return a list with the local path of all mounted points
        :return: list of strings
        """
        return [self.mounted[x]['path'] for x in self.mounted.keys()]

    def get_remote_mounted(self):
        """
        Return a list with the remote path of all mounted points
        :return: list of strings
        """
        return [self.mounted[x]['remote'] for x in self.mounted.keys()]

    def mount(self, path, remote, password, download):
        """
        Mount a file system
        :param path: local path
        :param remote: remote path
        :param password: password of a filesystem
        :param download: download metadata from remote path
        :return: 2-tuple with a boolean for the successfully mount and a message string
        """
        command = Queue()
        event = Queue()
        query = Queue()

        fs = Process(target=filesystem_main, args=(command, event, query, path, remote, password, download))
        fs.start()

        result, status, key = event.get()

        if result is True:
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

        return result, status

    def unmount(self, path):
        """
        Unmount a file system
        :param path: local path to file system
        :return: boolean for the successful of operation
        """
        mount = self.mounted.pop(path, None)
        if mount is None:
            return False
        mount['cmd'].put((1,))
        mount['fs'].join()
        mount['index'].join()
        return True

    def start_sync(self, local, remote):
        """
        Trig the sync routines
        :param local: local path to the file system
        :param remote: remote path to the file system
        :return: None
        """
        mount = self.mounted.get(local)
        if mount is None:
            return
        mount['cmd'].put((2,))

    def destroy(self):
        """
        When the class is destroyed all file systems are unmounted
        :return: None
        """
        [self.unmount(x) for x in list(self.mounted.keys())]
