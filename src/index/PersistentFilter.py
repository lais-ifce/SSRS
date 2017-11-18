from src.index.Filter import Filter
from src.index.tools import *
from src.config import *
from math import ceil, log
from base64 import b64encode
import pickle
import time
import textract


class PersistentFilter(Filter):
    """
    Class that extends the Filter class. Have methods to built the filter and save it in a persistent way
    """
    def __init__(self, plain_path, enc_path, key, lang='EN', false=1.0E-6):
        """
        :param plain_path: plain path to file that will be indexed
        :param enc_path: encrypted path to file that will be indexed
        :param key: user keypass
        :param lang: document's language
        :param false: float number that determine the false positive tolerance. default is 1.0E-6
        """

        super(PersistentFilter, self).__init__()

        self.data = hash_terms(filter_stop(normalize(self.extract(plain_path)), lang), key)
        self.false_positive = false
        self.len_filter = 0
        self.num_hash = 0
        self.filter = 0
        self.path = plain_path
        self.enc_path = enc_path

    @staticmethod
    def extract(path):
        """
        Perform a extraction of text from a specified file
        :param path: path to the file
        :return: a list of terms
        """
        try:
            t1 = time.time()
            raw_data = textract.process(path)
            debug("Extraction done in {} seconds".format(time.time()-t1))
            data = raw_data.decode('utf-8').replace("\n", " ").split(" ")
            return data
        except Exception as e:
            debug(e, True)
            raise

    def calc(self):
        """
        Defines the optimal filter size and the optimal hash functions quantity for the false positive parameter
        :return: a 2-tuple with the filter size and how much hash functions are needed
        """
        try:
            m = ceil((len(self.data) * log(self.false_positive)) / log(1.0 / (pow(2.0, log(2.0)))))
            k = round(log(2.0) * m / len(self.data))
            return m, k
        except Exception as e:
            debug(e, True)
            raise

    def build_filter(self):
        """
        Method that build the filter
        :return: True if the build is successful
        """
        try:
            if len(self.data) < 1:
                debug("File witout text")
                return True
            t1 = time.time()
            self.len_filter, self.num_hash = self.calc()
            self.filter = (1 << int(self.len_filter))
            for t in self.data:
                for i in self.prepare_term(t, self.len_filter, self.num_hash):
                    self.filter |= (1 << i)
            debug("Filter Built in {} seconds".format(time.time()-t1))
            return True
        except Exception as e:
            debug(e, True)
            raise

    def save_filter(self):
        """
        Method that save the filter
        :return: True if the operation is successful
        """
        try:
            file = open(self.enc_path, "wb")
            pickle.dump((self.len_filter, self.num_hash, self.filter), file)
            file.close()
            debug("Filter stored with {} terms, {} hash functions, {} bits".format(len(self.data), self.num_hash,
                                                                                   self.len_filter))
            return True
        except Exception as e:
            debug(e, True)
            raise


def index_loop(command, fs_root, key):
    """
    File system indexer
    :param command: 3-tuple with event id, path to file and ecrypted path
    :param fs_root: file system root
    :param key: user key
    :return: None
    """
    while True:
        ev, path, enc_path = command.get()
        repo = b64encode(fs_root.encode()).decode()
        if ev == 1:
            debug("Exiting")
            break
        if not os.path.exists(os.path.join(INDEX_ROOT, repo)):
            try:
                os.mkdir(os.path.join(INDEX_ROOT, repo))
            except Exception as e:
                debug(e, True)
                raise
        debug("path:", path)
        debug("fsroot", fs_root)
        path = path[1:] if path[0] == "/" else path
        enc_path = os.path.join(INDEX_ROOT, repo, b64encode(enc_path.encode()).decode())
        if not os.path.basename(os.path.abspath(os.path.join(fs_root, path))).startswith(".") and ".index/" not in path:
            pf = PersistentFilter(os.path.join(fs_root, path), enc_path, key)
            assert pf.build_filter()
            assert pf.save_filter()
