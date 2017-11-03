from struct import unpack
import zmq

class Event:
    EVENT_NONE = 0
    EVENT_OPEN = 1
    EVENT_WRITE = 2
    EVENT_READ = 3
    EVENT_RELEASE = 4
    EVENT_UNLINK = 5
    EVENT_RMDIR = 6
    EVENT_RENAME = 7

    def __init__(self, ipc_addr):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PAIR)
        self._socket.setsockopt(zmq.RCVTIMEO, 100)
        self._socket.connect(ipc_addr)

    def recv(self):
        try:
            ev = unpack('i', self._socket.recv())[0]
            path = self._socket.recv_string()
            cipher = self._socket.recv_string()
        except zmq.ZMQError:
            ev = self.EVENT_NONE
            path = None
            cipher = None

        return (ev, path, cipher)

