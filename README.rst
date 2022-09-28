Purpose: Extract Medical Concepts from Physician Notes
=======================================================
This package simplifies communication with cTAKES NLP servers which produce matches with UMLS Concepts.

- Clinical Text and Knowledge Extraction System (http://ctakes.apache.org)  
- UMLS Unified Medical Language System / National Library of Medicine (https://nlm.nih.gov/research/umls)


Quickstart
==============================
Clinical text fragment or entire physician note.

.. code-block:: python3

   physician_note = 'Chief Complaint: Patient c/o cough, denies fever, recent COVID test negative. Denies smoking.'
   output = ctakesclient.client.post(physician_note)

Output
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


MatchText: Physician Notes
===================================
MatchText(s) are the character positions in the physician note where a UmlsConcept was found.

.. image:: https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/MatchText.png
  :width: 400
  :alt: MatchText::= begin end text polarity UmlsConcept+

MatchText: Polarity
===================================
.. image:: https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/polarity.png

UMLS Concept
================================================
.. image:: https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/UmlsConcept.png
.. image:: https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/cui.png
.. image:: https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/tui.png

UMLS Vocabulary
================================================
.. image:: https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/codingScheme.png
.. image:: https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/code.png

UMLS Semantic Types and Groups
=========================================================
You can browse the `list of UMLS Semantic Types`_ at the
National Library of Medicine.

.. _list of UMLS Semantic Types: https://uts.nlm.nih.gov/uts/umls/semantic-network/root