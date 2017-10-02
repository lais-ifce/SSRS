import textract
from math import ceil, log
from hashlib import md5
import mmh3
import fnv
import pickle

LANG = {
    "EN": "en-us",
    "PT": "pt-br"
}


class Extractor:
    def __init__(self, path, enc_path, key, lang="EN", false_positive=1.0E-6):
        self.path = path
        self.enc_path = enc_path
        self.user_key = key
        self.raw_data = []
        self.stop_words = []
        self.data = []
        self.filter = 0
        self.hash_data = []
        self.false_positive = false_positive
        self.len_filter = -1
        self.num_hash = -1
        self.lang = lang

    def extract(self):
        try:
            self.raw_data = textract.process(self.path)
            self.data = self.raw_data.decode('utf-8').replace("\n", " ").split(" ")
            return True
        except Exception as e:
            print(e)
            return False

    def normalize(self):
        try:
            self.data = [x.replace("-", "") for x in self.data]
            self.data = [x.lower() for x in self.data if x.isalnum()]
            return True
        except Exception as e:
            print(e)
            return False

    def filter_stop(self):
        try:
            stop = open("./stopwords/" + LANG[self.lang], "r").read().splitlines()
            self.data = [x for x in self.data if x not in stop]
            return True
        except Exception as e:
            print(e)
            return False

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
                    bits.append(mmh3.hash(t, primes[i]) % self.len_filter)
                for i in bits:
                    self.filter |= (1 << i)
            return True
        except Exception as e:
            print(e)
            return False

    def save_filter(self):
        try:
            file = open(self.enc_path, "wb")
            pickle.dump(self.filter, file)
            file.close()
            return True
        except Exception as e:
            print(e)
            return False


primes = [
    6947, 6949, 6959, 6961, 6967, 6971, 6977, 6983, 6991, 6997, 7001, 7013, 7019, 7027, 7039, 7043, 7057, 7069,
    7079, 7103, 7109, 7121, 7127, 7129, 7151, 7159, 7177, 7187, 7193, 7207, 7211, 7213, 7219, 7229, 7237, 7243,
    7247, 7253, 7283, 7297, 7307, 7309, 7321, 7331, 7333, 7349, 7351, 7369, 7393, 7411, 7417, 7433, 7451, 7457,
    7459, 7477, 7481, 7487, 7489, 7499, 7507, 7517, 7523, 7529, 7537, 7541, 7547, 7549, 7559, 7561, 7573, 7577,
    7583, 7589, 7591, 7603, 7607, 7621, 7639, 7643, 7649, 7669, 7673, 7681, 7687, 7691, 7699, 7703, 7717, 7723,
    7727, 7741, 7753, 7757, 7759, 7789, 7793, 7817, 7823, 7829, 7841, 7853, 7867, 7873, 7877, 7879, 7883, 7901,
    7907, 7919
]
