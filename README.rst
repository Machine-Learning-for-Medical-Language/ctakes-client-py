.. contents:: ctakes-client-python

what is ctakes-client-python?
==============================

This package simplifies communication with CTAKES servers which produce matches with UMLS Concepts.

- Clinical Text and Knowledge Extraction System (http://ctakes.apache.org) 
- UMLS Unified Medical Language System

Quickstart
==============================
::
   pip install ctakes-client


Configuration
==============================
Default client talks to "localhost" running a server locally (https://github.com/Machine-Learning-for-Medical-Language/ctakes-covid-container)
::
   export CTAKES_URL_REST='http://tmill-desktop:8082/ctakes-web-rest/service/analyze'

   
HTTP Request
==============================
::
   text = 'Chief Complaint: Patient c/o cough, denies fever, recent COVID test negative. Denies smoking.'
   
   ctakes_client.call_ctakes(text)

   
   
   
   

	      
