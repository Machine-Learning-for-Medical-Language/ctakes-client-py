import os
import json
import unittest
from ctakes.ctakes_json import CtakesJSON

class TestCtakesJSON(unittest.TestCase):

    def test(self, example='/your/path/to/ctakes.json'):

        if os.path.exists(example):
            with open(example, 'r') as fp:
                from_json = json.load(fp)
                reader = CtakesJSON(from_json)

                self.assertDictEqual(from_json, reader.as_json(), 'ctakes json did not match before/after serialization')

                self.assertGreaterEqual(len(reader.list_match()), 1, 'response should have at least one match')
                self.assertGreaterEqual(len(reader.list_match_text()), 1, 'response should have at least one text match')
                self.assertGreaterEqual(len(reader.list_concept()), 1, 'response should have at least one concept')
                self.assertGreaterEqual(len(reader.list_concept_cui()), 1, 'response should have at least one concept CUI')
