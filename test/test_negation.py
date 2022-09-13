from typing import List
import logging
import json
import unittest
import ctakesclient
from ctakesclient.typesystem import Polarity
from tests.test_resources import PathResource, LoadResource

def covid_symptoms() -> dict:
    return ctakesclient.filesystem.map_cui_pref(PathResource.covid_symptoms.value)

def note_negated_ros_review_of_symptoms() -> str:
    return LoadResource.test_negation.value

def note_negated_denies() -> str:
    return 'Denies any fevers or chills, sore throat, anosmia, cough.'

def note_positive_headache() ->str:
    return 'Presents for a 5-day history of headache,sore throat, fever up to 100.5,cough,anosmia, dysgeusia.'

def note_negation_api_example() -> str:
    """
    https://github.com/Machine-Learning-for-Medical-Language/cnlp_transformers#negation-api
    """
    return 'The patient has a sore knee and headache but denies nausea and has no anosmia.'

def pretty(result: dict) -> str:
    return json.dumps(result, indent=4)

class TestNegationCtakesDefaultContext(unittest.TestCase):
    """
    https://cwiki.apache.org/confluence/display/CTAKES/cTAKES+3.0+-+NE+Contexts
    """
    def test_ctakes_covid_symptoms(self):
        ner = ctakesclient.client.extract(note_negated_ros_review_of_symptoms())

        symptoms_dict = covid_symptoms()
        positive_list = ner.list_concept(Polarity.pos)

        for unexpected in positive_list:
            msg = json.dumps(unexpected.as_json(), indent=4)
            msg = f'########## \t Found positive match: {msg}'
            logging.warning(msg)

            if unexpected.cui in symptoms_dict.keys():
                logging.error(msg)

    def test_patient_denies(self):
        text = note_negated_denies()

        false_positives = ctakesclient.client.extract(text).list_match_text()
        self.assertEqual(list(), false_positives)

    def test_history_of_headache(self):
        text = note_positive_headache()
        self.assertTrue('headache' in ctakesclient.client.extract(text).list_match_text())


if __name__ == '__main__':
    unittest.main()
