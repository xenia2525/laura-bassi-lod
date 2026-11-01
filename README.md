# Laura Bassi in Linked Open Data

LODLAM project for **Information Science and Cultural Heritage** (DHDK, University of Bologna, 2025/2026), Prof. Francesca Tomasi and Prof. Marilena Daquino.

**Author:** Polyxeni Chasanai
**Report (website):** https://xenia2525.github.io/laura-bassi-lod/

Starting from the English Wikipedia page [Laura Bassi](https://en.wikipedia.org/w/index.php?title=Laura_Bassi&oldid=1372047911), the project creates structured data about her and the entities related to her.

## 1. Study of the domain

| | File |
|---|---|
| **Idea:** Laura Bassi (1711–1778), physicist, the first woman with a university chair in Europe (Bologna, 1732) | [index.html](index.html) |
| **Entities:** 13 selected entities (people, places, organisations, events, a work, a concept), linked to Wikidata and VIAF | [docs/entities.csv](docs/entities.csv) (column `core`) |

## 2. Knowledge organisation

| | File |
|---|---|
| **Theoretical model:** relations between Laura Bassi and the 13 entities | [models/theoretical_model.png](models/theoretical_model.png), [models/theoretical_model.md](models/theoretical_model.md) |
| **Conceptual model:** the ontology, reusing CIDOC CRM, FOAF, schema.org, FaBiO, SKOS and DC Terms | [models/ontology.ttl](models/ontology.ttl), [models/conceptual_model.md](models/conceptual_model.md) |
| **Graffoo diagram** of the conceptual model | [models/conceptual_model_graffoo.svg](models/conceptual_model_graffoo.svg) |

## 3. Knowledge representation

| | File |
|---|---|
| **XML/TEI** document: the text of the page with the annotated entities, `listPerson`, `listOrg`, `listPlace`, `listEvent`, `listBibl`, `listRelation`, linked to Wikidata/VIAF | [data/laura_bassi.xml](data/laura_bassi.xml) |
| **XML → HTML** transformation (XSLT, run with Python) and its output | [scripts/tei2html.xsl](scripts/tei2html.xsl), [scripts/tei2html.py](scripts/tei2html.py) → [output/laura_bassi.html](output/laura_bassi.html) |
| **XML/TEI → RDF** transformation (Python, rdflib) and the dataset | [scripts/tei2rdf.py](scripts/tei2rdf.py) → [data/laura_bassi.ttl](data/laura_bassi.ttl) |

## How to run the scripts

```bash
pip install lxml rdflib
python scripts/tei2html.py   # creates output/laura_bassi.html
python scripts/tei2rdf.py    # creates data/laura_bassi.ttl
```

## License

Code under the license in `LICENSE`. Text derived from Wikipedia under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
