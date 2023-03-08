"""Transforms cTAKES output into FHIR resources"""

import uuid
from enum import Enum
from typing import List, Optional

from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.coding import Coding
from fhirclient.models.condition import Condition
from fhirclient.models.domainresource import DomainResource
from fhirclient.models.extension import Extension
from fhirclient.models.fhirreference import FHIRReference
from fhirclient.models.observation import Observation
from fhirclient.models.medicationstatement import MedicationStatement
from fhirclient.models.procedure import Procedure
from fhirclient.models.resource import Resource

import ctakesclient
from ctakesclient.typesystem import CtakesJSON, MatchText, Polarity, Span


###############################################################################
# URLs to qualify Extensions:
#   FHIR DerivationReference
#   SMART-on-FHIR StructureDefinition
###############################################################################
FHIR_DERIVATION_REF_URL = "http://hl7.org/fhir/StructureDefinition/derivation-reference"
NLP_SOURCE_URL = "http://fhir-registry.smarthealthit.org/StructureDefinition/nlp-source"
NLP_POLARITY_URL = "http://fhir-registry.smarthealthit.org/StructureDefinition/nlp-polarity"


class Vocab(Enum):
    """
    https://build.fhir.org/terminologies-systems.html
    """

    SNOMEDCT_US = "http://snomed.info/sct"
    RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"
    LOINC = "http://loinc.org"
    LNC = "http://loinc.org"
    CPT = "http://www.ama-assn.org/go/cpt"
    MEDRT = "http://va.gov/terminology/medrt"
    NDFRT = "http://hl7.org/fhir/ndfrt"
    NDC = "http://hl7.org/fhir/sid/ndc"
    CVX = "http://hl7.org/fhir/sid/cvx"
    ICD9 = "ICD-9"
    ICD10 = "ICD-10"
    UMLS = "http://terminology.hl7.org/CodeSystem/umls"


def _vocab_url(umls_sab: str) -> Optional[str]:
    """
    Returns the URL for the given UMLS vocabulary, or None if it's custom or not recognized

    See https://www.nlm.nih.gov/research/umls/sourcereleasedocs/index.html

    :param umls_sab: UMLS SAB = "Source Abbreviation"
    :return: URL of UMLS vocab
    """
    if not hasattr(Vocab, umls_sab):
        return None
    return str(Vocab[umls_sab].value)


###############################################################################
# Common extension helper methods
#
###############################################################################


def _value_string(url: str, value: str) -> Extension:
    """
    :param url: either URL or simple "key"
    :param value: valueString to associate with URL
    :return: Extension with simple url:valueString
    """
    return Extension({"url": url, "valueString": value})


def _value_integer(url: str, value: str) -> Extension:
    """
    :param url: either URL or simple "key"
    :param value: valueInteger to associate with URL
    :return: Extension with simple url:valueInteger
    """
    return Extension({"url": url, "valueInteger": value})


def _value_boolean(url: str, value: bool) -> Extension:
    """
    :param url: either URL or simple "key"
    :param value: valueString to associate with URL
    :return: Extension with simple url:valueBoolean
    """
    return Extension({"url": url, "valueBoolean": value})


def _value_reference(value: FHIRReference) -> Extension:
    """
    :param value: valueString to associate with URL
    :return: Extension with reference:FHIRReference like 'Patient/123456789'
    """
    return Extension({"url": "reference", "valueReference": value.as_json()})


def _value_list(url: str, values: List[Extension]) -> Extension:
    """
    :param url: either URL or simple "key"
    :param values: nested list of extensions
    :return: Extension with nested content extension:List
    """
    return Extension({"url": url, "extension": [v.as_json() for v in values]})


###############################################################################
# Standard FHIR References are ResourceType/id
###############################################################################


def _random_id() -> str:
    """
    Provides a random id for newly created resources

    Users may override these, but nice to give them something valid if they don't care.
    """
    return str(uuid.uuid4())


def _ref_resource(resource_type: str, resource_id: str) -> FHIRReference:
    """
    Reference the FHIR proper way
    :param resource_type: Name of resource, like "Patient"
    :param resource_id: ID for resource (isa REF can be UUID)
    :return: FHIRReference as Resource/$id
    """
    if not resource_id:
        raise ValueError("Missing resource ID")
    return FHIRReference({"reference": f"{resource_type}/{resource_id}"})


def _ref_subject(subject_id: str) -> FHIRReference:
    """
    Patient Reference the FHIR proper way
    :param subject_id: ID for patient (isa REF can be UUID)
    :return: FHIRReference as Patient/$id
    """
    return _ref_resource("Patient", subject_id)


def _ref_encounter(encounter_id: str) -> FHIRReference:
    """
    Encounter Reference the FHIR proper way
    :param encounter_id: ID for encounter (isa REF can be UUID)
    :return: FHIRReference as Encounter/$id
    """
    return _ref_resource("Encounter", encounter_id)


def _ref_document(docref_id: str) -> FHIRReference:
    """
    Encounter Reference the FHIR proper way
    :param docref_id: ID for encounter (isa REF can be UUID)
    :return: FHIRReference as Encounter/$id
    """
    return _ref_resource("DocumentReference", docref_id)


