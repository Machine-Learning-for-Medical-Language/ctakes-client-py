"""HTTP client for medical language"""

from typing import List
import os
import requests
from ctakesclient.exceptions import ClientError
from ctakesclient.typesystem import Polarity

###############################################################################
#
# https://github.com/Machine-Learning-for-Medical-Language/cnlp_transformers#negation-api
#
###############################################################################


def get_url_cnlp_negation() -> str:
    """
    https://github.com/Machine-Learning-for-Medical-Language/cnlp_transformers#negation-api

    :return: CTAKES_URL_NEGATION env variable or default using localhost
    """
    url = os.environ.get("URL_CNLP_NEGATION")
    return url or "http://localhost:8000/negation/process"


def list_polarity(sentence: str, spans: list, url: str = None) -> List[Polarity]:
    """
    :param sentence: clinical text to send to cTAKES
    :param spans: list of spans where each span is a tuple of (begin,end)
    :param url: Clinical NLP Transformer: Negation API
    :return: List of Polarity (positive or negated)
    """
    url = url or get_url_cnlp_negation()
    doc = {"doc_text": sentence, "entities": spans}

    # TODO: consider exposing a pass-through timeout parameter
    response = requests.post(url=url, json=doc)  # pylint: disable=missing-timeout
    response.raise_for_status()
    response = response.json()
    polarities = []

    for status in response["statuses"]:
        # NOT negated (double negative)
        if status == -1:
            polarities.append(Polarity.pos)
        # Negated
        elif status == 1:
            polarities.append(Polarity.neg)
        else:
            raise ClientError(f"negate-api unknown {status}, url= {url}")

    if len(spans) != len(polarities):
        raise ClientError("Number of Spans and Polarities did not match: " f"{spans}, {polarities}")

    return polarities


def map_polarity(sentence: str, spans: list, url: str = None) -> dict:
    """
    :param sentence: clinical text to send to cTAKES
    :param spans: list of spans where each span is a tuple of (begin,end)
    :param url: Clinical NLP Transformer: Negation API
    :return: Map of Polarity key=span, value=polarity
    """
    url = url or get_url_cnlp_negation()
    polarities = list_polarity(sentence, spans, url)
    mapped = {}

    for span, polarity in zip(spans, polarities):
        mapped[span] = polarity

    return mapped
