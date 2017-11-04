from src.index.Filter import Filter
from src.index.tools import *
from math import ceil, log
import pickle
import time


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

        self.data = hash_terms(filter_stop(normalize(extract(plain_path)), lang), key)
        self.false_positive = false
        self.len_filter = 0
        self.num_hash = 0
        self.filter = 0
        self.path = plain_path
        self.enc_path = enc_path

    def calc(self):
        """
        Defines the optimal filter size and the optimal hash functions quantity for the false positive parameter
        :return: a 2-tuple with the filter size and how much hash functions are needed
        """
        try:
            len_filter = ceil((len(self.data) * log(self.false_positive)) / log(1.0 / (pow(2.0, log(2.0)))))
            num_hash = round(log(2.0) * self.len_filter / len(self.data))
            return int(len_filter), int(num_hash)
        except Exception as e:
            debug(e, True)
            raise

    def build_filter(self):
        """
        Method that build the filter
        :return: True if the build is successful
        """
        try:
            t1 = time.time()
            self.len_filter, self.num_hash = self.calc()
            self.filter = (1 << self.len_filter)
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
            file = open(self.path, "wb")
            pickle.dump((self.enc_path, self.len_filter, self.num_hash, self.filter), file)
            file.close()
            debug("Filter stored with {} terms, {} hash functions, {} bits".format(len(self.data), self.num_hash,
                                                                                   self.len_filter))
            return True
        except Exception as e:
            debug(e, True)
            raise
