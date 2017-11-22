from src.sync.event import Event
from src.sync.state import State
from src.sync.network import SyncNetwork
from src.index.tools import debug

from src.sync.file import FileInfo

from subprocess import Popen, PIPE

from hashlib import md5, sha256

from queue import Empty as QueueEmptyError

from time import sleep

import os


class Sync:
    """
    This class is responsible for controling the low-level filesystem driver.
    It also performs synchronization operations of the filesystem data.
    """
    def __init__(self, command_queue, event_queue, query_queue, fs_root, remote):
        """
        Create a new mountable filesystem instance.
        :param command_queue: Queue for sending commands to the filesystem.
        :param event_queue: Queue from which events in the filesystem will be transmited.
        :param query_queue: Queue for querying the filesystem state.
        :param fs_root: The root directory to mount the filesystem.
        :param remote: The remote URI used to sync the filesystem.
        """
        self._fs_root = os.path.abspath(fs_root)
        self._fs_low = "%s/._ssrs_%s" % (os.path.dirname(fs_root), os.path.basename(fs_root))
        self._cmd_queue = command_queue
        self._event_queue = event_queue
        self._q_queue = query_queue

        self._state = None
        self._driver = None
        self._encfs = None

        self._network = SyncNetwork(self._fs_low, fs_root, remote)

    def mount(self, password, from_remote=False):
        """
        Attempts to mount the filesystem in the determined root directory.
        :param password: The filesystem secret key
        :param from_remote: Synchronize the remote filesystem instead of creating a new one.
        :return:
        """
        event_addr = "ipc:///tmp/%s" % (md5(str(self._fs_root).encode()).hexdigest())

        new_filesystem = False

        config = self._fs_low + '/.encfs6.xml'
        if not os.path.exists(config):
            debug('Filesystem "%s" does not exist in' % (self._fs_root,))
            os.mkdir(self._fs_low)
            if from_remote is True:
                configuration = self._network.get_remote_configuration('.encfs6.xml')
                if configuration is None:
                    raise Exception('Could not retrieve remote filesystem configuration')
                with open(config, 'wb') as f:
                    f.write(configuration)
            else:
                new_filesystem = True

        self._encfs = encfs = Popen([
            '../dsfs/cmake-build-debug/dsfs', '-f', '-S', '--standard',
            self._fs_low,
            self._fs_root],
            stdin=PIPE)

        debug('Sending IPC address to driver')
        encfs.stdin.write(event_addr.encode())
        encfs.stdin.write(b'\n')
        encfs.stdin.flush()

        if new_filesystem is True:
            debug('Creating new filesystem in %s' % (self._fs_root,))
            encfs.stdin.write(password.encode())
            encfs.stdin.write(b'\n')
            encfs.stdin.flush()

        debug('Sending filesystem password')
        encfs.stdin.write(password.encode())
        encfs.stdin.write(b'\n')
        encfs.stdin.flush()

        self._driver = Event(event_addr)
        self._state = State(self._event_queue)

        debug('Waiting for driver')

        fskey = None
        retry = 3
        while retry > 0:
            sleep(1)
            fskey = self._driver.connect()
            if fskey is not None:
                fskey = sha256(fskey).hexdigest()
                break
            retry = retry - 1

        if fskey is None:
            raise Exception('Could not initialize filesystem driver')

        self._network.set_remote_key(fskey)

        debug('Filesystem private key is %s' % (fskey,))
        debug('Restoring filesystem state')
        self._state.load(self._fs_root + '/._ssrs_state')

        return fskey

    def load_remote_state(self, block):
        """
        Attempt to load the remote filesystem state from the specified block.
        :param block:
        :return:
        """
        if self._network.download_remote_block(block) is False:
            return None

        state = State(None)
        state.load(os.path.join(self._fs_root, block.path[1:]))

        return state

    def sync_filesystem(self):
        """
        Sync the filesystem data with the remote server.
        :return:
        """
        debug('Syncing filesystem of root %s' % (self._fs_root,))
        state_file = self._state.files['/._ssrs_state']

        remote_state = self.load_remote_state(state_file)
        if remote_state is not None:
            for (key, remote) in remote_state.files.items():
                if key not in self._state.files:
                    self._state.update_node(remote.path, remote.cipher)

        state_file.modified = False
        for (key, local) in self._state.files.items():
            if local.modified is True:
                self._network.upload_local_block(local)
                local.modified = False
            else:
                remote = None if remote_state is None else remote_state.files.get(key)
                if remote is not None:
                    if local.hash != remote.hash:
                        self._network.download_remote_block(local)
                        local.hash = remote.hash

        self._state.freeze(self._fs_root + '/._ssrs_state')
        self._network.upload_local_block(state_file)

        if self._network.get_remote_configuration('.encfs6.xml') is None:
            self._network.upload_local_block(FileInfo('configuration', '.encfs6.xml'))

    def main_loop(self):
        """
        This is the main loop responsible for processing events and updating filesystem state.
        This method will block until the filesystem is requested to finish or an unexpected error occurs.
        :return:
        """
        debug('Filesystem up and running')

        while True:
            ev, path, cipher = self._driver.recv()

            try:
                message = self._cmd_queue.get_nowait()

                if message[0] == 1:
                    self._event_queue.put((1, "", "",))
                    debug('Exit command received')
                    break
                elif message[0] == 2:
                    debug('Sync command received')
                    try:
                        self._network.sync_index()
                        self.sync_filesystem()
                    except Exception as e:
                        debug('Failed to synchronize filesystem %s: %s' % (self._fs_root, e,))
                elif message[0] == 3:
                    cipher = message[1]
                    fi = self._state.lookup.get(cipher)
                    if fi is not None:
                        self._q_queue.put(fi.path)
                    else:
                        debug('Failed decoding %s' % (cipher,))
                        self._q_queue.put('')
            except QueueEmptyError:
                pass

            if self._encfs.poll() is not None:
                raise Exception('File system driver has exited unexpectedly')

            if ev == self._driver.EVENT_OPEN:
                self._state.open(path, os.path.relpath(cipher, self._fs_low))
            elif ev == self._driver.EVENT_WRITE:
                self._state.write(path)
            elif ev == self._driver.EVENT_RELEASE:
                self._state.close(path)
            elif ev == self._driver.EVENT_UNLINK:
                self._state.unlink(path)

        debug('Freezing filesystem state')
        self._state.freeze(self._fs_root + '/._ssrs_state')
        debug('Terminating filesystem driver')
        self._encfs.terminate()
        self._encfs.wait()


def filesystem_main(command, event, query, fs_root, remote, password, download):
    """
    This is a bootstrap function used as main entry point for the filesystem.
    It is responsible for trying to mount the filesystem and running its main loop.
    :param command:
    :param event:
    :param query:
    :param fs_root:
    :param remote:
    :param password:
    :param download:
    :return:
    """
    filesystem = Sync(command, event, query, fs_root, remote)

    try:
        fskey = filesystem.mount(password, download)
    except Exception as e:
        event.put((False, str(e), None))
        return

    event.put((True, "It works!", fskey))

    try:
        filesystem.main_loop()
    except Exception as e:
        debug('Filesystem has finished unexpectedly: %s' % (e,))

    debug('bye')
