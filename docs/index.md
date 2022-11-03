# ``ctakesclient``: a Python interface for cTAKES

This package is an easy way to parse physician notes into a list of symptoms or medications.

`ctakesclient` talks to a [cTAKES](https://ctakes.apache.org/) natural language processing
(NLP) server to annotate fragments of text with appropriate medical
[UMLS](https://nlm.nih.gov/research/umls) concepts and polarity.

For example, given the note `Patient denies fever`, you can now detect that:

- The third word is a symptom
- That symptom relates to SNOMED CT codes 386661006 (fever) and 50177009 (elevated body temp)
- With negative polarity (they don't have it)

## Installation

`ctakesclient` can be installed from PyPI:

```sh
pip install ctakesclient
```

## Example

Let's explore the simple fever example above.

```python3
import ctakesclient, pprint

ner = ctakesclient.client.extract('Patient denies fever')

# Now print what we found
for symptom in ner.list_sign_symptom():
  pprint.pp(symptom.as_json())

# Which would print out something like:
{'begin': 15,
'conceptAttributes': [{'code': '386661006',
                       'codingScheme': 'SNOMEDCT_US',
                       'cui': 'C0015967',
                       'tui': 'T184'},
                      {'code': '50177009',
                       'codingScheme': 'SNOMEDCT_US',
                       'cui': 'C0015967',
                       'tui': 'T184'}],
'end': 20,
'polarity': -1,
'text': 'fever',
'type': 'SignSymptomMention'}
```

## Specifying which cTAKES Server to Use

By default, `ctakesclient` assumes the cTAKES server is running locally at `http://localhost:8080`.
There are two ways to tell it where the server actually lives.

By environment variable:

```sh
export URL_CTAKES_REST=https://ctakes.example.org/ctakes-web-rest/service/analyze
```

Or by code parameter, which overrides the environment variable:

```python3
ctakesclient.client.extract(text, url='https://ctakes.example.org/ctakes-web-rest/service/analyze')
```

## Using Clinical NLP Transformers (Optional)

The `ctakesclient.transformer` module uses a separate machine-learning NLP server to
get a second opinion on text polarity.

A cNLP transformer can be fed the original sentence plus the cTAKES spans (text regions)
and answer with (potentially better) polarity for each span using a trained model.

See the [cnlp_transformers](https://github.com/Machine-Learning-for-Medical-Language/cnlp_transformers#negation-api)
project for more information on how that works.

### Configuring the cNLP Server Address

The default cNLP server address is `http://localhost:8000/negation/process`.
But there are two ways to configure that.

By environment variable:

```sh
export URL_CNLP_NEGATION=https://cnlpt.example.org/negation/process
```

Or by code parameter, which overrides the environment variable:

```python3
ctakesclient.transformer.list_polarity(text, spans, url='https://cnlpt.example.org/negation/process')
```

### Example

```python3
import ctakesclient

note = 'Patient denies fever'
ner = ctakesclient.client.extract(note)

symptoms = ner.list_sign_symptom()
spans = ner.list_spans(symptoms)

polarities_ctakes = ner.list_polarity(symptoms)
polarities_cnlp = ctakesclient.transformer.list_polarity(note, spans)
```

```{eval-rst}
.. toctree::
   :maxdepth: 1
   :caption: Contents:

   api.rst
```
