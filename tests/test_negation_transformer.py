from tests.test_negation import *

class TestNegationTransformer(unittest.TestCase):

    def test_negation_api_example(self):
        self.assertPolarityCompatible(note_negation_api_example())

    def test_negated_symptoms_list(self):
        for note in [note_negated_denies(),
                     note_negated_ros_review_of_symptoms()]:
            #note = note.replace('¿', ' ')
            self.assertEqual(list(), self.false_positives(note))

    def false_positives(self, note: note_negated_denies()):
        ner = ctakesclient.client.extract(note)
        symptoms = ner.list_sign_symptom()
        spans = ner.list_spans(symptoms)
        polarities_cnlp = ctakesclient.transformer.list_polarity(sentence=note, spans=spans)

        fp = list()

        for index in range(0, len(symptoms)):
            polarity = polarities_cnlp[index]

            if polarity != Polarity.neg:
                #print(f'symptoms={symptoms}, polarities={polarities_cnlp}, text={note}')
                fp.append(symptoms[index].text)
        return fp

    def assertPolarityCompatible(self, text: str):
        ner = ctakesclient.client.extract(text)
        symptoms = ner.list_sign_symptom()
        polarities_ctakes = ner.list_polarity(symptoms)
        polarities_cnlp = ctakesclient.transformer.list_polarity(text, ner.list_spans(symptoms))

        self.assertEqual(polarities_ctakes, polarities_cnlp, text)

    def debug_helper(self, text: str):
        print('###############################################################################')
        print(text)

        ner = ctakesclient.client.extract(text)

        matches = ner.list_match()
        spans = ner.list_spans(matches)

        for match in matches:
            print(f'{match.polarity.name}\t{match.span()}\t{match.text}\t\t{match.type.value}')

        polarities_cnlp = ctakesclient.transformer.list_polarity(text, spans)
        polarities_ctakes = ner.list_polarity(spans)

        print('###############################################################################')
        print('cNLP=')
        print(polarities_cnlp)

        print('###############################################################################')
        print('cTAKES=')
        print(polarities_ctakes)


if __name__ == '__main__':
    unittest.main()
