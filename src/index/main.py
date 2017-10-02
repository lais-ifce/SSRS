from src.index.Extractor import Extractor
from src.index.Filter import Filter


if __name__ == "__main__":
    ex = Extractor("teste/file1", "PT")
    assert ex.extract()
    assert ex.normalize()
    assert ex.filter_stop()
    fi = Filter(ex.data, "MYKEY", "teste/file1.out")
    assert fi.calc()
    assert fi.hash_terms()
    assert fi.build_filter()
    assert fi.save_filter()
    fi2 = Filter([], "MYKEY", "teste/file1.out")
    fi2.load_filter()

