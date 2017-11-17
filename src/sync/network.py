from src.index.tools import debug
from src.config import *

from base64 import b64encode

import requests
import os


class SyncNetwork:
    """
    This class is responsible for keeping the filesystem data in sync with remote servers.
    It supports downloading and uploading encrypted blocks, currently in synchronous manner.
    """
    def __init__(self, fs_low, fs_root, remote):
        """
        Create a new network sync.
        :param fs_low:
        :param fs_root:
        :param remote:
        """
        self._fs_low = fs_low
        self._fs_root = fs_root
        self._remote = remote

        self._session = requests.Session()
        self._session.verify = CONFIG_FOLDER + '/trusted'

    def get_remote_configuration(self, config):
        """
        Retrieve the remote filesystem configuration.
        :return:
        """
        r = self._session.get(self._remote + '/get/' + b64encode(config.encode()).decode())
        if r.status_code is not 200:
            return None

        return r.content

    def sync_index(self):
        """
        Sync the current filesystem indexes with the remote.
        :return:
        """
        source = os.path.join(self._fs_root, ".index")
        if os.path.exists(source):
            files = os.listdir(source)
            # files = [x for x in files if re.fullmatch(r'([0-9a-fA-F]){32}', x) is not None]
            remote = self._remote + "/" if self._remote[-1] != "/" else self._remote
            for f in files:
                with open(os.path.join(source, f), "rb") as file:
                    r = self._session.put(remote + "search", files={
                        "index": file
                    })
                    assert r.status_code == 200
                try:
                    os.remove(os.path.join(source, f))
                except Exception as e:
                    pass

    def upload_local_block(self, file):
        """
        Upload an encrypted block to the remote server.
        :param file:
        :return: True if the block was uploaded, False otherwise.
        """
        block_uri = b64encode(file.cipher.encode()).decode()

        debug('Uploading file %s' % (file.path,))
        try:
            with open(os.path.join(self._fs_low, file.cipher), 'rb') as f:
                req = self._session.put(self._remote + '/put/' + block_uri, data=f)
                if req.status_code is not 200:
                    return False
                file.hash = req.content.decode()
        except FileNotFoundError:
            return False

        return True

    def download_remote_block(self, file):
        """
        Download the specified block from the remote server.
        :param file:
        :return: True if the block was downloaded, False otherwise
        """
        block_uri = b64encode(file.cipher.encode()).decode()

        r = self._session.get(self._remote + '/get/' + block_uri, stream=True)
        if r.status_code is not 200:
            return False

        try:
            with open(os.path.join(self._fs_low, file.cipher), 'wb') as f:
                for chunk in r.iter_content(1024**2):
                    f.write(chunk)
        except FileNotFoundError:
            return False

        return True

