"""Tests based on covid symptoms"""
from enum import Enum
import json
import unittest
import ctakesclient


def pretty(result: dict):
    print(json.dumps(result, indent=4))

class Symptom(Enum):
    # pylint: disable=invalid-name
    Cough = ['R05.9', '786.2', 'Post-tussive', 'tussive', 'Coughing']
    Fever = ['R50.9', '780.60', 'Fevers', 'Chills']
    Diarrhea = ['R19.7', '787.91', 'Watery stool']
    Fatigue = ['R53.81', '780.79', 'Fatigued']
    Nausea = ['R11.0', 'Nauseated', 'nauseous']
    Congestion = ['R09.81', 'runny nose', 'nasal congestion']
    SoreThroat = ['M79.1', 'Pharyngitis']
    Headache = ['R51.9', 'R51', 'Headache', 'Headaches', 'HA']
    Dyspnea = ['R06.0', 'SOB', 'Short of Breath']
    Aches = ['Myalgias', 'Muscle Aches']
    Anosmia = ['R43', 'R43.0', 'Loss of smell', 'loss of taste']

class TestCtakesClient(unittest.TestCase):
    """Test case for ctakes client extracting covid symptoms"""

    def test_covid_symptoms_medical_synonyms(self):
        """
        Test if COVID19 symptom synonyms are mapped in the BSV dictionary.
        """
        expected = []
        missed_icd = []
        actual = []
        for symptom in Symptom:
            for synonym in symptom.value:

                text = f'Chief Complaint: {synonym}'
                found = ctakesclient.client.extract(text).list_match_text()
                found = [hit.title() for hit in found]

                if synonym.title() in found:
                    expected.append(synonym.title())
                    actual.append(synonym.title())
                # elif 3 > len(synonym):
                #     warn.append(synonym)
                elif '.' in synonym:
                    missed_icd.append(synonym)
                else:
                    expected.append(synonym.title())

        diff = set(expected).difference(set(actual))

        # print(warn)

        self.assertEqual(set(), diff, 'diff should be empty, missing')

    def test_covid_symptoms_exist_in_response(self):
        """
        Symptoms of COVID-19
        https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html

        Test if every COVID symptom is found in server dictionary.
        https://github.com/Machine-Learning-for-Medical-Language/ctakes-client-py/blob/main/ctakesclient/resources/covid_symptoms.bsv
        -->
        https://github.com/Machine-Learning-for-Medical-Language/ctakes-covid-container/blob/main/covid.bsv
        """
        for bsv in ctakesclient.filesystem.covid_symptoms():
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
