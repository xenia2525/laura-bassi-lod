# Laura Bassi – a LODLAM project

Individual project for **Information Science and Cultural Heritage** (DHDK, University of Bologna, a.y. 2025/2026 — Prof. Francesca Tomasi & Prof. Marilena Daquino).

Starting from the Wikipedia page [Laura Bassi](https://en.wikipedia.org/wiki/Laura_Bassi) — the first woman to hold an official university chair in Europe (University of Bologna, 1732) — the project models the page's topic and related entities, encodes the text in XML/TEI, and publishes the result as Linked Open Data.

## Structure

| Folder | Content |
|---|---|
| `data/` | `laura_bassi.xml` (XML/TEI, annotated text) · `laura_bassi.ttl` (RDF dataset) |
| `scripts/` | `tei2html.xsl` + `tei2html.py` (XML → HTML) · `tei2rdf.py` (XML/TEI → RDF, rdflib) |
| `output/` | `laura_bassi.html` (HTML generated from the TEI) |
| `models/` | Theoretical model (mind map) · Conceptual model (Graffoo diagram) |
| `docs/` | Notes, entity table, sources |
| `index.html` | Project report (published with GitHub Pages) |

## Workflow

1. **Domain study** – topic and ≥ 10 related entities
2. **Theoretical model** – relations between the topic and the entities (mind map)
3. **Conceptual model** – formal ontology reusing existing vocabularies + Graffoo diagram
4. **XML/TEI** – text of the page with annotated entities, `listPerson`, `listPlace`, `listOrg`, `listEvent`, `listBibl`, `listRelation`, reconciled to Wikidata / VIAF / LCSH / WorldCat
5. **XML → HTML** – XSLT run from Python (lxml)
6. **XML/TEI → RDF** – Python + rdflib, Turtle serialization
7. **Report** – web page linking all the files

## Requirements

```bash
pip install lxml rdflib
python scripts/tei2html.py
python scripts/tei2rdf.py
```

## License

Code under the license in `LICENSE`. Text derived from Wikipedia is available under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
