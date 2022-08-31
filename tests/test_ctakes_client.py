import os
import json
import unittest
from ctakes import bsv_reader
from ctakes import ctakes_client
from ctakes.ctakes_client import CtakesJSON, Polarity

from tests import test_resources
from tests.test_resources import COVID_SYMPTOMS_BSV
from tests.test_resources import TEST_PHYSICIAN_NOTE_TXT
from tests.test_resources import TEST_PHYSICIAN_NOTE_JSON

def pretty(result: dict):
    print(json.dumps(result, indent=4))

class TestCtakesJSON(unittest.TestCase):

    def test_covid_symptoms_exist_in_response(self):
        """
        Symptoms of COVID-19
        https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html
        """
        for bsv in bsv_reader.list_bsv(COVID_SYMPTOMS_BSV):
            cuis = ctakes_client.extract(bsv.text).list_concept_cui()
            self.assertTrue(bsv.code in cuis, f'{bsv.__dict__} not found in response')

    def test_physician_note(self):
        physician_note = test_resources.load(TEST_PHYSICIAN_NOTE_TXT)
        expected = test_resources.load(TEST_PHYSICIAN_NOTE_JSON)

        raw = ctakes_client.post(physician_note)

        actual1 = ctakes_client.extract(physician_note).as_json()
        actual2 = ctakes_client.extract(physician_note).as_json()

        unittest.TestCase.maxDiff = None

        self.assertDictEqual(actual1, actual2, 'calling service twice produces same results')
        self.assertDictEqual(expected, actual1, 'JSON did not match round trip serialization')




