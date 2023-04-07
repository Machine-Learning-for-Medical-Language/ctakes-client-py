"""HTTP client for medical language"""

import os
import logging

import httpx

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
    url = os.environ.get("URL_CTAKES_REST")
    return url or "http://localhost:8080/ctakes-web-rest/service/analyze"


async def post(sentence: str, url: str = None, client: httpx.AsyncClient = None) -> dict:
    """
    Sends clinical text to cTAKES for analysis and returns the raw server response

    You likely want the higher-level `extract` method instead of this one.
    For one, it will return a nice `CtakesJSON` object instead of raw json.
    For another, the raw cTAKES response has some oddities, like utf16-based span indexes,
    which `extract` fixes for you.

    :param sentence: clinical text to send to cTAKES
    :param url: cTAKES REST server fully qualified path
    :param client: optional existing HTTPX client session
    :return: Parsed json response from cTAKES
    """
    url = url or get_url_ctakes_rest()
    client = client or httpx.AsyncClient()
    logging.debug(url)
    response = await client.post(
        url,
        content=sentence.encode("utf8"),
        headers={
            "Content-Type": "text/plain; charset=UTF-8",
        },
    )
    response.raise_for_status()
    return response.json()


async def extract(sentence: str, url: str = None, client: httpx.AsyncClient = None) -> CtakesJSON:
    """
    Send clinical text to cTAKES for analysis and packages the response up for you

    :param sentence: clinical text to send to cTAKES
    :param url: cTAKES REST server fully qualified path
    :param client: optional existing HTTPX client session
    :return: CtakesJSON wrapper
    """
    response = await post(sentence, url=url, client=client)
    ner = CtakesJSON(response)
    _adjust_character_indexes(sentence, ner)  # Fix Java character indexes into Python ones
    return ner


###############################################################################
#
# Helpers
#
###############################################################################


def _utf16le_to_unicode_index(utf16: bytes, code_point_index: int) -> int:
    """
    Adjust one utf-16-le-code-point-index into a character-index for the given string
    """
    bytes_index = code_point_index * 2  # all code points are 2-bytes
    prefix = utf16[0:bytes_index].decode("utf-16-le")
    return len(prefix)  # and the length of that is the character index into the original unicode string


def _adjust_character_indexes(original: str, ner: CtakesJSON) -> None:
    """
    Adjust any span begin/end values from a cTAKES utf16-code-point-index into a character-index

    cTAKES responses give very Java-centric begin/end values as the code-point index into
    a utf16 encoding of the given string. But as a Python module, we should instead expose
    character indexes in case anyone wants to go back to the original string.

    So this method fixes all found span indexes into a more Pythonic character index.
    This is important to do because `ctakesclient.transformer` does expect the given
    spans to be character indexes. So if we don't do this, we'll get odd results from it.

    In practice, this is often the same position value -- it only really changes for unicode
    scalar values higher than U+FFFF (i.e. those that can't be encoded in just two bytes).
    """
    # Try to early exit by seeing if any character in the source is actually above U+FFFF (usually not)
    for c in original:
        if ord(c) > 0xFFFF:
            break
    else:
        return  # nothing to do, utf16-code-points happen to be the same as characters, so early exit

    # Ah well, looks like we'll have to actually translate the indexes

    utf16 = original.encode("utf-16-le")  # use low-endian encoding to avoid a byte-order-mark messing up our counts
    matches = ner.list_match()
    cache = {}  # use a cache, just because a lot of indexes do get re-used between concepts
    for match in matches:
        # We could try to be clever here and use the length of match.text to calculate the correct end position,
        # but I have some concerns that match.text is maybe unicode-normalized and doesn't represent the text in
        # the original source text byte-for-byte. So just to be super-safe, convert both begin and end by looking
        # at the source text, since that's where they were defined from.
        for index_attr in ["begin", "end"]:
            index = getattr(match, index_attr)
            if index in cache:
                setattr(match, index_attr, cache[index])
            else:
                value = _utf16le_to_unicode_index(utf16, index)
                setattr(match, index_attr, value)
                cache[index] = value
