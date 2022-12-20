"""Tests for the client module"""

import os
import unittest
from unittest import mock

from ctakesclient import client
from ctakesclient.typesystem import Polarity

from tests.test_resources import LoadResource


class TestClient(unittest.TestCase):
    """Test case for client cTAKES extraction"""

    @mock.patch.dict(os.environ, {"URL_CTAKES_REST": ""})
    def test_server_url_default(self):
        self.assertEqual(client.get_url_ctakes_rest(), "http://localhost:8080/ctakes-web-rest/service/analyze")

    @mock.patch.dict(os.environ, {"URL_CTAKES_REST": "http://example.com:2002/blarg"})
    def test_server_url_override(self):
        self.assertEqual(client.get_url_ctakes_rest(), "http://example.com:2002/blarg")

    @mock.patch("ctakesclient.client.requests.post")
    def test_simple_extract(self, mock_post):
        """Confirm that a call to extract() gives us the expected CtakesJSON object"""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = LoadResource.PHYSICIAN_NOTE_JSON.value
        mock_post.return_value = mock_response
        ner = client.extract("input text does not matter")

        # CtakesJSON is tested more fully in test_typesystem.py.
        # We just want to make sure that we did actually load the json here.
        expected = {"Diarrhea", "cough"}
        sign_symptom_pos = [m.text for m in ner.list_sign_symptom(Polarity.pos)]
        self.assertEqual(expected, set(sign_symptom_pos))
