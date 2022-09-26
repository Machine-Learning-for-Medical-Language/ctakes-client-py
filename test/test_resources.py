"""Resource helpers for use in tests"""

import os
from enum import Enum
import unittest
from ctakesclient import filesystem

def path(filename):
    """
    :param filename: basename of file like 'covid_symptoms.bsv'
    :return: path to file
    """
    return os.path.join(os.path.dirname(__file__), 'resources', filename)

def list_files(basedir):
    """
    :param basedir: folder like "resources", "curated", or "synthetic"
    :return:
    """
    return [os.path.join(basedir, filename) for filename in os.listdir(basedir)]

def curated():
    """
    *** NOT PHI NOT REAL PATIENTS**
    :return: curated directory containing 2363 "stories" about typical patient vists.
    """
    return os.path.join(os.path.dirname(__file__), 'resources', 'curated')

def synthetic():
    """
    *** NOT PHI NOT REAL PATIENTS**
    :return: Synthea (AI generative process) physican note examples
    """
    return os.path.join(os.path.dirname(__file__), 'resources', 'synthetic')

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
    COVID_SYMPTOMS = path('covid_symptoms.bsv')
    PHYSICIAN_NOTE_TEXT = path('test_physician_note.txt')
    PHYSICIAN_NOTE_JSON = path('test_physician_note.json')
    TEST_NEGATION = path('test_negation_hard.txt')
    SEMANTIC_GROUPS = path('SemGroups_2018.bsv')


class LoadResource(Enum):
    COVID_SYMPTOMS = load(PathResource.COVID_SYMPTOMS.value)
    PHYSICIAN_NOTE_TEXT = load(PathResource.PHYSICIAN_NOTE_TEXT.value)
    PHYSICIAN_NOTE_JSON = load(PathResource.PHYSICIAN_NOTE_JSON.value)
    TEST_NEGATION = load(PathResource.TEST_NEGATION.value)
    SEMANTIC_GROUPS = load(PathResource.SEMANTIC_GROUPS.value)


class TestResourceValidity(unittest.TestCase):
    """Test case for sanity checking resources"""

    def assertExists(self, resource_file):
        self.assertTrue(os.path.exists(resource_file),
                        f'resource did not exist: {resource_file}')

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
