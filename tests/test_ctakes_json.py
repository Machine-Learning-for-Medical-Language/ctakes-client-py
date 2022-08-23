import unittest
from etl import store
from etl.ctakes.ctakes_json import CtakesJSON

class TestCtakesJSON(unittest.TestCase):

    def test_parse_json(self, example='/your/path/to/ctakes.json'):

        example = '/Users/andy/phi/i2b2/processed/1069/106913362/e5830e63ee070e734d5c0b2e66a5f19e/ctakes.json'

        if store.path_exists(example):
            from_json = store.read_json(example)
            reader = CtakesJSON(from_json)

            self.assertDictEqual(from_json, reader.as_json(), 'ctakes json did not match before/after serialization')

            self.assertGreaterEqual(len(reader.list_match()), 1, 'response should have at least one match')
            self.assertGreaterEqual(len(reader.list_match_text()), 1, 'response should have at least one text match')
            self.assertGreaterEqual(len(reader.list_concept()), 1, 'response should have at least one concept')
            self.assertGreaterEqual(len(reader.list_concept_cui()), 1, 'response should have at least one concept CUI')
