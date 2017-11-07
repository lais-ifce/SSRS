from src.sync.event import Event
from src.sync.state import State
from src.config import BASE_URL

from subprocess import Popen, PIPE
from hashlib import md5, sha256

from multiprocessing import Queue
from threading import Thread

from queue import Empty as QueueEmptyError

import sys
import os
import re
import requests

from time import sleep


def filesystem_main(command, change, fs_root, password):
    fs_root = os.path.abspath(fs_root)
    fs_low = "%s/._ssrs_%s" % (os.path.dirname(fs_root), os.path.basename(fs_root))

    event_addr = "ipc:///tmp/%s" % (md5(str(fs_root).encode()).hexdigest())

    new_filesystem = False

    if not os.path.exists(fs_low + '/.encfs6.xml'):
        print('Filesystem does not exist')
        os.mkdir(fs_low)
        new_filesystem = True

    encfs = Popen(['../dsfs/cmake-build-debug/dsfs', '-f', '-S', '--standard', fs_low, fs_root], stdin=PIPE)

    print('Sending IPC address')
    encfs.stdin.write(event_addr.encode())
    encfs.stdin.write(b'\n')
    encfs.stdin.flush()

    if new_filesystem:
        print('Creating new filesystem...')
        encfs.stdin.write(password.encode())
        encfs.stdin.write(b'\n')
        encfs.stdin.flush()

    print('Sending filesystem password')
    encfs.stdin.write(password.encode())
    encfs.stdin.write(b'\n')
    encfs.stdin.flush()

    event = Event(event_addr)
    fs = State(change)

    print('Waiting for driver')
    sleep(3)
    fskey = sha256(event._socket.recv()).hexdigest()

    change.put(fskey)

    print('Filesystem private key is', fskey)

    print('Restoring filesystem state')
    fs.load(fs_root + '/._ssrs_state')

    print('Filesystem up and running')

    # print(fs.files)

    while True:
        ev, path, cipher = event.recv()

        try:
            message = command.get_nowait()
            if message == 1:
                change.put((1, "", "",))
                print('Exit command received')
                break
            elif message == 2:
                print('Syncing filesystem')
        except QueueEmptyError:
            pass

        if encfs.poll() is not None:
            exit('FATAL: File system has exited')

        if ev == event.EVENT_OPEN:
            fs.open(path, cipher)
        elif ev == event.EVENT_WRITE:
            fs.write(path)
        elif ev == event.EVENT_RELEASE:
            fs.close(path)
        elif ev == event.EVENT_UNLINK:
            fs.unlink(path)

    print('Freezing filesystem state')
    fs.freeze(fs_root + '/._ssrs_state')
    print('Terminating filesystem driver')
    encfs.terminate()
    encfs.wait()
    print('Bye')


def sync_index(fs_root, remote):
    source = os.path.join(fs_root, ".index")
    if os.path.exists(source):
        files = os.listdir(source)
        files = [x for x in files if re.fullmatch(r'([0-9a-fA-F]){32}', x) is not None]
        remote = remote + "/" if remote[-1] != "/" else remote
        for f in files:
            r = requests.put(remote + "search", files={
                "index": open(os.path.join(source, f), "rb")
            })
            assert r.status_code == 200
    exit(0)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit('Missing arguments')
    cmd = Queue()
    fs = Thread(target=filesystem_main, args=(cmd, sys.argv[1], sys.argv[2]))
    fs.start()
    input()
    cmd.put(1)
    fs.join()

