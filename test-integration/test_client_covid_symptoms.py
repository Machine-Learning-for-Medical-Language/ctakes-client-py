"""Tests based on covid symptoms"""

import json
import unittest
import ctakesclient
from test.test_resources import LoadResource


def pretty(result: dict):
    print(json.dumps(result, indent=4))


# pylint: disable-next=line-too-long
@unittest.skip('https://github.com/Machine-Learning-for-Medical-Language/ctakes-client-py/issues/7')
class TestCtakesClient(unittest.TestCase):
    """Test case for ctakes client extracting covid symptoms"""

    def test_covid_symptoms_medical_synonyms(self):
        """
        Test if COVID19 symptom synonyms are mapped in the BSV dictionary.
        https://github.com/Machine-Learning-for-Medical-Language/ctakes-covid-container/blob/main/covid.bsv
        """
        expected = {
            'SOB': 'Shortness Of Breath',
            'HA': 'Headache',
            'Myalgias': 'Muscle aches and pain',
            'Chills': 'Fever or chills',
            'Post-tussive': 'after Coughing',
            'tussive': 'related to Coughing',
            'Pharyngitis': 'sore throat',
            'Odynophagia': 'sore throat',
            'Loss of taste': 'Anosmia',
            'Loss of smell': 'Anosmia',
            'Tired': 'Fatigue',
        }

        actual = []
        for symptom in expected:
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
        https://github.com/Machine-Learning-for-Medical-Language/ctakes-client-py/blob/main/test/resources/covid_symptoms.bsv
        -->
        https://github.com/Machine-Learning-for-Medical-Language/ctakes-covid-container/blob/main/covid.bsv
        """
        for bsv in LoadResource.COVID_SYMPTOMS.value:
            ner = ctakesclient.client.extract(bsv.text)

            cui_list = []
            text_list = []

            for match in ner.list_sign_symptom():
                text_list.append(match.text)
                for concept in match.conceptAttributes:
                    cui_list.append(concept.cui)

            self.assertIn(bsv.text, text_list)
            self.assertIn(bsv.cui, cui_list)


if __name__ == '__main__':
    unittest.main()
