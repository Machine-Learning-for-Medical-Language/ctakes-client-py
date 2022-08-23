.. contents:: ctakes-client-python

what is ctakes-client-python?
==============================

This package simplifies communication with CTAKES NLP servers which produce matches with UMLS Concepts.

- Clinical Text and Knowledge Extraction System (http://ctakes.apache.org)  
- UMLS Unified Medical Language System

Quickstart
==============================
Python3 pip install
::
   pip install ctakes-client

   

Configuration
==============================
Default client talks to "localhost" running a server locally (https://github.com/Machine-Learning-for-Medical-Language/ctakes-covid-container)
::
   export CTAKES_URL_REST='http://tmill-desktop:8082/ctakes-web-rest/service/analyze'

   
HTTP Request
==============================
Clinical text fragment or entire physician note. 
::
   clinical_text = 'Chief Complaint: Patient c/o cough, denies fever, recent COVID test negative. Denies smoking.'
   
   response = ctakes_client.call_ctakes(text)


HTTP Response
==============================
This client parses responses into lists of MatchText and UmlsConcept. 
::
    CtakesJSON(response)

    def list_match(self) -> List[MatchText]
    
    def list_concept(self) -> List[UmlsConcept]

    def list_sign_symptom(self) -> List[MatchText]

    def list_disease_disorder(self) -> List[MatchText]

    def list_medication(self) -> List[MatchText]

    def list_procedure(self) -> List[MatchText]

    def list_anatomical_site(self) -> List[MatchText]

    def list_identified_annotation(self) -> List[MatchText]
    
    


   
   
   
   

	      
