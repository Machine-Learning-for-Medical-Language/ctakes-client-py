import os
import unittest

COVID_SYMPTOMS_BSV = os.path.join(os.getcwd(), '../resources/covid_symptoms.bsv')

class TestResources(unittest.TestCase):

    def test_exists_resource_file(self, resource_file=COVID_SYMPTOMS_BSV):
        self.assertTrue(os.path.exists(resource_file), f'resource did not exist: {resource_file}')