import os
import unittest
from ctakes import bsv_reader

COVID_SYMPTOMS_BSV = os.path.join(os.getcwd(), '../resources/covid_symptoms.bsv')
TEST_PHYSICIAN_NOTE_TXT = os.path.join(os.getcwd(), '../resources/test_physician_note.txt')
TEST_PHYSICIAN_NOTE_JSON = os.path.join(os.getcwd(), '../resources/test_physician_note.json')

def load(filename):
    if str(filename).endswith('.json'):
        return bsv_reader.read_json(filename)
    elif str(filename).endswith('.txt'):
        return bsv_reader.read_text(filename)
    elif str(filename).endswith('.bsv'):
        return bsv_reader.list_bsv(filename)

class TestResources(unittest.TestCase):

    def assertExists(self, resource_file=COVID_SYMPTOMS_BSV):
        self.assertTrue(os.path.exists(resource_file), f'resource did not exist: {resource_file}')

    def test_resource_exists(self):
        self.assertExists(COVID_SYMPTOMS_BSV)
        self.assertExists(TEST_PHYSICIAN_NOTE_TXT)
        self.assertExists(TEST_PHYSICIAN_NOTE_JSON)

    def test_resource_load(self):
        self.assertIsNotNone(load(COVID_SYMPTOMS_BSV))
        self.assertIsNotNone(load(TEST_PHYSICIAN_NOTE_TXT))
        self.assertIsNotNone(load(TEST_PHYSICIAN_NOTE_JSON))


if __name__ == '__main__':
    unittest.main()
