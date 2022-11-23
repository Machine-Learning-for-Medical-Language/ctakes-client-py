"""Tests for the transformer module"""

import os
import unittest
from unittest import mock

from ctakesclient import transformer


class TestTransformer(unittest.TestCase):
    """Test case for client cNLP extraction"""

    @mock.patch.dict(os.environ, {'URL_CNLP_NEGATION': ''})
    def test_server_url_default(self):
        self.assertEqual(transformer.get_url_cnlp_negation(), 'http://localhost:8000/negation/process')

    @mock.patch.dict(os.environ, {'URL_CNLP_NEGATION': 'http://example.com:2002/cnlp'})
    def test_server_url_override(self):
        self.assertEqual(transformer.get_url_cnlp_negation(), 'http://example.com:2002/cnlp')
