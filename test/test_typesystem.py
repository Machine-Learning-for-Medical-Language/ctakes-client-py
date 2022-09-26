"""Tests for the typesystem module"""

import unittest

from ctakesclient.typesystem import CtakesJSON, Polarity, UmlsConcept, MatchText
from ctakesclient.typesystem import sort_concepts
from .test_resources import LoadResource


class TestCtakesJSON(unittest.TestCase):
    """Test case for json parsing"""

    def test_physician_note(self):
        reader = CtakesJSON(LoadResource.PHYSICIAN_NOTE_JSON.value)

        expected = {
            'headache', 'nausea', 'vomiting', 'chest pain', 'mental status'
        }
        sign_symptom_neg = [
            m.text for m in reader.list_sign_symptom(Polarity.neg)
        ]
        self.assertEqual(expected, set(sign_symptom_neg))

        expected = {'Diarrhea', 'cough'}
        sign_symptom_pos = [
            m.text for m in reader.list_sign_symptom(Polarity.pos)
        ]
        self.assertEqual(expected, set(sign_symptom_pos))

        self.assertEqual(0, len(reader.list_disease_disorder()),
                         'no diseases expected')
        self.assertEqual(0, len(reader.list_procedure()),
                         'no procedures expected')
        self.assertEqual(0, len(reader.list_medication()),
                         'no medications expected')

    def test_umls_concept_medical_entries_exist(self):
        expected = LoadResource.PHYSICIAN_NOTE_JSON.value
        actual = CtakesJSON(expected)

        self.assertDictEqual(
            expected, actual.as_json(),
            'ctakes json did not match before/after serialization')

        self.assertGreaterEqual(len(actual.list_match()), 1,
                                'response should have at least one match')
        self.assertGreaterEqual(len(actual.list_match_text()), 1,
                                'response should have at least one text match')
        self.assertGreaterEqual(len(actual.list_concept()), 1,
                                'response should have at least one concept')
        self.assertGreaterEqual(
            len(actual.list_concept_cui()), 1,
            'response should have at least one concept CUI')

    def test_sort_concept_list_match_chest(self):
        """
        Test fix for
        https://github.com/comorbidity/ctakes-client-python/issues/8
        """
        snomed1 = UmlsConcept({'code': '51185008',  'cui': 'C0817096',
                               'codingScheme': 'SNOMEDCT_US', 'tui': 'T029'})
        snomed2 = UmlsConcept({'code': '261179002', 'cui': 'C0817096',
                               'codingScheme': 'SNOMEDCT_US', 'tui': 'T029'})
        # broader match entry
        loinc1 = UmlsConcept({'code': 'LP7138-3',  'cui': 'C1442171',
                              'codingScheme': 'LNC', 'tui': 'T029'})

        concept_attributes1 = [snomed1, snomed2, loinc1]
        concept_attributes2 = [snomed2, snomed1, loinc1]
        concept_attributes3 = [loinc1, snomed1, snomed2]
        concept_attributes4 = [loinc1, snomed2, snomed1]

        self.assertEqual(sort_concepts(concept_attributes1),
                         sort_concepts(concept_attributes2))
        self.assertEqual(sort_concepts(concept_attributes1),
                         sort_concepts(concept_attributes3))
        self.assertEqual(sort_concepts(concept_attributes1),
                         sort_concepts(concept_attributes4))


if __name__ == '__main__':
    unittest.main()