###############################################################################
# modifierExtension
#   "nlp-source" is Required
#   "nlp-polarity" is Optional
#
###############################################################################


def _nlp_modifier(source=None, polarity=None) -> List[Extension]:
    """
    :param source: default = "ctakesclient" with version tag.
    :param polarity: pos= concept is true, neg=concept is negated ("patient denies cough")
    :return: FHIR resource.modifierExtension
    """
    if source is None:
        source = _nlp_source()

    if polarity is None:
        return [source]
    else:
        return [source, _nlp_polarity(polarity)]


def _nlp_source(algorithm=None, version=None) -> Extension:
    """
    :param algorithm: optional, default = "ctakesclient".
    :param version: optional, default = "ctakesclient" version.
    """
    values = [_nlp_algorithm(algorithm), _nlp_version(version)]
    return _value_list(NLP_SOURCE_URL, values)


def _nlp_algorithm(algorithm=None) -> Extension:
    """
    :param algorithm: optional, default = "ctakesclient".
    """
    if not algorithm:
        algorithm = ctakesclient.__package__

    return _value_string("algorithm", algorithm)


def _nlp_version(version=None) -> Extension:
    """
    :param version: optional, default = "ctakesclient" version.
    """
    if version is None:
        release = ctakesclient.__version__
        version = f"https://github.com/Machine-Learning-for-Medical-Language/ctakes-client-py/releases/tag/v{release}"

    return _value_string("version", version)


def _nlp_polarity(polarity: Polarity) -> Extension:
    """
    :param polarity: pos= concept is true, neg=concept is negated ("patient denies cough")
    """
    positive = polarity == Polarity.pos
    return _value_boolean(NLP_POLARITY_URL, positive)


###############################################################################
#  DerivationReference
#
#   "reference" is Required
#   "offset" is Optional
#   "length" is Optional
#
###############################################################################


def _nlp_derivation_span(docref_id, span: Span) -> Extension:
    return _nlp_derivation(docref_id=docref_id, offset=span.begin, length=span.end - span.begin)


def _nlp_derivation(docref_id, offset=None, length=None) -> Extension:
    """
    README: http://build.fhir.org/extension-derivation-reference.html

    :param docref_id: ID for the DocumentReference from which NLP resource was derived.
    :param offset: optional character *offset in document* (integer!)
    :param length: optional character *length from offset* of the matching text span.
    :return: Extension for DerivationReference defining which document and text position was derived using NLP
    """
    values = [_value_reference(_ref_document(docref_id))]

    if offset:
        values.append(_value_integer("offset", offset))

    if length:
        values.append(_value_integer("length", length))

    values = [v.as_json() for v in values]

    return Extension({"url": FHIR_DERIVATION_REF_URL, "extension": values})


def _nlp_extensions(fhir_resource: Resource, docref_id: str, nlp_match: MatchText, source=None) -> None:
    """
    apply "extensions" and "modiferExtension" to provided $fhir_resource

    :param fhir_resource: passed by reference
    :param docref_id: ID for DocumentReference (isa REF can be UUID)
    :param nlp_match: response from cTAKES or other NLP Client
    :param source: NLP Version information, if none is provided use version of ctakesclient.
    """
    fhir_resource.modifierExtension = _nlp_modifier(source, nlp_match.polarity)
    fhir_resource.extension = [_nlp_derivation_span(docref_id, nlp_match.span())]


###############################################################################
#
# Individual NLP conversion functions for a single MatchText
#
###############################################################################


def nlp_concept(match: MatchText) -> CodeableConcept:
    """
    NLP match --> FHIR CodeableConcept

    :param match: everything needed to make CodeableConcept
    :return: FHIR CodeableConcept with both UMLS CUI and source vocab CODE
    """
    coded = []
    for concept in match.conceptAttributes:
        coded.append(Coding({"system": _vocab_url(concept.codingScheme), "code": concept.code}))
        coded.append(Coding({"system": Vocab.UMLS.value, "code": concept.cui}))

    return CodeableConcept({"text": match.text, "coding": [c.as_json() for c in coded]})


