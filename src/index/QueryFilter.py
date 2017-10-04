from src.index.Filter import Filter
import os
import pickle


class QueryFilter(Filter):
    def __init__(self, terms, path):
        super(QueryFilter, self).__init__()
        self.terms = terms
        self.filters = self.get_filters(path)
        self.path = path

    @staticmethod
    def get_filters(path):
        try:
            files = os.listdir(path)
            return files
        except Exception as e:
            print(e)
            raise

    @staticmethod
    def load_filter(path):
        try:
            file = open(path, "rb")
            len_filter, num_hash, data = pickle.load(file)
            file.close()
            return len_filter, num_hash, data
        except Exception as e:
            print(e)
            raise

    def run_query(self):
        result = []
        for p in self.filters:
            len_f, n_hash, data = self.load_filter(self.path + p)
            check = False
            for t in self.terms:
                f = (1 << len_f)
                for i in self.prepare_term(t, len_f, n_hash):
                    f |= (1 << i)
                if data & f == f:
                    check = True
            if check:
                result.append(p)
        return result, len(result)

    def old_run_query(self, data, len_filter, num_hash):
        result = False
        for t in self.terms:
            r = self.prepare_term(t, len_filter, num_hash)
            f = (1 << len_filter)
            for i in r:
                f |= (1 << i)
            if data & f == f:
                result = True
        return result
