from typing import List
import os
import logging
import requests
from ctakesclient.exceptions import ClientError
from ctakesclient.typesystem import Span, Polarity

#######################################################################################################################
#
# HTTP Client for Medical Language
#
# https://github.com/Machine-Learning-for-Medical-Language/cnlp_transformers#negation-api
#
#######################################################################################################################

def get_url_cnlp_negation() -> str:
    """
    https://github.com/Machine-Learning-for-Medical-Language/cnlp_transformers#negation-api

    :return: CTAKES_URL_NEGATION env variable or default using localhost
    """
    return os.environ.get('URL_CNLP_NEGATION', 'http://localhost:8000/negation/process')

def list_polarity(sentence: str, spans: list, url=get_url_cnlp_negation()) -> List[Polarity]:
    """
    :param sentence: clinical text to send to cTAKES
    :param spans: list of spans where each span is a tuple of (begin,end)
    :param url: Clinical NLP Transformer: Negation API
    :return: List of Polarity (positive or negated)
    """
    doc = {'doc_text': sentence, 'entities': spans}

    response = requests.post(url=url, json=doc).json()
    polarities = list()

    for status in response['statuses']:
        # NOT negated (double negative)
        if status == -1:
            polarities.append(Polarity.pos)
        # Negated
        elif status == 1:
            polarities.append(Polarity.neg)
        else:
            raise ClientError(f'negate-api unknown {status}, url= {url}')

    if len(spans) != len(polarities):
        raise ClientError(f'Number of Spans and Polarities did not match: {spans}, {polarities}')

    return polarities

def map_polarity(sentence: str, spans: list, url=get_url_cnlp_negation()) -> dict:
    """
    :param sentence: clinical text to send to cTAKES
    :param spans: list of spans where each span is a tuple of (begin,end)
    :param url: Clinical NLP Transformer: Negation API
    :return: Map of Polarity key=span, value=polarity
    """
    polarities = list_polarity(sentence, spans, url)
    mapped = dict()

    for span, polarity in zip(spans, polarities):
        mapped[span] = polarity

    return mapped
