import json
from typing import List
import logging

class BSV:
    def __init__(self, cui=None, tui=None, code=None, vocab=None, text=None, pref=None):
        """
        BSV file format =
        CUI|TUI|CODE|VOCAB|TXT|PREF

        UMLS Concept Names and Sources
        https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.concept_names_and_sources_file_mr/

        :param cui: CUI from UMLS or NA for "identified annotation"
        :param code: CODE or "identified annotation" code
        :param vocab: SNOMEDCT_US or other vocab https://www.nlm.nih.gov/research/umls/sourcereleasedocs/index.html
        :param text: string representation
        :param pref: preferred terms https://www.nlm.nih.gov/research/umls/new_users/online_learning/Meta_004.html
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
        if isinstance(source, BSV):
            return source

        if isinstance(source, str):
            source = source.split('|')

        if 6 != len(source):
            raise Exception(f'from_bsv failed: {source}')

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

def list_bsv(filename) -> List[BSV]:
    """
    :param filename: BSV filename to parse
    :return: list of BSV entries
    """
    entries = list()

    with open(filename) as f:
        for line in f.read().splitlines():
            if line.startswith('#'):
                logging.info(f'found header : {line}')
            else:
                parsed = BSV()
                parsed.from_bsv(line)
                entries.append(parsed)

    return entries

def bsv_file_cui_map(bsv_file) -> dict:
    """
    :param bsv_file: see BSV file, where rows are CUI|TUI|CODE|VOCAB|TXT|PREF
    :return: map of {cui:text} labels
    """
    cui_map = dict()
    for bsv in list_bsv(bsv_file):
        cui_map[bsv.cui] = bsv.pref
    return cui_map

def read_text(filename) -> str:
    logging.info(f'read_text({filename})')
    with open(filename, 'r') as fp:
        return fp.read()

def read_text_lines(filename) -> List[str]:
    logging.info(f'read_text({filename})')
    with open(filename, 'r') as fp:
        return fp.readlines()

def read_json(filename) -> dict:
    logging.info(f'read_json({filename})')
    with open(filename, 'r') as fp:
        return json.load(fp)

