"""HTTP client for medical language"""

import os
import logging
import requests
from ctakesclient.typesystem import CtakesJSON

###############################################################################
#
# https://github.com/Machine-Learning-for-Medical-Language/ctakes-covid-container
#
# https://github.com/Machine-Learning-for-Medical-Language/cnlp_transformers#negation-api
#
###############################################################################


def get_url_ctakes_rest() -> str:
    """
    https://github.com/Machine-Learning-for-Medical-Language/ctakes-covid-container

    :return: URL_CTAKES_REST env variable or default using localhost
    """
    return os.environ.get(
        'URL_CTAKES_REST',
        'http://localhost:8080/ctakes-web-rest/service/analyze')

def ascii(sentence:str) -> bytes:
    """
    https://pythonguides.com/remove-unicode-characters-in-python/#:~:text=In%20python%2C%20to%20remove%20non,decode().
    :param sentence:
    :return: sentence REMOVED of unicode chars - note LENGTH of text input may change!
    """
    return sentence.encode("ascii", "ignore")

def utf8(sentence:str) -> bytes:
    """
    https://stackoverflow.com/questions/34618149/post-unicode-string-to-web-service-using-python-requests-library
    :param sentence:
    :return: sentence ESCAPED unicode chars - note LENGTH of text input may change!
    """
    # import re
    # return re.sub(r'[^\u1F600-\u1F64F ]|[^\u1F300-\u1F5FF ]', " ", sentence)
    return sentence.encode("utf-8")

def post(sentence: str, url=get_url_ctakes_rest()) -> dict:
    """
    :param sentence: clinical text to send to cTAKES
    :param url: cTAKES REST server fully qualified path
    :return: dict JSON response from cTAKES
    """
    logging.debug(url)
    # TODO: consider exposing a pass-through timeout parameter
    return requests.post(url, data=sentence).json()  # pylint: disable=missing-timeout


def extract(sentence: str, url=get_url_ctakes_rest()) -> CtakesJSON:
    """
    :param sentence: clinical text to send to cTAKES
    :param url: cTAKES REST server fully qualified path
    :return: CtakesJSON wrapper
    """
    return CtakesJSON(post(sentence, url))
