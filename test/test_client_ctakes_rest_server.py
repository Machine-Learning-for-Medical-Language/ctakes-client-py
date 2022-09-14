import logging
import json
import unittest
import ctakesclient
from test.test_resources import PathResource, LoadResource

class TestClientCtakesRestServer(unittest.TestCase):

    def test_physician_note(self):
        """
        Test calling REST server returns JSON that matches expected.
        Strong typing (Polarity, MatchText, UmlsConcept) enforced during serialization.
        """
        physician_note = LoadResource.physician_note_text.value
        expected = LoadResource.physician_note_json.value

        actual1 = ctakesclient.client.extract(physician_note).as_json()
        actual2 = ctakesclient.client.extract(physician_note).as_json()

        unittest.TestCase.maxDiff = None

        self.assertDictEqual(expected, actual1, 'JSON did not match round trip serialization')
        self.assertDictEqual(actual1, actual2, 'calling service twice produces same results')


if __name__ == '__main__':
    unittest.main()




