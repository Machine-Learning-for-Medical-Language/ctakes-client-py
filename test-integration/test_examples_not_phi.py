import unittest
import logging
from collections import OrderedDict
from typing import List
import json
import ctakesclient
from test.test_resources import curated, synthetic, list_resources

def read_text(filepath:str) -> str:
    with open(filepath, 'r') as f:
        return f.read()

def read_json(filepath:str) -> dict:
    with open(filepath, 'r') as f:
        return json.load(f)

def list_corpus_zip(corpus=curated()):
    """
    :param corpus: physician notes collection
    :return: Iterable collection of sorted TXT and JSON files
    """
    files_txt = list_resources(corpus, '.txt')
    files_json = list_resources(corpus, '.txt.json')
    return zip(files_txt, files_json)

def post_corpus_to_server(corpus=curated()) -> List[str]:
    """
    Send corpus of notes to cTAKES server (HTTP required)
    :param corpus: physician notes collection
    :return list of JSON files
    """
    logging.getLogger().setLevel(logging.DEBUG)

    processed = list()
    for path_txt in list_resources(corpus, '.txt'):

        text = read_text(path_txt)
        logging.debug(path_txt)
        ctakes_json = ctakesclient.client.post(text)

        path_json = path_txt.replace('.txt', '.txt.json')

        with open(path_json, 'w') as fp_output:
            json.dump(ctakes_json, fp_output, indent=4)
            processed.append(path_json)
    return processed

def term_freq(term_list: list) -> dict:
    """
    Term Frequency calculation
    :param term_list: String, CUI, CODE, or other "term"
    :return: OrderedDict sorted by count descending
    """
    tf = dict()
    for term in term_list:
        if term not in tf.keys():
            tf[term] = 1
        else:
            tf[term] += 1

    ordered = OrderedDict()
    for k in sorted(tf, key=tf.get, reverse=True):
        ordered[k] = tf[k]
    return ordered

def term_freq_corpus(corpus=curated(), write_json=True) -> dict:
    """
    Send corpus of notes to cTAKES server (HTTP required)
    :param corpus: physician notes collection
    :param write_json: output json file "corpus.tf.json"
    :return list of JSON files
    """
    terms_type = list()
    terms_text = list()
    terms_cui = list()
    terms_polarity = list()

    for path_json in list_resources(corpus, '.txt.json'):
        reader = ctakesclient.CtakesJSON(read_json(path_json))

        terms_cui += reader.list_concept_cui()
        terms_text += reader.list_match_text()
        terms_polarity += [p.name for p in reader.list_polarity(reader.list_match())]
        terms_type += [t.name for t in reader.list_match_type()]

    tf= {'corpus': corpus,
         'cui': term_freq(terms_cui),
         'text': term_freq(terms_text),
         'type': term_freq(terms_type),
         'polarity': term_freq(terms_polarity)}

    if write_json:
        with open(f'{corpus}/corpus.tf.json', 'w') as f:
            json.dump(tf, f, indent=4)

    return tf

class TestExamples(unittest.TestCase):

    def test_server(self):
        post_corpus_to_server(synthetic())
        post_corpus_to_server(curated())

    @unittest.skip('character position issue?')
    def test_json_response(self):
        self.assertCtakesJSON(synthetic())
        self.assertCtakesJSON(curated())

    def test_term_freq(self):

        texts = ['cold', 'cough', 'flu', 'covid', 'cough']
        tf = term_freq(term_list=texts)

        self.assertEqual(2, tf.get('cough'))
        self.assertEqual(1, tf.get('cold'))
        self.assertEqual(None, tf.get('diabetes'))

        term_freq_corpus(synthetic())
        term_freq_corpus(curated())

    def assertCtakesJSON(self, corpus=synthetic()):
        """
        Assert that all CTakes client helper functions can be called and that response is well formulated.
        Physician note TEXT should match the MatchText.span() and MatchText.text.

        :param corpus: directory with ctakes JSON respones
        """
        for path_txt, path_json in list_corpus_zip(corpus=corpus):

            physician_note = read_text(path_txt)
            ctakes_json = read_json(path_json)

            reader = ctakesclient.CtakesJSON(ctakes_json)

            # test methods do not throw Exception - basic method test
            reader.list_anatomical_site()
            reader.list_disease_disorder()
            reader.list_medication()
            reader.list_sign_symptom()
            reader.list_procedure()

            match_list = reader.list_match()
            text_list = reader.list_match_text()
            span_list = reader.list_spans(match_list)
            polarity_list = reader.list_polarity(match_list)

            reader.list_concept()
            reader.list_concept_cui()
            reader.list_concept_tui()
            reader.list_concept_code()

            for match in match_list:
                expected = match.text
                actual = physician_note[match.span().begin: match.span().end]

                if expected != actual:
                    logging.error(f'{path_txt}')
                    logging.error(f'{match.as_json()}')
                    self.assertEqual(expected, actual, 'MatchText.span did not match original characters of physician note[begin:end]')


if __name__ == '__main__':
    unittest.main()
