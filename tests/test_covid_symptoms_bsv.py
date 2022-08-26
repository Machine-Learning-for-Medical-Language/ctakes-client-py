import os
import logging
import unittest

from ctakes import ctakes_client
from ctakes import bsv_reader

COVID_SYMPTOMS_BSV = os.path.join(os.getcwd(), '../resources/covid_symptoms.bsv')

class TestCovidSymptomsBSV(unittest.TestCase):
    """
    Symptoms of COVID-19
    https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html
    """
    def test_covid_symptoms_exist_in_response(self):

        for bsv in bsv_reader.list_bsv(COVID_SYMPTOMS_BSV):

            cuis = ctakes_client.process(bsv.text).list_concept_cui()

            self.assertTrue(bsv.code in cuis, f'{bsv.__dict__} not found in response')


if __name__ == '__main__':
    unittest.main()
