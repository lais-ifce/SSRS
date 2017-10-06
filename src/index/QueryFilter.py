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
            enc_path, len_filter, num_hash, data = pickle.load(file)
            file.close()
            return enc_path, len_filter, num_hash, data
        except Exception as e:
            print(e)
            raise

    def run_query(self):
        result = []
        for p in self.filters:
            enc_path, len_f, n_hash, data = self.load_filter(self.path + p)
            check = 0
            for t in self.terms:
                f = (1 << len_f)
                for i in self.prepare_term(t, len_f, n_hash):
                    f |= (1 << i)
                if data & f == f:
                    check += 1
            if check == len(self.terms):
                result.append((p, enc_path))
        return result, len(result)

