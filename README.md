# Purpose: Extract Medical Concepts from Physician Notes
This package simplifies communication with cTAKES NLP servers which produce matches with UMLS Concepts.

- Clinical Text and Knowledge Extraction System ([cTAKES](http://ctakes.apache.org))
- Unified Medical Language System ([UMLS](https://nlm.nih.gov/research/umls))

# Quickstart
Clinical text fragment or entire physician note.

```python
physician_note = 'Chief Complaint: Patient c/o cough, denies fever, recent COVID test negative. Denies smoking.'
output = await ctakesclient.client.post(physician_note)
```

Note that `ctakesclient` uses an async API.
If your code is not async, you can simply wrap calls in `asyncio.run()`:

```python
output = asyncio.run(ctakesclient.client.post(physician_note))
```

# Output

This client parses responses into lists of MatchText and UmlsConcept.

```
CtakesJSON(output)

list_match() -> List[MatchText]

list_concept() -> List[UmlsConcept]

list_sign_symptom() -> List[MatchText]

list_disease_disorder() -> List[MatchText]

list_medication() -> List[MatchText]

list_procedure() -> List[MatchText]

list_anatomical_site() -> List[MatchText]
```

# MatchText: Physician Notes
MatchText(s) are the character positions in the physician note where a UmlsConcept was found.

![MatchText::= begin end text polarity UmlsConcept+](https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/MatchText.png)

# MatchText: Polarity
![](https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/polarity.png)

# UMLS Concept
![](https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/UmlsConcept.png)
![](https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/cui.png)
![](https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/tui.png)

# UMLS Vocabulary
![](https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/codingScheme.png)
![](https://raw.githubusercontent.com/Machine-Learning-for-Medical-Language/ctakes-client-py/de43929/docs/diagram/code.png)

# UMLS Semantic Types and Groups
You can browse the [list of UMLS Semantic Types](https://uts.nlm.nih.gov/uts/umls/semantic-network/root)
at the National Library of Medicine.
