Setup cTAKES server (optional)
==============================
Server server locally or use a remote server (https://github.com/Machine-Learning-for-Medical-Language/ctakes-covid-container)
::
   export URL_CTAKES_URL='http://localhost:8080/ctakes-web-rest/service/analyze'

   ner = ctakesclient.client.extract(physician_note, url=URL_CTAKES_URL)

Setup Clinical NLP Transformers  (Optional)
===============================================
https://github.com/Machine-Learning-for-Medical-Language/cnlp_transformers#negation-api
::
    export URL_CNLP_NEGATION='http://localhost:8000/negation/process'

cNLP transformer can be fed the original sentence and the ctakes spans (text regions) and answer with (potentially better) polarity for each span using a trained model.
::
    symptoms = ner.list_sign_symptom()
    spans = ner.list_spans(symptoms)

    polarities_ctakes = ner.list_polarity(matches=symptoms)
    polarities_cnlp = ctakesclient.transformer.list_polarity(physician_note, spans, url=URL_CNLP_NEGATION)
