"""Resource helpers for use in tests"""

import os
from enum import Enum
import unittest
from ctakesclient import filesystem


def path(filename) -> str:
    return os.path.join(os.path.dirname(__file__), "resources", filename)


def load(filepath):
    if str(filepath).endswith(".json"):
        return filesystem.read_json(filepath)
    elif str(filepath).endswith(".txt"):
        return filesystem.read_text(filepath)


class PathResource(Enum):
    CONCEPTS_BSV = path("concepts.bsv")
    PHYSICIAN_NOTE_TEXT = path("test_physician_note.txt")
    PHYSICIAN_NOTE_JSON = path("test_physician_note.json")
    SEMANTICS_BSV = path("semantics.bsv")
    SYNTHETIC_JSON = path("synthetic.json")
    TEST_NEGATION = path("test_negation_hard.txt")


class LoadResource(Enum):
    PHYSICIAN_NOTE_TEXT = load(PathResource.PHYSICIAN_NOTE_TEXT.value)
    PHYSICIAN_NOTE_JSON = load(PathResource.PHYSICIAN_NOTE_JSON.value)
    SYNTHETIC_JSON = load(PathResource.SYNTHETIC_JSON.value)
    TEST_NEGATION = load(PathResource.TEST_NEGATION.value)


class TestResourceValidity(unittest.TestCase):
    """Test case for sanity checking resources"""

    def assertExists(self, resource_file):
        self.assertTrue(os.path.exists(resource_file), f"resource did not exist: {resource_file}")

    def test_resource_exists(self):
        for res in PathResource:
            self.assertExists(res.value)

    def test_resource_load(self):
        for loader in LoadResource:
            # print(loader.value)
            self.assertIsNotNone(loader.value)
            self.assertTrue(len(loader.value) > 0)


if __name__ == "__main__":
    unittest.main()
