"""Tests for text2fhir.py"""

import unittest

import ctakesclient
from ctakesclient import text2fhir
from ctakesclient.typesystem import CtakesJSON, MatchText, Polarity

from tests.test_resources import LoadResource


def expected_nlp_source() -> dict:
    ver = ctakesclient.__version__
    url = f"https://github.com/Machine-Learning-for-Medical-Language/ctakes-client-py/releases/tag/v{ver}"

    return {
        "url": "http://fhir-registry.smarthealthit.org/StructureDefinition/nlp-source",
        "extension": [
            {"url": "algorithm", "valueString": "ctakesclient"},
            {"url": "version", "valueString": f"{url}"},
        ],
    }


###############################################################################
#
# Unit Test : assertions and lightweight checking reading/printing FHIR types
#
###############################################################################


class TestText2Fhir(unittest.TestCase):
    """
    Test Transformation from NLP results  to FHIR resources.
    Test serialization to/from JSON of the different types (NLP and FHIR).
    """

    def setUp(self):
        super().setUp()
        self.ctakes = CtakesJSON(LoadResource.SYNTHETIC_JSON.value)
        self.maxDiff = None  # For debugging. pylint: disable=invalid-name

    def test_nlp_source(self):
        expected = expected_nlp_source()
        actual = text2fhir._nlp_source()  # pylint: disable=protected-access
        # common.print_json(actual)
        self.assertDictEqual(expected, actual.as_json())

    def test_nlp_derivation_reference(self):
        actual = text2fhir._nlp_derivation(docref_id="ABCD", offset=20, length=5)  # pylint: disable=protected-access
        # common.print_json(actual)
        self.assertDictEqual(
            {
                "url": "http://hl7.org/fhir/StructureDefinition/derivation-reference",
                "extension": [
                    {"url": "reference", "valueReference": {"reference": "DocumentReference/ABCD"}},
                    {"url": "offset", "valueInteger": 20},
                    {"url": "length", "valueInteger": 5},
                ],
            },
            actual.as_json(),
        )

    def test_nlp_concept(self):
        """
        Test construction of FHIR CodeableConcept
        """
        match = self.ctakes.list_anatomical_site(Polarity.pos)[0]
        bodysite = text2fhir.nlp_concept(match).as_json()

        self.assertDictEqual(
            {
                "coding": [
                    {
                        "code": "8205005",
                        "system": "http://snomed.info/sct",
                    },
                    {
                        "code": "C0043262",
                        "system": "http://terminology.hl7.org/CodeSystem/umls",
                    },
                ],
                "text": "wrist",
            },
            bodysite,
        )

    def test_nlp_concept_unknown_vocab(self):
        """
        Confirm we gracefully handle unknown vocabularies
        """
        match = MatchText(
            {
                "conceptAttributes": [
                    {
                        "code": "foobar",
                        "codingScheme": "custom",
                        "cui": "C0043262",
                    }
                ],
                "polarity": 0,
                "text": "boo",
                "type": "AnatomicalSiteMention",
            }
        )
        concept = text2fhir.nlp_concept(match).as_json()

        self.assertDictEqual(
            {
                "coding": [
                    {
                        "code": "foobar",
                    },
                    {
                        "code": "C0043262",
                        "system": "http://terminology.hl7.org/CodeSystem/umls",
                    },
                ],
                "text": "boo",
            },
            concept,
        )

    def test_nlp_condition(self):
        """
        Test conversion from NLP to FHIR (DiseaseDisorder -> FHIR Condition).
        Test serialization to/from JSON.
        Does not text expected values.
        """
        match = self.ctakes.list_disease_disorder()[0]
        condition = text2fhir.nlp_condition("1234", "5678", "ABCD", match).as_json()
        del condition["id"]  # randomly generated id

        self.assertDictEqual(
            {
                "code": {
                    "coding": [
                        {
                            "code": "195662009",
                            "system": "http://snomed.info/sct",
                        },
                        {
                            "code": "C0396000",
                            "system": "http://terminology.hl7.org/CodeSystem/umls",
                        },
                    ],
                    "text": "acute viral pharyngitis",
                },
                "encounter": {
                    "reference": "Encounter/5678",
                },
                "extension": [
                    {
                        "extension": [
                            {"url": "reference", "valueReference": {"reference": "DocumentReference/ABCD"}},
                            {"url": "offset", "valueInteger": 152},
                            {"url": "length", "valueInteger": 23},
                        ],
                        "url": "http://hl7.org/fhir/StructureDefinition/derivation-reference",
                    },
                ],
                "modifierExtension": [
                    expected_nlp_source(),
                    {
                        "url": "http://fhir-registry.smarthealthit.org/StructureDefinition/nlp-polarity",
                        "valueBoolean": True,
                    },
                ],
                "resourceType": "Condition",
                "subject": {
                    "reference": "Patient/1234",
                },
                "verificationStatus": {
                    "coding": [
                        {
                            "code": "unconfirmed",
                            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        },
                    ],
                    "text": "Unconfirmed",
                },
            },
            condition,
        )

    def test_nlp_medication(self):
        """
        Test conversion from NLP to FHIR (MedicationMention -> FHIR MedicationStatement).
        Test serialization to/from JSON.
        Does not text expected values.
        """
        match = self.ctakes.list_medication()[0]
        medication = text2fhir.nlp_medication("1234", "5678", "ABCD", match).as_json()
        del medication["id"]  # randomly generated id

        self.assertDictEqual(
            {
                "context": {
                    "reference": "Encounter/5678",
                },
                "medicationCodeableConcept": {
                    "coding": [
                        {
                            "code": "66076007",
                            "system": "http://snomed.info/sct",
                        },
                        {
                            "code": "C0304290",
                            "system": "http://terminology.hl7.org/CodeSystem/umls",
                        },
                        {
                            "code": "91058",
                            "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        },
                        {
                            "code": "C0304290",
                            "system": "http://terminology.hl7.org/CodeSystem/umls",
                        },
                    ],
                    "text": "chewable tablet",
                },
                "extension": [
                    {
                        "extension": [
                            {"url": "reference", "valueReference": {"reference": "DocumentReference/ABCD"}},
                            {"url": "offset", "valueInteger": 442},
                            {"url": "length", "valueInteger": 15},
                        ],
                        "url": "http://hl7.org/fhir/StructureDefinition/derivation-reference",
                    },
                ],
                "modifierExtension": [
                    expected_nlp_source(),
                    {
                        "url": "http://fhir-registry.smarthealthit.org/StructureDefinition/nlp-polarity",
                        "valueBoolean": True,
                    },
                ],
                "resourceType": "MedicationStatement",
                "status": "unknown",
                "subject": {
                    "reference": "Patient/1234",
                },
            },
            medication,
        )

    def test_nlp_observation(self):
        """
        Test conversion from NLP to FHIR (SignSymptomMention -> FHIR Observation).
        Test serialization to/from JSON.
        Does not text expected values.
        """
        match = self.ctakes.list_sign_symptom()[0]
        symptom = text2fhir.nlp_observation("1234", "5678", "ABCD", match).as_json()
        del symptom["id"]  # randomly generated id

        self.assertDictEqual(
            {
                "code": {
                    "coding": [
                        {
                            "code": "33962009",
                            "system": "http://snomed.info/sct",
                        },
                        {
                            "code": "C0277786",
                            "system": "http://terminology.hl7.org/CodeSystem/umls",
                        },
                        {
                            "code": "409586006",
                            "system": "http://snomed.info/sct",
                        },
                        {
                            "code": "C0277786",
                            "system": "http://terminology.hl7.org/CodeSystem/umls",
                        },
                    ],
                    "text": "Complaint",
                },
                "encounter": {
                    "reference": "Encounter/5678",
                },
                "extension": [
                    {
                        "extension": [
                            {"url": "reference", "valueReference": {"reference": "DocumentReference/ABCD"}},
                            {"url": "offset", "valueInteger": 21},
                            {"url": "length", "valueInteger": 9},
                        ],
                        "url": "http://hl7.org/fhir/StructureDefinition/derivation-reference",
                    },
                ],
                "modifierExtension": [
                    expected_nlp_source(),
                    {
                        "url": "http://fhir-registry.smarthealthit.org/StructureDefinition/nlp-polarity",
                        "valueBoolean": False,
                    },
                ],
                "resourceType": "Observation",
                "status": "preliminary",
                "subject": {
                    "reference": "Patient/1234",
                },
            },
            symptom,
        )

    def test_nlp_procedure(self):
        """
        Test conversion from NLP to FHIR (Procedure -> FHIR Procedure).
        Test serialization to/from JSON.
        Does not text expected values.
        """
        match = self.ctakes.list_procedure()[0]
        procedure = text2fhir.nlp_procedure("1234", "5678", "ABCD", match).as_json()
        del procedure["id"]  # randomly generated id

        self.assertDictEqual(
            {
                "code": {
                    "coding": [
                        {
                            "code": "129265001",
                            "system": "http://snomed.info/sct",
                        },
                        {
                            "code": "C1261322",
                            "system": "http://terminology.hl7.org/CodeSystem/umls",
                        },
                        {
                            "code": "386053000",
                            "system": "http://snomed.info/sct",
                        },
                        {
                            "code": "C1261322",
                            "system": "http://terminology.hl7.org/CodeSystem/umls",
                        },
                    ],
                    "text": "Assessment",
                },
                "encounter": {
                    "reference": "Encounter/5678",
                },
                "extension": [
                    {
                        "extension": [
                            {"url": "reference", "valueReference": {"reference": "DocumentReference/ABCD"}},
                            {"url": "offset", "valueInteger": 461},
                            {"url": "length", "valueInteger": 10},
                        ],
                        "url": "http://hl7.org/fhir/StructureDefinition/derivation-reference",
                    },
                ],
                "modifierExtension": [
                    expected_nlp_source(),
                    {
                        "url": "http://fhir-registry.smarthealthit.org/StructureDefinition/nlp-polarity",
                        "valueBoolean": True,
                    },
                ],
                "resourceType": "Procedure",
                "status": "unknown",
                "subject": {
                    "reference": "Patient/1234",
                },
            },
            procedure,
        )

    def test_nlp_fhir(self):
        """
        Test conversion from NLP to FHIR (all types).
        """
        fhir = text2fhir.nlp_fhir("1234", "5678", "ABCD", self.ctakes)

        self.assertEqual(68, len(fhir))
        self.assertSetEqual(
            {
                "Condition",
                "MedicationStatement",
                "Observation",
                "Procedure",
            },
            {type(x).__name__ for x in fhir},
        )
