import mmh3
import fnv


class Filter:
    def __init__(self):
        self.primes = [6947, 6949, 6959, 6961, 6967, 6971, 6977, 6983, 6991, 6997, 7001, 7013, 7019, 7027, 7039,
                       7043, 7057, 7069, 7079, 7103, 7109, 7121, 7127, 7129, 7151, 7159, 7177, 7187, 7193, 7207]

    def prepare_term(self, term, len_filter, num_hash):
        """
        Prepare terms to be inserted in filter
        :param term: a term to be hashed
        :param len_filter: size of filter in bits
        :param num_hash: number of hash functions
        :return: a list of bits that represent the term
        """
        if type(term) is not bytes:
            term = bytes(term, 'utf-8')
        bits = [fnv.hash(term) % len_filter]
        for i in range(num_hash - 1):
            bits.append(mmh3.hash(term, self.primes[i]) % len_filter)
        return bits
