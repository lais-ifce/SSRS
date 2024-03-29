import os
import pickle
import time

from common.Filter import Filter

from client.index.tools import debug
from config import *


class QueryFilter(Filter):
    """
    Class that extends Filter class. Have methods to load filters and perform queries
    """
    def __init__(self, terms, path):
        """
        :param terms: list of hashed terms to be searched
        :param path: path to directory with user's indexes
        """
        super(QueryFilter, self).__init__()
        self.path = os.path.join(INDEX_ROOT, path)
        self.terms = terms
        self.filters = self.get_filters(self.path)

    @staticmethod
    def get_filters(path):
        """
        Method for get all filters on the specified path
        :param path: path for a folder with indexes
        :return: list of filenames
        """
        try:
            files = os.listdir(path)
            debug("Retrieved {} indexes".format(len(files)))
            return files
        except Exception as e:
            debug(e, True)
            raise

    @staticmethod
    def load_filter(path):
        """
        Load a filter from disk
        :param path: filter path
        :return: 4-tuple with the encrypted path, filter size in bits, number of hash functions and the filter itself
        """
        try:
            file = open(path, "rb")
            len_filter, num_hash, data = pickle.load(file)
            file.close()
            debug("Filter {} loaded".format(path))
            return len_filter, num_hash, data
        except Exception as e:
            debug(e, True)
            raise

    def run_query(self):
        """
        Performs the search over all filters that belong to an user, with the terms defined in constructor
        :return: a list of encrypted path of the files that probably match with the query
        """
        result = []
        t0 = time.time()
        for p in self.filters:
            debug(os.path.join(self.path, p))
            len_f, n_hash, data = self.load_filter(os.path.join(self.path, p))
            if n_hash < 1:
                continue
            f = (1 << len_f)
            for t in self.terms:
                for i in self.prepare_term(t, len_f, n_hash):
                    f |= (1 << i)
            if data & f == f:
                result.append(p)
        debug("Search with {} terms in {} filters performed in {} seconds".format(len(self.terms),
              len(self.filters), int(time.time()-t0)))
        return result
