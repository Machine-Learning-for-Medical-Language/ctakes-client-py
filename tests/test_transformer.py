"""Tests for the transformer module"""

import os
import unittest
from unittest import mock

import respx

from ctakesclient import transformer
from ctakesclient.typesystem import Polarity


class TestTransformer(unittest.IsolatedAsyncioTestCase):
    """Test case for client cNLP extraction"""

    @mock.patch.dict(os.environ, {"URL_CNLP_NEGATION": ""})
    def test_negation_url_default(self):
        self.assertEqual(transformer.get_url_cnlp_negation(), "http://localhost:8000/negation/process")

    @mock.patch.dict(os.environ, {"URL_CNLP_NEGATION": "http://example.com:2002/cnlp"})
    def test_negation_url_override(self):
        self.assertEqual(transformer.get_url_cnlp_negation(), "http://example.com:2002/cnlp")

    @mock.patch.dict(os.environ, {"URL_CNLP_TERM_EXISTS": ""})
    def test_term_exists_url_default(self):
        self.assertEqual(transformer.get_url_cnlp_term_exists(), "http://localhost:8000/termexists/process")

    @mock.patch.dict(os.environ, {"URL_CNLP_TERM_EXISTS": "http://example.com:2003/cnlp"})
    def test_term_exists_url_override(self):
        self.assertEqual(transformer.get_url_cnlp_term_exists(), "http://example.com:2003/cnlp")

    @respx.mock
    async def test_negation_polarity(self):
        """Confirm that a basic call to map_polarity() works with the default negation model"""
        sentence = "input text sentence"
        spans = [(3, 5), (8, 13)]

        # Prepare mocked response
        respx.post(
            "http://localhost:8000/negation/process",
            json={"doc_text": sentence, "entities": spans},
        ).respond(json={"statuses": [1, -1]})

        # Make the actual call
        results = await transformer.map_polarity(sentence, spans)

        self.assertEqual(
            {
                (3, 5): Polarity.neg,
                (8, 13): Polarity.pos,
            },
            results,
        )

    @respx.mock
    async def test_term_exists_polarity(self):
        """Confirm that a basic call to map_polarity() works with the term exists model"""
        sentence = "input text sentence"
        spans = [(3, 5), (8, 13)]

        # Prepare mocked response
        respx.post(
            "http://localhost:8000/termexists/process",
            json={"doc_text": sentence, "entities": spans},
        ).respond(json={"statuses": [-1, 1]})

        # Make the actual call
        results = await transformer.map_polarity(sentence, spans, model=transformer.TransformerModel.TERM_EXISTS)

        self.assertEqual(
            {
                (3, 5): Polarity.neg,
                (8, 13): Polarity.pos,
            },
            results,
        )
