import src.index.tools as tools
from src.index.QueryFilter import QueryFilter
from src.index.PersistentFilter import PersistentFilter
import os
from hashlib import sha1


def test_index(path):
    files = [x for x in os.listdir(path) if ".pdf" in x]
    for i in files:
        file = path + i
        out_fil = path + ".index/" + sha1(bytes(path + i, 'utf-8')).hexdigest()
        key = "MYKEY"
        print("Indexing " + i)
        data = tools.hash_terms(tools.filter_stop(tools.normalize(tools.extract(file))), key)
        if len(data) != 0:
            f = PersistentFilter(data)
            print("Building filter for " + i)
            assert f.build_filter()
            assert f.save_filter(out_fil, path + i)
        else:
            print("No terms for " + i)
        print("Job done for " + i + "\n" + "-"*80)
    print(len(files))


def test_query(base, query):
    terms = query.split(" ")
    key = "MYKEY"
    path = base + ".index/"
    data = tools.hash_terms(tools.filter_stop(tools.normalize(terms)), key)
    q = QueryFilter(data, path)
    print(q.run_query())


if __name__ == "__main__":
    pass
