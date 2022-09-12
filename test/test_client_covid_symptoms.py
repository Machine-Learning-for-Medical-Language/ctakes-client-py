import logging
import os
import json
import unittest
import ctakesclient
from tests.test_resources import PathResource, LoadResource

def pretty(result: dict):
    print(json.dumps(result, indent=4))

@unittest.skip("https://github.com/comorbidity/ctakes-client-python/issues/6")
class TestCtakesClient(unittest.TestCase):

    def test_covid_symptoms_medical_synonyms(self):
        """
        Test if COVID19 symptom synonyms are mapped in the BSV dictionary.
        https://github.com/Machine-Learning-for-Medical-Language/ctakes-covid-container/blob/main/covid.bsv
        """
        expected = {'SOB': 'Shortness Of Breath',
                    'HA': 'Headache',
                    'Myalgias': 'Muscle aches and pain',
                    'Chills': 'Fever or chills',
                    'Post-tussive': 'after Coughing',
                    'tussive':'related to Coughing',
                    'Pharyngitis':'sore throat',
                    'Odynophagia': 'sore throat',
                    'Loss of taste': 'Anosmia',
                    'Loss of smell': 'Anosmia',
                    'Tired': 'Fatigue',
                    }

        actual = list()
        for symptom in expected.keys():
            found = ctakesclient.client.extract(symptom).list_match_text()
            if symptom in found:
                actual.append(symptom)

        diff = set(expected.keys()).difference(set(actual))

        self.assertEqual(set(), diff, 'diff should be empty, missing')

    def test_covid_symptoms_exist_in_response(self):
        """
        Symptoms of COVID-19
        https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html

        Test if every COVID symptom is found in server dictionary.
        https://github.com/comorbidity/ctakes-client-python/blob/main/resources/covid_symptoms.bsv -->
        https://github.com/Machine-Learning-for-Medical-Language/ctakes-covid-container/blob/main/covid.bsv
        """
        for bsv in LoadResource.covid_symptoms.value:
            ner = ctakesclient.client.extract(bsv.text)

            cui_list = list()
            text_list = list()

            for match in ner.list_sign_symptom():
                text_list.append(match.text)
                for concept in match.conceptAttributes:
                    cui_list.append(concept.cui)

            if bsv.text not in text_list:
                err = f'{bsv.cui}\t\t ** cui NOT found in {set(cui_list)} ** \t{str(bsv)}'
                logging.error(err)

                self.assertTrue(bsv.text in text_list, err)

            if bsv.cui not in cui_list:
                err = f'{bsv.cui}\t\t ** cui NOT found in {set(cui_list)} ** \t{str(bsv)}'
                logging.error(err)

                self.assertTrue(bsv.cui in cui_list, err)

if __name__ == '__main__':
    unittest.main()




