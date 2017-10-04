from src.index.Filter import Filter
from math import ceil, log
import pickle


class PersistentFilter(Filter):
    def __init__(self, data, false=1.0E-6):
        super(PersistentFilter, self).__init__()
        self.data = data
        self.false_positive = false
        self.len_filter = 0
        self.num_hash = 0
        self.filter = 0

    def calc(self):
        try:
            len_filter = ceil((len(self.data) * log(self.false_positive)) / log(1.0 / (pow(2.0, log(2.0)))))
            num_hash = round(log(2.0) * self.len_filter / len(self.data))
            return int(len_filter), int(num_hash)
        except Exception as e:
            print(e)
            raise

    def build_filter(self):
        try:
            self.len_filter, self.num_hash = self.calc()
            self.filter = (1 << self.len_filter)
            for t in self.data:
                for i in self.prepare_term(t, self.len_filter, self.num_hash):
                    self.filter |= (1 << i)
            return True
        except Exception as e:
            print(e)
            raise

    def save_filter(self, path):
        try:
            file = open(path, "wb")
            pickle.dump((self.len_filter, self.num_hash, self.filter), file)
            file.close()
            return True
        except Exception as e:
            print(e)
            raise
