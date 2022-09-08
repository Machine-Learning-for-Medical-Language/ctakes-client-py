import logging
import os
import json
import unittest
import ctakes
from tests.test_resources import PathResource, LoadResource

def pretty(result: dict):
    print(json.dumps(result, indent=4))

class TestCtakesClient(unittest.TestCase):

    def test_covid_symptoms_medical_synonyms(self):
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
            found = ctakes.client.extract(symptom).list_match_text()
            if symptom in found:
                actual.append(symptom)

        diff = set(expected.keys()).difference(set(actual))

        self.assertEqual(set(), diff, 'diff should be empty, missing')

    def test_covid_symptoms_exist_in_response(self):
        """
        Symptoms of COVID-19
        https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html
        """
        for bsv in LoadResource.covid_symptoms.value:
            ner = ctakes.client.extract(bsv.text)

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

    def test_physician_note(self):
        physician_note = LoadResource.physician_note_text.value
        expected = LoadResource.physician_note_json.value

        actual1 = ctakes.client.extract(physician_note).as_json()
        actual2 = ctakes.client.extract(physician_note).as_json()

        unittest.TestCase.maxDiff = None

        self.assertDictEqual(expected, actual1, 'JSON did not match round trip serialization')
        self.assertDictEqual(actual1, actual2, 'calling service twice produces same results')


if __name__ == '__main__':
    unittest.main()




