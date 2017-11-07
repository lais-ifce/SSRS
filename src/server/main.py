import tornado.web

from src.config import *

from src.server.search import SearchHandler
from src.server.storage import StorageHandler


if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/([A-z]+)/search", SearchHandler),
        (r"/([A-z|.]+)/file", StorageHandler),
    ], debug=True)

    app.listen(SERVER_PORT, SERVER_IP)

    tornado.ioloop.IOLoop.current().start()

