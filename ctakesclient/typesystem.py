"""UMLS (Unified Medical Language System)"""
import json
import logging
from typing import List
from enum import Enum


class UmlsTypeMention(Enum):
    """
    Semantic Types in the UMLS (Unified Medical Language System)
    https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/documentation/SemanticTypesAndGroups.html
    Semantic type groupings here:
    """

    # pylint: disable=invalid-name
    DiseaseDisorder = "DiseaseDisorderMention"
    SignSymptom = "SignSymptomMention"
    AnatomicalSite = "AnatomicalSiteMention"
    Medication = "MedicationMention"
    Procedure = "ProcedureMention"
    CustomDict = "IdentifiedAnnotation"


class UmlsConcept:
    """Concept in the UMLS (Unified Medical Language System)"""

    def __init__(self, source=None):
        """
        * CUI   Concept Unique Identifier
        * CODE  identified by the vocabulary
        https://www.ncbi.nlm.nih.gov/books/NBK9684/#ch02.sec2.5

        * codingScheme also known as SAB for "source abbreviation" or vocabulary
        https://www.nlm.nih.gov/research/umls/sourcereleasedocs/index.html

        * TUI Type Unique Identifier (semantic types)
        https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/documentation/SemanticTypesAndGroups.html

        :param source: contains UMLS concept metadata
        """
        self.codingScheme = None  # pylint: disable=invalid-name
        self.code = None
        self.cui = None
        self.tui = None

        if source:
            self.from_json(source)

    def from_json(self, source: dict) -> None:
        """
        :param source: contains UMLS Concept source
        """
        self.codingScheme = source.get("codingScheme")
        self.code = source.get("code")
        self.cui = source.get("cui")
        self.tui = source.get("tui")

    def as_json(self) -> dict:
        return {"code": self.code, "cui": self.cui, "codingScheme": self.codingScheme, "tui": self.tui}

    def as_string(self) -> str:
        """
        :return: string representation, also serves as "key" for sorting.
        """
        return json.dumps(self.as_json(), indent=4)

    def __str__(self):
        return self.as_string()


###############################################################################
#
# JSON Responses from CTAKES REST Server
#
###############################################################################


class Polarity(Enum):
    """ "
    Polarity means "negation" like "patient denies cough".
    NegEx algorithm popularized by Wendy Chapman et al
    https://www.sciencedirect.com/science/article/pii/S1532046401910299
    """

    # pylint: disable=invalid-name
    pos = 0
    neg = -1


class Span:
    """
    Helper class to strongly type sharing of TextSpan similar to cTAKES package:
    https://ctakes.apache.org/apidocs/4.0.0/org/apache/ctakes/typesystem/type/textspan/package-summary.html
    """

    def __init__(self, begin: int, end: int):
        """
        :param begin: first character position for a MatchText
        :param end: last character position for a MatchText
        """
        self.begin = begin
        self.end = end

    def key(self) -> tuple:
        """
        :return: span as a single item (tuple entry)
        """
        return self.begin, self.end

    def __str__(self):
        return str(self.key())


