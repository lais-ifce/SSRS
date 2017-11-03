from event import Event
from state import State

from subprocess import Popen, PIPE
from hashlib import md5

from multiprocessing import Queue
from threading import Thread

import sys
import os

from time import sleep

def outra_funcao():
    pass

def filesystem_main(command, fs_root, password):
    fs_root = os.path.abspath(fs_root)
    fs_low  = "%s/._ssrs_%s" % (os.path.dirname(fs_root), os.path.basename(fs_root))

    event_addr = "ipc:///tmp/%s" % (md5(str(fs_root).encode()).hexdigest())

    new_filesystem = False

    if not os.path.exists(fs_low + '/.encfs6.xml'):
        print('Filesystem does not exist')
        os.mkdir(fs_low)
        new_filesystem = True

    encfs = Popen(['../fs/cmake-build-debug/dsfs', '-f', '-S', '--standard', fs_low, fs_root], stdin=PIPE)

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
    fs = State()

    print('Restoring filesystem state')
    sleep(1)
    fs.load(fs_root + '/._ssrs_state')

    print('Filesystem up and running')

    # print(fs.files)

    while True:
        ev, path, cipher = event.recv()

        try:
            cmd = command.get_nowait()
            if cmd == 1:
                print('Exit command received')
                break
        except:
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


if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit('Missing arguments')
    cmd = Queue()
    fs = Thread(target=filesystem_main, args=(cmd, sys.argv[1], sys.argv[2]))
    fs.start()
    input()
    cmd.put(1)
    fs.join()

