"""
Use cNLP transformers to detect polarity of specific words in text.

For example, you might have cTAKES results, but want to know the difference between
"the patient has a cough" and "the patient does not have a cough".
In the former, the word cough has a positive polarity, in the latter a negative polarity.

cTAKES has some built-in negation ability, but it's not perfect.
These transformer models perform a bit better.

We offer multiple polarity detection models.
See: https://github.com/Machine-Learning-for-Medical-Language/cnlp_transformers
"""

import enum
import os
from typing import List, Tuple

import httpx

from ctakesclient.exceptions import ClientError
from ctakesclient.typesystem import Polarity


class TransformerModel(enum.Enum):
    # Use the cnlpt model slug as a value, in case that's convenient for any consumers
    NEGATION = "negation"
    TERM_EXISTS = "termexists"


def get_url_cnlp_negation() -> str:
    """
    https://github.com/Machine-Learning-for-Medical-Language/cnlp_transformers#negation-api

    :return: CTAKES_URL_NEGATION env variable or default using localhost
    """
    url = os.environ.get("URL_CNLP_NEGATION")
    return url or "http://localhost:8000/negation/process"


def get_url_cnlp_term_exists() -> str:
    """
    Grabs the URL for the termexists model.

    https://github.com/Machine-Learning-for-Medical-Language/cnlp_transformers/blob/main/src/cnlpt/api/termexists_rest.py

    :return: CTAKES_URL_TERM_EXISTS env variable or default using localhost
    """
    url = os.environ.get("URL_CNLP_TERM_EXISTS")
    return url or "http://localhost:8000/termexists/process"


async def list_polarity(
    sentence: str,
    spans: List[Tuple[int, int]],
    url: str = None,
    client: httpx.AsyncClient = None,
    model: TransformerModel = TransformerModel.NEGATION,
) -> List[Polarity]:
    """
    :param sentence: clinical text to send to cTAKES
    :param spans: list of spans where each span is a tuple of (begin,end)
    :param url: Clinical NLP Transformer: Negation API
    :param client: optional existing HTTPX client session
    :param model: which transformer model to use
    :return: List of Polarity (positive or negated)
    """
    client = client or httpx.AsyncClient()

    if model == TransformerModel.NEGATION:
        pos_status = -1  # NOT negated (double negative)
        neg_status = 1  # negated
        url = url or get_url_cnlp_negation()
    elif model == TransformerModel.TERM_EXISTS:
        pos_status = 1
        neg_status = -1
        url = url or get_url_cnlp_term_exists()
    else:
        raise ValueError(f"Transformer model '{model.value}' not recognized.")

    doc = {"doc_text": sentence, "entities": spans}
    response = await client.post(url=url, json=doc)
    response.raise_for_status()
    response = response.json()
    polarities = []

    for status in response["statuses"]:
        if status == pos_status:
            polarities.append(Polarity.pos)
        elif status == neg_status:
            polarities.append(Polarity.neg)
        else:
            raise ClientError(f"negate-api unknown {status}, url= {url}")

    if len(spans) != len(polarities):
        raise ClientError("Number of Spans and Polarities did not match: " f"{spans}, {polarities}")

    return polarities


async def map_polarity(
    sentence: str,
    spans: List[Tuple[int, int]],
    url: str = None,
    client: httpx.AsyncClient = None,
    model: TransformerModel = TransformerModel.NEGATION,
) -> dict:
    """
    :param sentence: clinical text to send to cTAKES
    :param spans: list of spans where each span is a tuple of (begin,end)
    :param url: Clinical NLP Transformer: Negation API
    :param client: optional existing HTTPX client session
    :param model: which transformer model to use
    :return: Map of Polarity key=span, value=polarity
    """
    polarities = await list_polarity(sentence, spans, url=url, client=client, model=model)
    return dict(zip(spans, polarities))
