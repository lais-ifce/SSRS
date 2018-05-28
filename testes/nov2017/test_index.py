from src.index.PersistentFilter import PersistentFilter
from os import path

words = open(path.join(path.dirname(path.abspath(__file__)), "ten_thousand.txt"), "r").readlines()[0].split(" ")


def index(terms):
    pf = PersistentFilter(terms, "/tmp/perf_test", "688787d8ff144c502c7f5cffaafe2cc588d86079f9de88304c26b0cb99ce91c6")
    pf.build_filter()
    pf.save_filter()


def test(start, end):
    for i in range(start, end+1):
        index(words[:i])


if __name__ == "__main__":
    test(100, 10000)
