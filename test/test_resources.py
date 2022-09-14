import os
from enum import Enum
import unittest
from ctakesclient import filesystem

def path(filename):
    return os.path.join(os.path.dirname(__file__), 'resources', filename)

def load(filepath):
    if str(filepath).endswith('.json'):
        return filesystem.read_json(filepath)
    elif str(filepath).endswith('.txt'):
        return filesystem.read_text(filepath)
    if str(filepath).endswith('.bsv'):
        if 'SemGroups' in filepath:
            return filesystem.list_bsv_semantics(filepath)
        else:
            return filesystem.list_bsv_concept(filepath)


class PathResource(Enum):
    covid_symptoms = path('covid_symptoms.bsv')
    physician_note_text = path('test_physician_note.txt')
    physician_note_json = path('test_physician_note.json')
    test_negation = path('test_negation_hard.txt')
    semantic_groups = path('SemGroups_2018.bsv')

class LoadResource(Enum):
    covid_symptoms = load(PathResource.covid_symptoms.value)
    physician_note_text = load(PathResource.physician_note_text.value)
    physician_note_json = load(PathResource.physician_note_json.value)
    test_negation = load(PathResource.test_negation.value)
    semantic_groups = load(PathResource.semantic_groups.value)

class TestResourceValidity(unittest.TestCase):

    def assertExists(self, resource_file):
        self.assertTrue(os.path.exists(resource_file), f'resource did not exist: {resource_file}')

    def test_resource_exists(self):
        for res in PathResource:
            self.assertExists(res.value)

    def test_resource_load(self):
        for loader in LoadResource:
            # print(loader.value)
            self.assertIsNotNone(loader.value)
            self.assertTrue(len(loader.value) > 0)


if __name__ == '__main__':
    unittest.main()
