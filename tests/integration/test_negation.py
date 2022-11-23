"""Tests for basic negation"""

import json
import unittest
import ctakesclient
from ctakesclient.typesystem import Polarity
from tests.test_resources import LoadResource


def note_negated_ros_review_of_symptoms() -> str:
    return LoadResource.TEST_NEGATION.value


def note_negated_denies() -> str:
    return 'Denies any fevers or chills, sore throat, anosmia, cough.'


def note_positive_headache() -> str:
    return ('Presents for a 5-day history of headache,sore throat, fever '
            'up to 100.5,cough,anosmia, dysgeusia.')


def note_negation_api_example() -> str:
    """
    https://github.com/Machine-Learning-for-Medical-Language/cnlp_transformers#negation-api
    """
    return ('The patient has a sore knee and headache but denies nausea '
            'and has no anosmia.')


def pretty(result: dict) -> str:
    return json.dumps(result, indent=4)


class TestNegationCtakesDefaultContext(unittest.TestCase):
    """
    https://cwiki.apache.org/confluence/display/CTAKES/cTAKES+3.0+-+NE+Contexts
    """

    def test_ctakes_covid_symptoms(self):
        ner = ctakesclient.client.extract(note_negated_ros_review_of_symptoms())

        symptoms_dict = ctakesclient.filesystem.covid_symptoms()
        symptoms_fp = []

        for match in ner.list_match(Polarity.pos):
            for concept in match.conceptAttributes:
                if concept.cui in symptoms_dict:
                    symptoms_fp.append(match)

        self.assertEqual([], symptoms_fp,
                         ('false positives found in purely NEGATED physician '
                          f'note review of systems {symptoms_fp}'))

    # pylint: disable-next=line-too-long
    @unittest.skip('https://github.com/Machine-Learning-for-Medical-Language/ctakes-client-py/issues/8')
    def test_patient_denies(self):
        """
        Test everything in this example note is negated.
        Unfortunately ctakes negation algorithm is not perfect.
        See linked issue above.
        """
        text = note_negated_denies()
        ner = ctakesclient.client.extract(text)
        false_positives = ner.list_match_text(Polarity.pos)
        self.assertEqual([], false_positives)

    def test_history_of_headache(self):
        text = note_positive_headache()
        ner = ctakesclient.client.extract(text)
        self.assertIn('headache', ner.list_match_text())


if __name__ == '__main__':
    unittest.main()
