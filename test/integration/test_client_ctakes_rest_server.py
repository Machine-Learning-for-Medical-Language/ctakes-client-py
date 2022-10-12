"""Tests for the cTAKES REST API"""

import unittest
import ctakesclient
from test.test_resources import LoadResource


class TestClientCtakesRestServer(unittest.TestCase):
    """Test case for REST requests"""

    def test_physician_note(self):
        """
        Test calling REST server returns JSON that matches expected.
        Strong typing (Polarity, MatchText, UmlsConcept) enforced during
        serialization.
        """
        physician_note = LoadResource.PHYSICIAN_NOTE_TEXT.value
        expected = LoadResource.PHYSICIAN_NOTE_JSON.value

        actual1 = ctakesclient.client.extract(physician_note).as_json()
        actual2 = ctakesclient.client.extract(physician_note).as_json()

        unittest.TestCase.maxDiff = None

        self.assertDictEqual(expected, actual1,
                             'JSON did not match round trip serialization')
        self.assertDictEqual(actual1, actual2,
                             'calling service twice produces same results')

    def test_unicode(self):
        """Ensure that we handle utf8/unicode correctly"""
        # First, make sure we don't blow up just by sending it
        ner = ctakesclient.client.extract('patient feels 🤒 with fever')

        # Then confirm that our spans are correct (0-based and character-based)
        self.assertEqual(1, len(ner.list_sign_symptom()))
        symptom = ner.list_sign_symptom()[0]
        self.assertEqual('fever', symptom.text)
        self.assertEqual(21, symptom.begin)
        self.assertEqual(26, symptom.end)


if __name__ == '__main__':
    unittest.main()
