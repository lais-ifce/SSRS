import tornado.web
import json
from src.index.QueryFilter import QueryFilter
from src.config import *
import os


class SearchHandler(tornado.web.RequestHandler):
    """
    Class that extends Tornado Web Request Handler and handle all requests to `search` endpoint
    """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.json_args = None

    def prepare(self):
        """
        Parse request content from a JSON if is the header set
        :return: None
        """
        if self.request.headers["Content-Type"].startswith("application/json"):
            if type(self.request.body) is bytes:
                self.json_args = json.loads(self.request.body.decode('utf-8'))
            else:
                self.json_args = json.loads(self.request.body)
        else:
            pass

    def post(self, repository):
        """
        Handle the query for a repository
        Receive on field `data` a list with hash fo terms to be searched
        Return a JSON object with file id that match with the query
        :param repository: repository on where are the indexes
        :return: None
        """
        response = {
            "ok": False,
            "data": []
        }
        if self.json_args is not None:
            response["ok"] = True
            response["data"] = QueryFilter(self.json_args['data'], repository).run_query()
        self.write(response)

    def put(self, repository):
        """
        Handle the insertion of an index
        Receive a file that represent the index
        Return a JSON object that indicates the successful of the operation
        :param repository: Index owner
        :return: None
        """
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
        """
        Handle the deletion of an index
        Receive on field `data` a list with the indexes that will be deleted
        Return a JSON object that indicates the successful of the operation
        :param repository: Index owner
        :return: None
        """
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
