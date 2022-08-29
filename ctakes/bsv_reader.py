from typing import List
import logging

class BSV(object):
    def __init__(self, cui=None, code=None, vocab=None, text=None, pref=None):
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
        self.code = code
        self.vocab = vocab
        self.text = text
        self.pref = pref

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
                cols = line.split('|')
                if 5 != len(cols):
                    logging.error(f'unknown line {line}')
                    raise Exception(f'cannot parse BSV line: {line}, cols was {cols}')
                entries.append(BSV(
                    cui=cols[0],
                    code=cols[1],
                    vocab=cols[2],
                    text=cols[3],
                    pref=cols[4]))

    return entries

def bsv_to_cui_map(bsv_file) -> dict:
    """
    :param bsv_file: see BSV file, where rows are CUI|TUI|CODE|VOCAB|TXT|PREF
    :return: map of {cui:text} labels
    """
    cui_map = dict()
    for bsv in list_bsv(bsv_file):
        cui_map[bsv.cui] = bsv.pref
    return cui_map
