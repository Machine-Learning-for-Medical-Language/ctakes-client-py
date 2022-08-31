import os
import logging
import requests
from ctakes.ctakes_json import UmlsTypeMention, UmlsConcept, MatchText, Polarity, CtakesJSON

#######################################################################################################################
#
# HTTP Client for CTAKES REST
#
# https://github.com/Machine-Learning-for-Medical-Language/ctakes-covid-container
#
#######################################################################################################################

def get_url_ctakes() -> str:
    """
    :return: CTAKES_URL_REST env variable or default using localhost
    """
    return os.environ.get('CTAKES_URL_REST', 'http://localhost:8080/ctakes-web-rest/service/analyze')

def post(sentence:str, url=get_url_ctakes()) -> dict:
    """
    :param sentence: clinical text to send to cTAKES
    :param url: cTAKES REST server fully qualified path
    :return:
    """
    logging.debug(url)
    return requests.post(url, data=sentence).json()

def extract(sentence:str, url=get_url_ctakes()) -> CtakesJSON:
    """
    :param sentence: clinical text to send to cTAKES
    :param url: cTAKES REST server fully qualified path
    :return: CtakesJSON wrapper
    """
    return CtakesJSON(post(sentence, url))