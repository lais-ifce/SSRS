from server.QueryFilter import QueryFilter
from client.index.tools import *

KEY = "fd7d6b3167c9c873861208a03878bd68c1cbdef6b40a722079cfe0fa9a4c00db"
terms = ["xcwekXLnZd", "xLXyxmIGZM", "ETUuOOzmhj", "SvfUFaFPGl", "rDneHNdsxy"]
terms = [x.decode('utf-8') for x in hash_terms(filter_stop(normalize(terms)), KEY)]
print(terms)

for z in "f".split():
    print("Filtro >> {}".format(z))
    for i in range(3):
        print("Round >> {}".format(i+1))
        for j in range(len(terms)):
            qf = QueryFilter(terms[:j+1], "out/{}".format(z)).run_query()
            del qf
