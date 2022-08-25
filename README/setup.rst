Setup
==============================
Server server locally or use a remote server (https://github.com/Machine-Learning-for-Medical-Language/ctakes-covid-container)
::
   export CTAKES_URL_REST='http://YOUR_SERVER:YOUR_PORT/ctakes-web-rest/service/analyze'

   output = ctakes_client.send(physician_note, server_address=CTAKES_URL_REST)
