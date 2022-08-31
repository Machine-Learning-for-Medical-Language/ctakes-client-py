import unittest
import os
import json

from ctakes.ctakes_json import CtakesJSON, Polarity
import test_resources
from test_resources import TEST_PHYSICIAN_NOTE_JSON

class TestCtakesJSON(unittest.TestCase):

    def test_physician_note(self, physician_note=TEST_PHYSICIAN_NOTE_JSON):
        reader = CtakesJSON(test_resources.load(physician_note))

        expected = {'headache', 'nausea', 'vomiting', 'chest pain', 'mental status'}
        sign_symptom_neg = [m.text for m in reader.list_sign_symptom(Polarity.neg)]
        self.assertEqual(expected, set(sign_symptom_neg))

        expected = {'Diarrhea', 'cough'}
        sign_symptom_pos = [m.text for m in reader.list_sign_symptom(Polarity.pos)]
        self.assertEqual(expected, set(sign_symptom_pos))

        self.assertEqual(0, len(reader.list_disease_disorder()), 'no diseases expected')
        self.assertEqual(0, len(reader.list_procedure()), 'no procedures expected')
        self.assertEqual(0, len(reader.list_medication()), 'no medications expected')
        self.assertEqual(0, len(reader.list_identified_annotation()), 'no custom dict expected')

    def test_umls_concept_medical_entries_exist(self, physician_note_json=TEST_PHYSICIAN_NOTE_JSON):
        expected = test_resources.load(physician_note_json)
        actual = CtakesJSON(expected)

        self.assertDictEqual(expected, actual.as_json(), 'ctakes json did not match before/after serialization')

        self.assertGreaterEqual(len(actual.list_match()), 1, 'response should have at least one match')
        self.assertGreaterEqual(len(actual.list_match_text()), 1, 'response should have at least one text match')
        self.assertGreaterEqual(len(actual.list_concept()), 1, 'response should have at least one concept')
        self.assertGreaterEqual(len(actual.list_concept_cui()), 1, 'response should have at least one concept CUI')


if __name__ == '__main__':
    unittest.main()
