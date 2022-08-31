import unittest

from ctakes import bsv_reader
from tests import test_resources

class TestCovidSymptomsBSV(unittest.TestCase):
    def test_covid_symptoms(self):
        """
        Symptoms of COVID-19
        https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html
        """
        for bsv in bsv_reader.list_bsv(test_resources.COVID_SYMPTOMS_BSV):
            self.assertTrue(bsv.cui.startswith('C'), 'Concept CUI expected')
            self.assertTrue(bsv.tui.startswith('T'), 'Type TUI expected')
            self.assertEqual(bsv.vocab, 'SNOMEDCT_US', 'clinical terms vocab expected')
            self.assertIsNotNone(bsv.text)
            self.assertIsNotNone(bsv.pref)


if __name__ == '__main__':
    unittest.main()
