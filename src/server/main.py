import tornado.ioloop
import tornado.web
from src.config import *
from src.server.search import SearchHandler

if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/search/([0-9a-fA-F]{40})", SearchHandler)
    ])
    app.listen(SERVER_PORT, SERVER_IP)
    tornado.ioloop.IOLoop.current().start()
