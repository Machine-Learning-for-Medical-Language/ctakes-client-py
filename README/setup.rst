Setup cTAKES server (optional)
==============================
Server server locally or use a remote server (https://github.com/Machine-Learning-for-Medical-Language/ctakes-covid-container)
::
   export URL_CTAKES_URL='http://localhost:8080/ctakes-web-rest/service/analyze'

   output = ctakes_client.post(physician_note, server_address=URL_CTAKES_URL)

Setup Clinical NLP Transformers  (Optional)
===============================================
https://github.com/Machine-Learning-for-Medical-Language/cnlp_transformers#negation-api
::
   export URL_CNLP_NEGATION='http://localhost:8000/negation/process''

   output = ctakes_client.post(physician_note, server_address=URL_CTAKES_URL)
