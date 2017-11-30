import tornado.web

from config import *

from server.search import SearchHandler
from server.storage import GETHandler, PUTHandler


if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/([A-z]+)/search", SearchHandler),
        (r"/([A-z]+)/get/([A-z0-9]+[=]*)", GETHandler),
        (r"/([A-z]+)/put/([A-z0-9]+[=]*)", PUTHandler),
    ], debug=True)

    app.listen(SERVER_PORT, SERVER_IP)

    tornado.ioloop.IOLoop.current().start()

