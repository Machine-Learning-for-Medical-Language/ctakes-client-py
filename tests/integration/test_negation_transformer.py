"""Tests for the machine learning negation API"""

import unittest
from typing import List
import ctakesclient
from ctakesclient.typesystem import Polarity
from .test_negation import (
    note_negated_denies,
    note_negated_ros_review_of_symptoms,
    note_negation_api_example,
)


def list_false_positive_ss(physician_note: str) -> List[str]:
    """
    :param physician_note: note containing negated entries.
    :return: strings of symptoms that were actually marked *Polarity.pos*
    """
    ner = ctakesclient.client.extract(physician_note)
    symptoms = ner.list_sign_symptom()
    spans = ner.list_spans(symptoms)
    polarities_cnlp = ctakesclient.transformer.list_polarity(
        sentence=physician_note, spans=spans)

    fp = []

    for index in range(0, len(symptoms)):
        polarity = polarities_cnlp[index]

        if polarity != Polarity.neg:
            fp.append(symptoms[index].text)
            # print(f'symptoms={symptoms}, polarities={polarities_cnlp}, '
            #       f'text={note}')
    return fp


def debug_helper(physician_note: str):
    print('##################################################################')
    print(physician_note)

    ner = ctakesclient.client.extract(physician_note)

    matches = ner.list_match()
    spans = ner.list_spans(matches)

    for match in matches:
        print(f'{match.polarity.name}\t{match.span()}\t{match.text}\t\t'
              f'{match.type.value}')

    polarities_cnlp = ctakesclient.transformer.list_polarity(
        physician_note, spans)
    polarities_ctakes = ner.list_polarity(spans)

    print('##################################################################')
    print('cNLP=')
    print(polarities_cnlp)

    print('##################################################################')
    print('cTAKES=')
    print(polarities_ctakes)


class TestNegationTransformer(unittest.TestCase):
    """Test case for the machine learning negation API"""

    def test_negation_api_example(self):
        """
        Test negation using the example provided by upstream.
        (the author of the server library, Tim Miller, PhD)
        """
        self.assertPolarityCompatible(note_negation_api_example())

    def test_negated_denies(self):
        """
        Test simple 'patient denies' type statements.
        """
        self.assertEqual([], list_false_positive_ss(note_negated_denies()))

    # pylint: disable-next=line-too-long
    @unittest.skip('https://github.com/Machine-Learning-for-Medical-Language/ctakes-client-py/issues/8')
    def test_negated_review_of_symptoms(self):
        """
        Test hard ROS section of a medical note.
        This is not yet 100% accurate and will take consider time to be perfect.
        Negation is not a solved problem in NLP community.
        """
        self.assertEqual([], list_false_positive_ss(
            note_negated_ros_review_of_symptoms()))

    def assertPolarityCompatible(self, text: str):
        ner = ctakesclient.client.extract(text)
        symptoms = ner.list_sign_symptom()
        polarities_ctakes = ner.list_polarity(symptoms)
        polarities_cnlp = ctakesclient.transformer.list_polarity(
            text, ner.list_spans(symptoms))

        self.assertEqual(polarities_ctakes, polarities_cnlp, text)


if __name__ == '__main__':
    unittest.main()
