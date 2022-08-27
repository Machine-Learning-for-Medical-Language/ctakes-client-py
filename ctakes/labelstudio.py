import os
import json
from ctakes.bsv_reader import BSV, list_bsv
from ctakes.ctakes_json import MatchText, UmlsConcept, CtakesJSON, UmlsTypeMention

class DocAnnot:
    def __init__(self, text: str):
        """
        :param text: input text of physician note
        """
        self.model_version = 'ctakes-covid'
        self.text = text
        self.result = list()

    def add_match(self, match: MatchText, labels):
        ner_spans = {'id': f'ss{len(self.result)}',
                     'from_name': 'label',
                     'to_name': 'text',
                     'type': 'labels',
                     'value': {
                        'start': match.begin,
                        'end': match.end,
                        'score': 1.0,
                        'text': match.text,
                        'labels': [labels]}}
        self.result.append(ner_spans)

    def add_concept(self, labels:set):
        whole_doc = {'id': f'ss{len(self.result)}',
                     'from_name': 'symptoms',
                     'to_name': 'text',
                     'type': 'choices',
                     'value': {'choices': [ss_name for ss_name in labels]}}

        self.result.append(whole_doc)

    # TODO: refactor
    def from_json(self, ctakes_said: CtakesJSON, cui_map: dict, umls_type= UmlsTypeMention.SignSymptom):
        """
        :param ctakes_said: JSON result from cTAKES
        :param cui_map: {cui:text} to select concepts for document level annotation
        :param umls_type: UMLS semantic type to filter by (select for)
        """
        whole_doc = set()

        if ctakes_said:
            for match in ctakes_said.list_match():
                for concept in match.conceptAttributes:
                    if concept.cui in cui_map.keys():
                        self.add_match(match, cui_map[concept.cui])
                        whole_doc.add(cui_map[concept.cui])

            self.add_concept(whole_doc)

    def as_json(self):
        return json.dumps(indent=4,
                          obj={'data': {'text': self.text},
                               'predictions': [{'model_version': self.model_version, 'result': self.result}]})


def find_by_name(dir_processed, endswith='ctakes.json') -> list:
    """
    :param dir_processed: root folder where JSON files are stored
    :param endswith: ctakes.json default, or other file pattern.
    :return:
    """
    found = list()
    for dirpath, dirs, files in os.walk(dir_processed):
        for filename in files:
            path = os.path.join(dirpath,filename)
            if path.endswith(endswith):
                found.append(path)

            if 0 == len(found) % 1000:
                print(f'found: {len(found)}')
                print(path)

    return found

def bsv_to_cui_map(bsv_file) -> dict:
    """
    :param bsv_file: see BSV file, where rows are CUI|TUI|CODE|VOCAB|TXT|PREF
    :return: map of {cui:text} labels
    """
    cui_map = dict()
    for bsv in list_bsv(bsv_file):
        cui_map[bsv.cui] = bsv.pref
    return cui_map