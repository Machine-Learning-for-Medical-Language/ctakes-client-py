import unittest
import os
import json

from ctakes.ctakes_json import CtakesJSON

class TestCtakesJSON(unittest.TestCase):

    def test_parse_json(self, example_json='/your/path/to/ctakes.json'):

        if os.path.exists(example_json):
            with open(example_json, 'r') as f:
                from_json = json.load(f)

                reader = CtakesJSON(from_json)

                self.assertDictEqual(from_json, reader.as_json(), 'ctakes json did not match before/after serialization')

                self.assertGreaterEqual(len(reader.list_match()), 1, 'response should have at least one match')
                self.assertGreaterEqual(len(reader.list_match_text()), 1, 'response should have at least one text match')
                self.assertGreaterEqual(len(reader.list_concept()), 1, 'response should have at least one concept')
                self.assertGreaterEqual(len(reader.list_concept_cui()), 1, 'response should have at least one concept CUI')
        else:
            print(f'skipping test, example_json does not exist: {example_json}')
