import tornado.web
import json
from src.index.QueryFilter import QueryFilter


class SearchHandler(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.headers["Content-Type"].startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None

    def post(self, repository):
        if self.json_args is not None:
            self.write(json.dumps(QueryFilter(self.json_args['data'], repository).run_query()))
        else:
            pass