def nlp_condition(
    subject_id: str,
    encounter_id: str,
    docref_id: str,
    nlp_match: MatchText,
    source: Extension = None,
) -> Condition:
    """
    FHIR Condition from an NLP match (e.g. a disease disorder)

    Use this method to get FHIR resource for a note that is for a ** specific encounter **.
    Be advised that a single note can reference past medical history.

    :param subject_id: ID for patient (isa REF can be UUID)
    :param encounter_id: ID for visit (isa REF can be UUID)
    :param docref_id: ID for DocumentReference (isa REF can be UUID)
    :param nlp_match: response from cTAKES or other NLP Client
    :param source: NLP Version information, if none is provided use version of ctakesclient.
    :return: FHIR Condition (note it will have a random id)
    """
    condition = Condition()

    # id linkage
    condition.id = _random_id()
    condition.subject = _ref_subject(subject_id)
    condition.encounter = _ref_encounter(encounter_id)

    # status is unconfirmed - NLP is not perfect.
    status = Coding({"system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "unconfirmed"})
    condition.verificationStatus = CodeableConcept({"text": "Unconfirmed", "coding": [status.as_json()]})

    # NLP
    _nlp_extensions(condition, docref_id, nlp_match, source)
    condition.code = nlp_concept(nlp_match)

    return condition


def nlp_observation(
    subject_id: str,
    encounter_id: str,
    docref_id: str,
    nlp_match: MatchText,
    source: Extension = None,
) -> Observation:
    """
    FHIR Observation from an NLP match (e.g. a sign symptom)

    Use this method to get FHIR resource for a note that is for a ** specific encounter **.
    Be advised that a single note can reference past medical history.

    :param subject_id: ID for patient (isa REF can be UUID)
    :param encounter_id: ID for visit (isa REF can be UUID)
    :param nlp_match: response from cTAKES or other NLP Client
    :param source: NLP Version information, if none is provided use version of ctakesclient.
    :return: FHIR Observation (note it will have a random id)
    """
    observation = Observation()

    # id linkage
    observation.id = _random_id()
    observation.subject = _ref_subject(subject_id)
    observation.encounter = _ref_encounter(encounter_id)
    observation.status = "preliminary"

    # NLP
    _nlp_extensions(observation, docref_id, nlp_match, source)
    observation.code = nlp_concept(nlp_match)

    return observation


def nlp_medication(
    subject_id: str,
    encounter_id: str,
    docref_id: str,
    nlp_match: MatchText,
    source: Extension = None,
) -> MedicationStatement:
    """
    FHIR MedicationStatement from an NLP match

    Use this method to get FHIR resource for a note that is for a ** specific encounter **.
    Be advised that a single note can reference past medical history.

    :param subject_id: ID for patient (isa REF can be UUID)
    :param encounter_id: ID for encounter (isa REF can be UUID)
    :param nlp_match: response from cTAKES or other NLP Client
    :param source: NLP Version information, if none is provided use version of ctakesclient.
    :return: FHIR MedicationStatement (note it will have a random id)
    """
    medication = MedicationStatement()

    # id linkage
    medication.id = _random_id()
    medication.subject = _ref_subject(subject_id)
    medication.context = _ref_encounter(encounter_id)
    medication.status = "unknown"

    # NLP
    _nlp_extensions(medication, docref_id, nlp_match, source)
    medication.medicationCodeableConcept = nlp_concept(nlp_match)

    return medication


def nlp_procedure(
    subject_id: str,
    encounter_id: str,
    docref_id: str,
    nlp_match: MatchText,
    source: Extension = None,
) -> Procedure:
    """
    FHIR Procedure from an NLP match

    Use this method to get FHIR resource for a note that is for a ** specific encounter **.
    Be advised that a single note can reference past medical history.

    :param subject_id: ID for Patient (isa REF can be UUID)
    :param encounter_id: ID for visit (isa REF can be UUID)
    :param docref_id: ID for DocumentReference (isa REF can be UUID)
    :param nlp_match: response from cTAKES or other NLP Client
    :param source: NLP Version information, if none is provided use version of ctakesclient.
    :return: FHIR Procedure (note it will have a random id)
    """
    procedure = Procedure()

    # id linkage
    procedure.id = _random_id()
    procedure.subject = _ref_subject(subject_id)
    procedure.encounter = _ref_encounter(encounter_id)
    procedure.status = "unknown"

    # NLP
    _nlp_extensions(procedure, docref_id, nlp_match, source)
    procedure.code = nlp_concept(nlp_match)

    return procedure


def nlp_fhir(
    subject_id: str,
    encounter_id: str,
    docref_id: str,
    nlp_results: CtakesJSON,
    source: Extension = None,
    polarity: Polarity = Polarity.pos,
) -> List[DomainResource]:
    """
    Returns all FHIR resources we can generate from a patient encounter.

    This is useful if you are not separating out the types yourself, but dumping to a database or similar store,
    where a downstream process will separate out and work upon the FHIR.

    Use this method to get all FHIR resources for a note that is for a ** specific encounter **.
    Be advised that a single note can reference past medical history.

    :param subject_id: ID for Patient (isa REF can be UUID)
    :param encounter_id: ID for visit (isa REF can be UUID)
    :param docref_id: ID for DocumentReference (isa REF can be UUID)
    :param nlp_results: response from cTAKES or other NLP Client
    :param source: NLP Version information, if none is provided use version of ctakesclient.
    :param polarity: filter only positive mentions by default
    :return: List of FHIR Resources (DomainResource)
    """
    as_fhir = []

    for match in nlp_results.list_sign_symptom(polarity):
        as_fhir.append(nlp_observation(subject_id, encounter_id, docref_id, match, source))

    for match in nlp_results.list_medication(polarity):
        as_fhir.append(nlp_medication(subject_id, encounter_id, docref_id, match, source))

    for match in nlp_results.list_disease_disorder(polarity):
        as_fhir.append(nlp_condition(subject_id, encounter_id, docref_id, match, source))

    for match in nlp_results.list_procedure(polarity):
        as_fhir.append(nlp_procedure(subject_id, encounter_id, docref_id, match, source))

    return as_fhir
