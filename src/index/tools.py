import textract
from hashlib import md5


LANG = {
    "EN": "en-us",
    "PT": "pt-br"
}


def extract(path):
    try:
        raw_data = textract.process(path)
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
        stop = open("./stopwords/" + LANG[lang], "r").read().splitlines()
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
