import unittest
from typing import List
import os
import json

from ctakesclient.typesystem import CtakesJSON, Polarity, UmlsConcept, MatchText
from .test_resources import PathResource, LoadResource

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

    def test_sort_concept_list_match_chest(self):
        """
        Test fix for
        https://github.com/comorbidity/ctakes-client-python/issues/8
        """
        snomed1 = UmlsConcept({'code': '51185008',  'cui': 'C0817096', 'codingScheme': 'SNOMEDCT_US', 'tui': 'T029'})
        snomed2 = UmlsConcept({'code': '261179002', 'cui': 'C0817096', 'codingScheme': 'SNOMEDCT_US', 'tui': 'T029'})
        loinc1 = UmlsConcept({'code': 'LP7138-3',  'cui': 'C1442171', 'codingScheme': 'LNC', 'tui': 'T029'}) # broader match entry

        conceptAttributes1 = [snomed1, snomed2, loinc1]
        conceptAttributes2 = [snomed2, snomed1, loinc1]
        conceptAttributes3 = [loinc1, snomed1, snomed2]
        conceptAttributes4 = [loinc1, snomed2, snomed1]

        self.assertEqual(MatchText.sort_concepts(conceptAttributes1), MatchText.sort_concepts(conceptAttributes2))
        self.assertEqual(MatchText.sort_concepts(conceptAttributes1), MatchText.sort_concepts(conceptAttributes3))
        self.assertEqual(MatchText.sort_concepts(conceptAttributes1), MatchText.sort_concepts(conceptAttributes4))


if __name__ == '__main__':
    unittest.main()
