import unittest
import os
import json

from ctakesclient.typesystem import CtakesJSON, Polarity
from test_resources import PathResource, LoadResource

class TestCtakesJSON(unittest.TestCase):

    def test_physician_note(self):
        reader = CtakesJSON(LoadResource.physician_note_json.value)

        expected = {'headache', 'nausea', 'vomiting', 'chest pain', 'mental status'}
        sign_symptom_neg = [m.text for m in reader.list_sign_symptom(Polarity.neg)]
        self.assertEqual(expected, set(sign_symptom_neg))

        expected = {'Diarrhea', 'cough'}
        sign_symptom_pos = [m.text for m in reader.list_sign_symptom(Polarity.pos)]
        self.assertEqual(expected, set(sign_symptom_pos))

        self.assertEqual(0, len(reader.list_disease_disorder()), 'no diseases expected')
        self.assertEqual(0, len(reader.list_procedure()), 'no procedures expected')
        self.assertEqual(0, len(reader.list_medication()), 'no medications expected')

    def test_umls_concept_medical_entries_exist(self):
        expected = LoadResource.physician_note_json.value
        actual = CtakesJSON(expected)

        self.assertDictEqual(expected, actual.as_json(), 'ctakes json did not match before/after serialization')

        self.assertGreaterEqual(len(actual.list_match()), 1, 'response should have at least one match')
        self.assertGreaterEqual(len(actual.list_match_text()), 1, 'response should have at least one text match')
        self.assertGreaterEqual(len(actual.list_concept()), 1, 'response should have at least one concept')
        self.assertGreaterEqual(len(actual.list_concept_cui()), 1, 'response should have at least one concept CUI')


if __name__ == '__main__':
    unittest.main()
