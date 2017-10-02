from math import ceil, log
from hashlib import md5
import mmh3
import fnv
import pickle


class Filter:
    def __init__(self, terms, key, enc_path, false=1.0E-6):
        self.data = terms
        self.hash_data = []
        self.user_key = key
        self.enc_path = enc_path
        self.len_filter = -1
        self.num_hash = -1
        self.false_positive = false
        self.filter = -1
        self.primes = [6947, 6949, 6959, 6961, 6967, 6971, 6977, 6983, 6991, 6997, 7001, 7013, 7019, 7027, 7039,
                       7043, 7057, 7069, 7079, 7103, 7109, 7121, 7127, 7129, 7151, 7159, 7177, 7187, 7193, 7207]

    def calc(self):
        try:
            self.len_filter = ceil((len(self.data) * log(self.false_positive)) / log(1.0 / (pow(2.0, log(2.0)))))
            self.num_hash = round(log(2.0) * self.len_filter / len(self.data))
            return True
        except Exception as e:
            print(e)
            return False

    def hash_terms(self):
        try:
            self.hash_data = [bytes(md5(bytes(x + self.user_key, 'utf-8')).hexdigest(), "utf-8") for x in self.data]
            return True
        except Exception as e:
            print(e)
            return False

    def build_filter(self):
        try:
            self.filter = (1 << self.len_filter)
            for t in self.hash_data:
                bits = [fnv.hash(t) % self.len_filter]
                for i in range(self.num_hash - 1):
                    bits.append(mmh3.hash(t, self.primes[i]) % self.len_filter)
                for i in bits:
                    self.filter |= (1 << i)
            return True
        except Exception as e:
            print(e)
            return False

    def save_filter(self):
        try:
            file = open(self.enc_path, "wb")
            pickle.dump((self.len_filter, self.num_hash, self.filter), file)
            file.close()
            return True
        except Exception as e:
            print(e)
            return False

    def load_filter(self):
        try:
            file = open(self.enc_path, "rb")
            self.len_filter, self.num_hash, self.filter = pickle.load(file)
            file.close()
            return True
        except Exception as e:
            print(e)
            return False
