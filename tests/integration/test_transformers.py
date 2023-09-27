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


async def list_false_positive_ss(physician_note: str, **kwargs) -> List[str]:
    """
    :param physician_note: note containing negated entries.
    :return: strings of symptoms that were actually marked *Polarity.pos*
    """
    ner = await ctakesclient.client.extract(physician_note)
    symptoms = ner.list_sign_symptom()
    spans = ner.list_spans(symptoms)
    polarities_cnlp = await ctakesclient.transformer.list_polarity(sentence=physician_note, spans=spans, **kwargs)

    fp = []

    for index in range(0, len(symptoms)):
        polarity = polarities_cnlp[index]

        if polarity != Polarity.neg:
            fp.append(symptoms[index].text)
            # print(f'symptoms={symptoms}, polarities={polarities_cnlp}, '
            #       f'text={note}')
    return fp


async def debug_helper(physician_note: str, **kwargs):
    print("##################################################################")
    print(physician_note)

    ner = await ctakesclient.client.extract(physician_note)

    matches = ner.list_match()
    spans = ner.list_spans(matches)

    for match in matches:
        print(f"{match.polarity.name}\t{match.span()}\t{match.text}\t\t" f"{match.type.value}")

    polarities_cnlp = await ctakesclient.transformer.list_polarity(physician_note, spans, **kwargs)
    polarities_ctakes = ner.list_polarity(spans)

    print("##################################################################")
    print("cNLP=")
    print(polarities_cnlp)

    print("##################################################################")
    print("cTAKES=")
    print(polarities_ctakes)


class TestNegationTransformer(unittest.IsolatedAsyncioTestCase):
    """Test case for the machine learning negation API"""

    model = ctakesclient.transformer.TransformerModel.NEGATION
    url = None

    def test_negation_api_example(self):
        """
        Test negation using the example provided by upstream.
        (the author of the server library, Tim Miller, PhD)
        """
        self.assertPolarityCompatible(note_negation_api_example())

    async def test_negated_denies(self):
        """
        Test simple 'patient denies' type statements.
        """
        false_positives = await list_false_positive_ss(note_negated_denies(), url=self.url, model=self.model)
        self.assertEqual([], false_positives)

    # pylint: disable-next=line-too-long
    @unittest.skip("https://github.com/Machine-Learning-for-Medical-Language/ctakes-client-py/issues/8")
    async def test_negated_review_of_symptoms(self):
        """
        Test hard ROS section of a medical note.
        This is not yet 100% accurate and will take consider time to be perfect.
        Negation is not a solved problem in NLP community.
        """
        false_positives = await list_false_positive_ss(
            note_negated_ros_review_of_symptoms(), url=self.url, model=self.model
        )
        self.assertEqual([], false_positives)

    async def assertPolarityCompatible(self, text: str):
        ner = await ctakesclient.client.extract(text)
        symptoms = ner.list_sign_symptom()
        polarities_ctakes = ner.list_polarity(symptoms)
        polarities_cnlp = await ctakesclient.transformer.list_polarity(
            text, ner.list_spans(symptoms), url=self.url, model=self.model
        )

        self.assertEqual(polarities_ctakes, polarities_cnlp, text)


class TestTermExistsTransformer(TestNegationTransformer):
    """Test case for the machine learning term exists API"""

    model = ctakesclient.transformer.TransformerModel.TERM_EXISTS
    url = "http://localhost:8001/termexists/process"  # url assumed by our integration tests


if __name__ == "__main__":
    unittest.main()
