import tornado.web

from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(2)


class StorageHandler(tornado.web.RequestHandler):

    def prepare(self):
        self.set_header('Content-Type', 'application/octet-stream')

    @tornado.gen.coroutine
    def get(self, filename):
        try:
            with open(filename, 'rb') as f:
                while True:
                    data = yield executor.submit(f.read, 1024**2)
                    if len(data) == 0:
                        self.finish()
                        break
                    self.write(data)
        except FileNotFoundError as e:
            raise tornado.web.HTTPError(404)

    @tornado.gen.coroutine
    def put(self, filename):
        pass

