import tornado.web
import os
import boto3

from botocore.exceptions import ClientError as S3ClientError

from concurrent.futures import ThreadPoolExecutor

from tempfile import TemporaryFile
from hashlib import md5

from config import S3BUCKET

bucket = boto3.resource('s3').Bucket(S3BUCKET)
executor = ThreadPoolExecutor(2)


class GETHandler(tornado.web.RequestHandler):

    def prepare(self):
        self.set_header('Content-Type', 'application/octet-stream')

    @tornado.gen.coroutine
    def get(self, repo, filename):
        try:
            yield executor.submit(bucket.download_file,
                                  repo + filename,
                                  os.path.join(repo, filename))
        except S3ClientError:
            raise tornado.web.HTTPError(404)

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

        os.unlink(os.path.join(repo, filename))

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
            try:
                with open(os.path.join(repo, 'key'), 'w') as f:
                    f.write(self.request.headers['X-SSRS-KEY'])
            except KeyError:
                os.rmdir(repo)
                raise tornado.web.HTTPError(401)

        with open(os.path.join(repo, 'key')) as f:
            try:
                if f.read() != self.request.headers['X-SSRS-KEY']:
                    raise tornado.web.HTTPError(403)
            except KeyError:
                raise tornado.web.HTTPError(401)

        content_hash = md5()
        with open(os.path.join(repo, filename), 'wb') as f:
            self.temp_file.seek(0)
            while True:
                data = yield executor.submit(self.temp_file.read, 1024**2)
                if len(data) == 0:
                    break
                content_hash.update(data)
                yield executor.submit(f.write, data)

        try:
            yield executor.submit(bucket.upload_file,
                                  os.path.join(repo, filename),
                                  repo + filename)
        except S3ClientError:
            raise tornado.web.HTTPError(500)
        finally:
            os.unlink(os.path.join(repo, filename))

        self.write(content_hash.hexdigest())
