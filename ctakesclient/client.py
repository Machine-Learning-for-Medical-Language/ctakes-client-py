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


def post(sentence: str, url=get_url_ctakes_rest()) -> dict:
    """
    :param sentence: clinical text to send to cTAKES
    :param url: cTAKES REST server fully qualified path
    :return:
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
