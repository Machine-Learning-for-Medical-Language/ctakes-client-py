.. contents:: ctakes-client-python

Purpose: Extract Medical Concepts from Physician Notes
=======================================================
This package simplifies communication with CTAKES NLP servers which produce matches with UMLS Concepts.

- Clinical Text and Knowledge Extraction System (http://ctakes.apache.org)  
- UMLS Unified Medical Language System


Quickstart
==============================
Clinical text fragment or entire physician note.
::
   physician_note = 'Chief Complaint: Patient c/o cough, denies fever, recent COVID test negative. Denies smoking.'

Output medical concepts matches by type
==========================================
This client parses responses into lists of MatchText and UmlsConcept. 
::
    CtakesJSON(output)

    list_match() -> List[MatchText]
    
    list_concept() -> List[UmlsConcept]

    list_sign_symptom() -> List[MatchText]

    list_disease_disorder() -> List[MatchText]

    list_medication() -> List[MatchText]

    list_procedure() -> List[MatchText]

    list_anatomical_site() -> List[MatchText]


Output Physician Note MatchText
===================================
MatchText(s) are the character positions in the physician note where a UmlsConcept was found.
.. |MatchText| image:: README/diagram/MatchText.png
  :width: 400
  :alt: MatchText::= begin end text polarity UmlsConcept+

Unified Medical Language System (UMLS) Concepts
================================================
For general information on UMLS, see National Library of Medicine: https://www.nlm.nih.gov/research/umls/
.. |UmlsConcept| image:: README/diagram/UmlsConcept.png
  :width: 400
  :alt: UmlsConcept::= begin end text polarity UmlsConcept+

    
UMLS (Unified Medical Language System)
=========================================================
For convenience, the list of UMLS Semantic Types is provided here.

.. csv-table:: Semantic Types and Groupings
   :file: README/SemGroups_2018.csv
   :widths: 10, 20, 10, 60
   :header-rows: 1

   
   
   

	      
