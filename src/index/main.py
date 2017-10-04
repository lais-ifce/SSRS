import src.index.tools as tools
from src.index.QueryFilter import QueryFilter
from src.index.PersistentFilter import PersistentFilter


def test_index():
    file = "teste/file5.pdf"
    out_fil = "teste/.index/file5.out"
    key = "MYKEY"
    data = tools.hash_terms(tools.filter_stop(tools.normalize(tools.extract(file))), key)
    f = PersistentFilter(data)
    assert f.build_filter()
    assert f.save_filter(out_fil)


def test_query():
    terms = ["exponential"]
    key = "MYKEY"
    path = "teste/.index/"
    data = tools.hash_terms(tools.filter_stop(tools.normalize(terms)), key)
    q = QueryFilter(data, path)
    print(q.run_query())


if __name__ == "__main__":
    # test_index()
    test_query()
