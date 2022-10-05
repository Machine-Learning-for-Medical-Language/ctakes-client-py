"""File loading and parsing"""

from typing import List, Union
import logging
import json
import os
from ctakesclient.exceptions import BSVError

###############################################################################
# Filetype: *.bsv
#
# BSV = Bar|Separated|Value
#
###############################################################################


class BsvConcept:
    """
    BSV flat file of UMLS Concept
    """

    def __init__(self,
                 cui=None,
                 tui=None,
                 code=None,
                 vocab=None,
                 text=None,
                 pref=None):
        """
        BSV file format =
        CUI|TUI|CODE|VOCAB|TXT|PREF

        UMLS Concept Names and Sources
        https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.concept_names_and_sources_file_mr/

        :param cui: CUI from UMLS or NA for "identified annotation"
        :param code: CODE or "identified annotation" code
        :param vocab: SNOMEDCT_US or other vocab
                      https://www.nlm.nih.gov/research/umls/sourcereleasedocs/index.html
        :param text: string representation
        :param pref: preferred terms
                     https://www.nlm.nih.gov/research/umls/new_users/online_learning/Meta_004.html
        """
        self.cui = cui
        self.tui = tui
        self.code = code
        self.vocab = vocab
        self.text = text
        self.pref = pref

    def as_json(self):
        return self.__dict__

    def from_json(self, source):
        self.cui = source.get('cui')
        self.tui = source.get('tui')
        self.code = source.get('code')
        self.vocab = source.get('vocab')
        self.text = source.get('text')
        self.pref = source.get('pref')

    def from_bsv(self, source):
        if isinstance(source, BsvConcept):
            return source

        if isinstance(source, str):
            source = source.split('|')

        if 6 != len(source):
            raise BSVError(f'from_bsv failed: {source}')

        self.cui = source[0]
        self.tui = source[1]
        self.code = source[2]
        self.vocab = source[3]
        self.text = source[4]
        self.pref = source[5]

    def to_bsv(self):
        return f'{self.cui}|{self.tui}|{self.code}|{self.vocab}|{self.text}|{self.pref}'

    def __str__(self):
        return self.to_bsv()


###############################################################################
# Filetype: *.bsv
#
# BSV Semantic Types
#
###############################################################################
class BsvSemanticType:
    """
    BSV file of Unified Medical Language System Groups
    National Library of Medicine provided source : SemGroups_2018.bsv

    TODO: cTAKES also has a Mentions grouping of UMLS Types
    https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/documentation/SemanticTypesAndGroups.html
    """

    def __init__(self,
                 group_id=None,
                 group_label=None,
                 tui=None,
                 tui_label=None):
        """
        :param group_id: UMLS Semantic Group Abbreviation
        :param group_label: UMLS Semantic Group Label (longer than abbreviation)
        :param tui: Term Unique Identifier (of semantic type)
        :param tui_label: TUI label (human readable)
        """
        self.group_id = group_id
        self.group_label = group_label
        self.tui = tui
        self.tui_label = tui_label

    def as_json(self):
        return self.__dict__

    def from_json(self, source):
        self.group_id = source.get('group_id')
        self.group_label = source.get('group_label')
        self.tui = source.get('tui')
        self.tui_label = source.get('tui_label')

    def from_bsv(self, source):
        if isinstance(source, BsvSemanticType):
            return source

        if isinstance(source, str):
            source = source.split('|')

        if 4 != len(source):
            raise BSVError(f'from_bsv failed: {source}')

        self.group_id = source[0]
        self.group_label = source[1]
        self.tui = source[2]
        self.tui_label = source[3]

    def to_bsv(self):
        return f'{self.group_id}|{self.group_label}|{self.tui}|{self.tui_label}'

    def __str__(self):
        return self.to_bsv()


###############################################################################
# FUNCTIONS for file handling
#
# File Common Helper functions with INFO logging
#
###############################################################################
def list_bsv(filename: str, class_bsv) -> list:
    """
    :param filename: BSV filename to parse
    :param class_bsv: what type of BSV resource to construct
    :return: list of BSV entries
    """
    entries = []
    for line in read_text_lines(filename):
        if line.startswith('#'):
            logging.info('found header : %s : %s', line, filename)
        else:
            parsed = class_bsv()
            parsed.from_bsv(line.strip())
            entries.append(parsed)
    return entries


def list_bsv_semantics(filename: str) -> List[BsvSemanticType]:
    return list_bsv(filename, BsvSemanticType)


def list_bsv_concept(filename: str) -> List[BsvConcept]:
    return list_bsv(filename, BsvConcept)


def map_cui_pref(concepts: Union[str, List[BsvConcept]]) -> dict:
    """
    :param concepts: a loaded BSV file, where rows are CUI|TUI|CODE|VOCAB|TXT|PREF, or a filename to load
    :return: map of {cui:text} labels
    """
    if isinstance(concepts, str):
        concepts = list_bsv_concept(concepts)

    cui_map = {}
    for bsv in concepts:
        cui_map[bsv.cui] = bsv.pref.strip()
    return cui_map


###############################################################################
#
# File Common Helper functions with INFO logging
#
###############################################################################
def read_text(filename) -> str:
    logging.info('read_text(%s)', filename)
    with open(filename, 'r', encoding='utf-8') as fp:
        return fp.read()


def read_text_lines(filename) -> List[str]:
    logging.info('read_text_lines(%s)', filename)
    with open(filename, 'r', encoding='utf-8') as fp:
        return fp.readlines()


def read_json(filename) -> dict:
    logging.info('read_json(%s)', filename)
    with open(filename, 'r', encoding='utf-8') as fp:
        return json.load(fp)


###############################################################################
#
# Standard BSVs for wide-interest topics, shipped with ctakesclient
#
###############################################################################

def _resource_file(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), 'resources', filename)


def covid_symptoms() -> List[BsvConcept]:
    """Returns a list of known covid symptoms"""
    return list_bsv_concept(_resource_file('covid_symptoms.bsv'))


def umls_semantic_groups() -> List[BsvSemanticType]:
    """
    Returns a list of UMLS semantic groups

    See https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/documentation/SemanticTypesAndGroups.html
    """
    return list_bsv_semantics(_resource_file('SemGroups_2018.bsv'))
