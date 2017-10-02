from src.mineirinho import Extractor


if __name__ == "__main__":
    ex = Extractor("../teste/in/file1", "../teste/out/file1", "MINHACHAVE", "PT", 1.0E-6)
    assert ex.extract()
    assert ex.normalize()
    assert ex.filter_stop()
    assert ex.calc()
    assert ex.hash_terms()
    assert ex.build_filter()
    assert ex.save_filter()
