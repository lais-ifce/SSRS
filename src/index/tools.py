from hashlib import md5
from src import config
import os
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

LANG = {
    "EN": "en-us",
    "PT": "pt-br"
}


def normalize(data):
    """
    Normalizes all text to lowercase, remove dashes and remove non alphanumeric terms
    :param data: list of terms to be processed
    :return: a list of normalized terms
    """
    try:
        data = [x.replace("-", "") for x in data]
        data = [x.lower() for x in data if x.isalnum()]
        debug("Normalized {} terms".format(len(data)))
        return data
    except Exception as e:
        debug(e, True)
        raise


def filter_stop(data, lang="EN"):
    """
    Filters all terms that are stopword
    :param data: list of normalized terms to be processed
    :param lang: language of terms. `EN` or `PT` default is `EN`
    :return:
    """
    try:
        stop = open(os.path.join(os.path.dirname(__file__), 'stopwords/') + LANG[lang], "r").read().splitlines()
        data = remove_duplicate(data)
        data = [x for x in data if x not in stop]
        debug("Stopwords filter result: {} terms".format(len(data)))
        return data
    except Exception as e:
        debug(e, True)
        raise


def remove_duplicate(data):
    """
    Remove duplicate terms
    :param data: terms to be processed
    :return: list of exclusive terms
    """
    unique = set()
    [unique.add(x) for x in data]
    debug("Remove duplicate: Before -> {} / After -> {}".format(len(data), len(unique)))
    return list(unique)


def hash_terms(data, user_key):
    """
    Compute a hash for each term with the user key to make it unique
    :param data: list unique normalized terms
    :param user_key: user key
    :return: list of hashed terms
    """
    try:
        hash_data = [bytes(md5(bytes(x + user_key, 'utf-8')).hexdigest(), "utf-8") for x in data]
        return hash_data
    except Exception as e:
        debug(e, True)
        raise


def debug(data, critical=False):
    """
    Print debug info if the `DEBUG` flag is `True` in `config.py` or if is a critical message
    :param data: message
    :param critical: bool to indicate if message is critical
    :return: None
    """
    if config.DEBUG and not critical:
        logging.info(data)
    elif critical:
        logging.critical(data)