class MatchText:
    """A fragment of text that may match a concept and polarity"""

    def __init__(self, source=None):
        self.begin = None
        self.end = None
        self.text = None
        self.polarity = None
        self.type = None
        self.conceptAttributes = None  # pylint: disable=invalid-name

        if source:
            self.from_json(source)

    def span(self) -> Span:
        return Span(self.begin, self.end)

    @staticmethod
    def parse_polarity(polarity) -> Polarity:
        if isinstance(polarity, Polarity):
            return polarity
        elif polarity == -1:
            return Polarity.neg
        elif polarity == 0:
            return Polarity.pos
        else:
            raise Exception(f"polarity unknown: {polarity}")

    @staticmethod
    def parse_mention(mention: str) -> UmlsTypeMention:
        if mention == "IdentifiedAnnotation":
            return UmlsTypeMention.CustomDict
        else:
            return UmlsTypeMention[mention.replace("Mention", "")]

    @staticmethod
    def sort_concepts(unsorted: List[UmlsConcept]) -> List[UmlsConcept]:
        """
        :param unsorted: guarantees responses from ctakes server are
                         identically ordered
        :return: sorted list of concepts.
        """
        return sorted(unsorted, key=UmlsConcept.as_string)

    def from_json(self, source: dict):
        self.begin = source.get("begin")
        self.end = source.get("end")
        self.text = source.get("text")
        self.type = self.parse_mention(source.get("type"))
        self.polarity = self.parse_polarity(source.get("polarity"))
        self.conceptAttributes = []

        # sort list of concepts ensuring same ordering
        unsorted = list(UmlsConcept(c) for c in source.get("conceptAttributes", []))

        for c in MatchText.sort_concepts(unsorted):
            self.conceptAttributes.append(c)

    def as_json(self):
        polarity_json = self.polarity.value
        concepts_json = [c.as_json() for c in self.conceptAttributes]
        return {
            "begin": self.begin,
            "end": self.end,
            "text": self.text,
            "polarity": polarity_json,
            "conceptAttributes": concepts_json,
            "type": self.type.value,
        }


class CtakesJSON:
    """Ctakes JSON contain MatchText with list of UmlsConcept"""

    def __init__(self, source=None):
        self.mentions = {}
        if source:
            self.from_json(source)

    def list_concept(self, polarity=None) -> List[UmlsConcept]:
        concat = []
        for match in self.list_match(polarity=polarity):
            concat += match.conceptAttributes
        return concat

    def list_concept_cui(self, polarity=None) -> List[str]:
        return [c.cui for c in self.list_concept(polarity)]

    def list_concept_tui(self, polarity=None) -> List[str]:
        return [c.tui for c in self.list_concept(polarity)]

    def list_concept_code(self, polarity=None) -> List[str]:
        return [c.code for c in self.list_concept(polarity)]

    def list_spans(self, matches: list) -> List[tuple]:
        return list(m.span().key() for m in matches)

    def list_polarity(self, matches: list) -> List[Polarity]:
        return list(m.polarity for m in matches)

    def list_match(self, polarity=None, filter_umls_type=None) -> List[MatchText]:
        logging.debug("list_match(polarity=%s, filter_umls_type=%s", polarity, filter_umls_type)

        if polarity is not None:
            polarity = MatchText.parse_polarity(polarity)

        concat = []
        for semtype, matches in self.mentions.items():
            if (filter_umls_type is None) or (semtype == filter_umls_type):
                if polarity is None:
                    concat += matches
                else:
                    for m in matches:
                        if polarity == m.polarity:
                            concat.append(m)
        return concat

    def list_match_text(self, polarity=None) -> List[str]:
        return list(m.text for m in self.list_match(polarity=polarity, filter_umls_type=None))

    def list_sign_symptom(self, polarity=None) -> List[MatchText]:
        return self.list_match(polarity, UmlsTypeMention.SignSymptom)

    def list_disease_disorder(self, polarity=None) -> List[MatchText]:
        return self.list_match(polarity, UmlsTypeMention.DiseaseDisorder)

    def list_medication(self, polarity=None) -> List[MatchText]:
        return self.list_match(polarity, UmlsTypeMention.Medication)

    def list_procedure(self, polarity=None) -> List[MatchText]:
        return self.list_match(polarity, UmlsTypeMention.Procedure)

    def list_anatomical_site(self, polarity=None) -> List[MatchText]:
        return self.list_match(polarity, UmlsTypeMention.AnatomicalSite)

    def list_identified_annotation(self, polarity=None) -> List[MatchText]:
        return self.list_match(polarity, UmlsTypeMention.CustomDict)

    def from_json(self, source: dict) -> None:
        for mention, match_list in source.items():
            semtype = MatchText.parse_mention(mention)

            if semtype not in self.mentions:
                self.mentions[semtype] = []

            for m in match_list:
                self.mentions[semtype].append(MatchText(m))

    def as_json(self):
        res = {}
        for mention, match_list in self.mentions.items():
            match_json = [m.as_json() for m in match_list]

            res[mention.value] = match_json
        return res
