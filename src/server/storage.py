import tornado.web
import os

from concurrent.futures import ThreadPoolExecutor

from tempfile import TemporaryFile
from hashlib import md5

executor = ThreadPoolExecutor(2)


class GETHandler(tornado.web.RequestHandler):

    def prepare(self):
        self.set_header('Content-Type', 'application/octet-stream')

    @tornado.gen.coroutine
    def get(self, repo, filename):
        try:
            with open(os.path.join(repo, filename), 'rb') as f:
                while True:
                    data = yield executor.submit(f.read, 1024**2)
                    if len(data) == 0:
                        self.finish()
                        break
                    self.write(data)
        except FileNotFoundError:
            raise tornado.web.HTTPError(404)

    def data_received(self, chunk):
        pass


@tornado.web.stream_request_body
class PUTHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.temp_file = TemporaryFile()

    def data_received(self, chunk):
        self.temp_file.write(chunk)

    @tornado.gen.coroutine
    def put(self, repo, filename):
        if not os.path.exists(repo):
            os.mkdir(repo)
        with open(os.path.join(repo, filename), 'wb') as f:
            self.temp_file.seek(0)
            content_hash = md5()
            while True:
                data = yield executor.submit(self.temp_file.read, 1024**2)
                if len(data) == 0:
                    break
                content_hash.update(data)
                yield executor.submit(f.write, data)
            self.write(content_hash.hexdigest())
