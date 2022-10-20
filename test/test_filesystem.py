"""Tests for the filesystem module"""

import unittest

import ctakesclient
from .test_resources import PathResource


class TestCovidSymptomsBSV(unittest.TestCase):
    """Test case for covid symptoms loaded from bsv"""

    def test_covid_symptom_concepts(self):
        """
        Symptoms of COVID-19
        https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html
        """
        for bsv in ctakesclient.filesystem.list_bsv_concept(
                PathResource.COVID_SYMPTOMS.value):
            self.assertTrue(bsv.cui.startswith('C'), 'Concept CUI expected')
            self.assertTrue(bsv.tui.startswith('T'), 'Type TUI expected')
            self.assertIsNotNone(bsv.text)
            self.assertIsNotNone(bsv.pref)

            expected = ['SNOMEDCT_US', 'ICD9CM', 'ICD10CM', 'HPO', 'CHV']

            self.assertTrue(bsv.vocab in expected, f'vocab not expected: {bsv.vocab}')


    def test_umls_semantic_types(self):
        bsv_list = ctakesclient.filesystem.list_bsv_semantics(
            PathResource.SEMANTIC_GROUPS.value)

        for bsv in bsv_list:
            self.assertEqual(4, len(bsv.group_id),
                             'Group Abbreviations are 4 chars')
            self.assertEqual(4, len(bsv.tui), 'TUI Abbreviations are 4 chars')
            self.assertTrue(bsv.tui.startswith('T'), 'Type TUI expected')
            self.assertIsNotNone(bsv.tui_label, 'TUI label should not be none')

        self.assertEqual(127, len(bsv_list), 'UMLS has 127 semantic types')
        self.assertEqual(127, len(set(bsv_list)), 'UMLS has 127 unique TUI')


if __name__ == '__main__':
    unittest.main()
