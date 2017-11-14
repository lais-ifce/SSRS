from src.sync.event import Event
from src.sync.state import State

from subprocess import Popen, PIPE
from hashlib import md5, sha256
from base64 import b64encode

from multiprocessing import Queue
from threading import Thread

from queue import Empty as QueueEmptyError

import sys
import os
import re
import requests

from time import sleep


def filesystem_main(command, change, query, fs_root, remote, password):
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
            if message[0] == 1:
                change.put((1, "", "",))
                print('Exit command received')
                break
            elif message[0] == 2:
                print('Sync command received')
                sync_index(fs_root, remote)
                sync_filesystem(fs, fs_low, fs_root, remote)
            elif message[0] == 3:
                cipher = message[1]
                fi = fs.lookup.get(cipher)
                if fi is not None:
                    query.put(fi.path)
                else:
                    print('Failed decoding', cipher)
                    query.put('None')
        except QueueEmptyError:
            pass

        if encfs.poll() is not None:
            exit('FATAL: File system has exited')

        if ev == event.EVENT_OPEN:
            fs.open(path, os.path.relpath(cipher, fs_low))
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


def upload_local_block(file, fs_low, remote):
    uri = b64encode(file.cipher.encode()).decode()

    print('Uploading file', file.path)
    try:
        with open(os.path.join(fs_low, file.cipher), 'rb') as f:
            if requests.put(remote + '/put/' + uri, data=f).status_code is not 200:
                return False
    except FileNotFoundError:
        return False

    return True


def download_remote_block(file, fs_low, remote):
    uri = b64encode(file.cipher.encode()).decode()

    r = requests.get(remote + '/get/' + uri, stream=True)
    if r.status_code is not 200:
        return False

    try:
        with open(os.path.join(fs_low, file.cipher), 'wb') as f:
            for chunk in r.iter_content(1024**2):
                f.write(chunk)
    except FileNotFoundError:
        return False

    return True


def load_remote_state(file, fs_low, fs_root, remote):
    if download_remote_block(file, fs_low, remote) is False:
        return None

    state = State(None)
    state.load(os.path.join(fs_root, file.path[1:]))

    return state


def sync_filesystem(state, fs_low, fs_root, remote):
    print('Syncing filesystem of root', fs_root, 'for remote', remote)
    try:
        state_file = state.files['/._ssrs_state']

        remote_state = load_remote_state(state_file, fs_low, fs_root, remote)
        if remote_state is not None:
            for (key, file) in remote_state.files.items():
                if key not in state.files:
                    state.files[key] = file

        state_file.modified = False
        for (key, file) in state.files.items():
            if file.modified is True:
                upload_local_block(file, fs_low, remote)
                file.modified = False
            else:
                download_remote_block(file, fs_low, remote)

        state.freeze(fs_root + '/._ssrs_state')
        upload_local_block(state_file, fs_low, remote)
    except Exception as e:
        print('Failed filesystem sync:', e)


def sync_index(fs_root, remote):
    source = os.path.join(fs_root, ".index")
    if os.path.exists(source):
        files = os.listdir(source)
        # files = [x for x in files if re.fullmatch(r'([0-9a-fA-F]){32}', x) is not None]
        remote = remote + "/" if remote[-1] != "/" else remote
        for f in files:
            with open(os.path.join(source, f), "rb") as file:
                r = requests.put(remote + "search", files={
                    "index": file
                })
                assert r.status_code == 200
            try:
                os.remove(os.path.join(source, f))
            except Exception as e:
                pass
    # exit(0)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit('Missing arguments')
    cmd = Queue()
    fs = Thread(target=filesystem_main, args=(cmd, sys.argv[1], sys.argv[2]))
    fs.start()
    input()
    cmd.put(1)
    fs.join()

