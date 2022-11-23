"""Tests for the filesystem module"""

import unittest

from ctakesclient import filesystem
from tests.test_resources import PathResource


class TestCovidSymptomsBSV(unittest.TestCase):
    """Test case for files loaded from bsv"""

    def test_covid_symptom_concepts(self):
        """
        Symptoms of COVID-19
        https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html
        """
        for bsv in filesystem.covid_symptoms():
            self.assertTrue(bsv.cui.startswith('C'), 'Concept CUI expected')
            self.assertTrue(bsv.tui.startswith('T'), 'Type TUI expected')
            self.assertIsNotNone(bsv.text)
            self.assertIsNotNone(bsv.pref)

            expected = ['SNOMEDCT_US', 'ICD10CM', 'HPO', 'CHV', 'NCI']

            self.assertTrue(bsv.vocab in expected, f'vocab not expected: {bsv.vocab}')

    def test_umls_semantic_types(self):
        bsv_list = filesystem.umls_semantic_groups()

        for bsv in bsv_list:
            self.assertEqual(4, len(bsv.group_id),
                             'Group Abbreviations are 4 chars')
            self.assertEqual(4, len(bsv.tui), 'TUI Abbreviations are 4 chars')
            self.assertTrue(bsv.tui.startswith('T'), 'Type TUI expected')
            self.assertIsNotNone(bsv.tui_label, 'TUI label should not be none')

        self.assertEqual(127, len(bsv_list), 'UMLS has 127 semantic types')
        self.assertEqual(127, len(set(bsv_list)), 'UMLS has 127 unique TUI')

    def test_list_bsv_semantics(self):
        semantics = filesystem.list_bsv_semantics(PathResource.SEMANTICS_BSV.value)
        self.assertEqual([
            {
                'group_id': 'ANAT',
                'group_label': 'Anatomy',
                'tui': 'T024',
                'tui_label': 'Tissue',
            },
            {
                'group_id': 'CHEM',
                'group_label': 'Chemicals & Drugs',
                'tui': 'T195',
                'tui_label': 'Antibiotic',
            },
        ], [x.as_json() for x in semantics])

    def test_list_bsv_concept(self):
        concepts = filesystem.list_bsv_concept(PathResource.CONCEPTS_BSV.value)
        self.assertEqual([
            {
                'cui': 'C0239134',
                'tui': 'T033',
                'code': '28743005',
                'vocab': 'SNOMEDCT_US',
                'text': 'Productive Cough',
                'pref': 'Cough',
            },
            {
                'cui': 'C0015672',
                'tui': 'T184',
                'code': '84229001',
                'vocab': 'SNOMEDCT_US',
                'text': 'Fatigue',
                'pref': 'Fatigue',
            },
        ], [x.as_json() for x in concepts])

    def test_map_cui_pref_takes_filename(self):
        cui_map = filesystem.map_cui_pref(PathResource.CONCEPTS_BSV.value)
        self.assertEqual({
            'C0239134': 'Cough',
            'C0015672': 'Fatigue',
        }, cui_map)

    def test_map_cui_pref_takes_list(self):
        cui_map = filesystem.map_cui_pref(filesystem.list_bsv_concept(PathResource.CONCEPTS_BSV.value))
        self.assertEqual({
            'C0239134': 'Cough',
            'C0015672': 'Fatigue',
        }, cui_map)


if __name__ == '__main__':
    unittest.main()
