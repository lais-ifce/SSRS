import tornado.web
import json
from src.index.QueryFilter import QueryFilter
from src.config import *
import os


class SearchHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.json_args = None

    def prepare(self):
        if self.request.headers["Content-Type"].startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            pass

    def post(self, repository):
        response = {
            "ok": False,
            "data": []
        }
        if self.json_args is not None:
            response["ok"] = True
            response["data"] = QueryFilter(self.json_args['data'], repository).run_query()
        self.write(response)

    def put(self, repository):
        response = {
            "ok": False
        }
        if "index" in self.request.files:
            file = self.request.files['index'][0]
            if not os.path.exists(os.path.join(INDEX_ROOT, repository)):
                os.mkdir(os.path.join(INDEX_ROOT, repository))
            with open(os.path.join(INDEX_ROOT, repository, file['filename']), "wb") as f:
                f.write(file['body'])
            response["ok"] = True
        self.write(response)

    def delete(self, repository):
        response = {
            "ok": False
        }
        if self.json_args is not None:
            if "data" in self.json_args.keys():
                for file in self.json_args['data']:
                    if os.path.exists(os.path.join(INDEX_ROOT, repository, file)):
                        try:
                            os.remove(os.path.join(INDEX_ROOT, repository, file))
                            response["ok"] = True
                        except Exception as e:
                            response["exception"] = e
        self.write(response)
