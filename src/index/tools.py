import textract
from hashlib import md5
import time
import os


LANG = {
    "EN": "en-us",
    "PT": "pt-br"
}


def extract(path):
    try:
        t1 = time.time()
        raw_data = textract.process(path)
        print("Extraction done in {} seconds".format(time.time()-t1))
        data = raw_data.decode('utf-8').replace("\n", " ").split(" ")
        return data
    except Exception as e:
        print(e)
        raise


def normalize(data):
    try:
        data = [x.replace("-", "") for x in data]
        data = [x.lower() for x in data if x.isalnum()]
        return data
    except Exception as e:
        print(e)
        raise


def filter_stop(data, lang="EN"):
    try:
        stop = open(os.path.join(os.path.dirname(__file__), 'stopwords/') + LANG[lang], "r").read().splitlines()
        data = [x for x in data if x not in stop]
        return data
    except Exception as e:
        print(e)
        raise


def hash_terms(data, user_key):
    try:
        hash_data = [bytes(md5(bytes(x + user_key, 'utf-8')).hexdigest(), "utf-8") for x in data]
        return hash_data
    except Exception as e:
        print(e)
        raise
