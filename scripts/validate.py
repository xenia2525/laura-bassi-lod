"""Validates the RDF dataset against the conceptual model.

1. Structural checks with SPARQL: every resource is typed and labelled, and the
   main properties are used with the domain and range declared in the model.
2. Authority control: which people, places and organisations are linked to
   Wikidata (owl:sameAs).
3. OWL 2 RL reasoning (owlrl) over ontology + data: the closure must not contain
   inconsistencies, and the expected inferences must appear (equivalent
   classes, sub-properties, symmetric properties).

Usage (from the repository root):
    pip install rdflib owlrl
    python scripts/validate.py
Output: docs/validation.md (and docs/validation.json for the website)
"""
from pathlib import Path
import json

import owlrl
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF

ROOT = Path(__file__).resolve().parent.parent
LB = "https://xenia2525.github.io/laura-bassi-lod/resource/"
PREFIXES = """
PREFIX lb: <https://xenia2525.github.io/laura-bassi-lod/resource/>
PREFIX lbo: <https://xenia2525.github.io/laura-bassi-lod/ontology#>
PREFIX schema: <https://schema.org/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX fabio: <http://purl.org/spar/fabio/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rel: <http://purl.org/vocab/relationship/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

# property: (allowed subject classes, allowed object classes), as in models/conceptual_model.md
EXPECTED = {
    "schema:spouse": (["foaf:Person"], ["foaf:Person"]),
    "schema:colleague": (["foaf:Person"], ["foaf:Person"]),
    "rel:mentorOf": (["foaf:Person"], ["foaf:Person"]),
    "lbo:patronOf": (["foaf:Person"], ["foaf:Person"]),
    "lbo:correspondedWith": (["foaf:Person"], ["foaf:Person"]),
    "lbo:precededBy": (["foaf:Person"], ["foaf:Person"]),
    "schema:memberOf": (["foaf:Person"], ["foaf:Organization"]),
    "schema:birthPlace": (["foaf:Person"], ["crm:E53_Place"]),
    "dbo:restingPlace": (["foaf:Person"], ["crm:E53_Place"]),
    "schema:knowsAbout": (["foaf:Person"], ["skos:Concept"]),
    "crm:P11_had_participant": (["crm:E5_Event"], ["foaf:Person"]),
    "crm:P14_carried_out_by": (["crm:E5_Event"], ["foaf:Organization", "foaf:Person"]),
    "crm:P7_took_place_at": (["crm:E5_Event"], ["crm:E53_Place"]),
    "crm:P16_used_specific_object": (["crm:E5_Event"], ["fabio:Thesis", "fabio:Expression"]),
    "crm:P89_falls_within": (["crm:E53_Place"], ["crm:E53_Place"]),
    "dcterms:creator": (["fabio:Thesis", "fabio:Expression", "fabio:Book", "fabio:JournalArticle", "schema:Quotation"], ["foaf:Person"]),
    "dcterms:isPartOf": (["fabio:JournalArticle"], ["fabio:Journal"]),
}


def ask(g, query):
    return list(g.query(PREFIXES + query))


def main():
    data = Graph().parse(ROOT / "data" / "laura_bassi.ttl")
    onto = Graph().parse(ROOT / "models" / "ontology.ttl")
    report = {"triples": len(data), "checks": [], "authority": {}, "reasoning": {}}

    def check(name, failures):
        report["checks"].append({"check": name, "ok": not failures, "failures": failures[:10]})

    # 1. structure --------------------------------------------------------------
    check("Every resource has a type", [str(r[0]) for r in ask(data, """
        SELECT DISTINCT ?s WHERE { ?s ?p ?o FILTER(STRSTARTS(STR(?s), STR(lb:))) FILTER NOT EXISTS { ?s a ?t } }""")])
    check("Every resource has an rdfs:label", [str(r[0]) for r in ask(data, """
        SELECT DISTINCT ?s WHERE { ?s a ?t FILTER(STRSTARTS(STR(?s), STR(lb:))) FILTER NOT EXISTS { ?s rdfs:label ?l } }""")])
    for prop, (dom, rng) in EXPECTED.items():
        dom_v = " ".join(dom)
        rng_v = " ".join(rng)
        bad = ask(data, f"""
            SELECT ?s ?o WHERE {{ ?s {prop} ?o .
              FILTER NOT EXISTS {{ VALUES ?d {{ {dom_v} }} ?s a ?d }} }}""")
        bad += ask(data, f"""
            SELECT ?s ?o WHERE {{ ?s {prop} ?o .
              FILTER NOT EXISTS {{ VALUES ?r {{ {rng_v} }} ?o a ?r }} }}""")
        used = len(ask(data, f"SELECT ?s WHERE {{ ?s {prop} ?o }}"))
        check(f"{prop} used {used}× with domain {'/'.join(dom)} and range {'/'.join(rng)}",
              [f"{s} → {o}" for s, o in bad])

    # 2. authority control ------------------------------------------------------
    for cls in ("foaf:Person", "foaf:Organization", "crm:E53_Place", "skos:Concept"):
        total = len(ask(data, f"SELECT ?s WHERE {{ ?s a {cls} FILTER(STRSTARTS(STR(?s), STR(lb:))) FILTER(STRLEN(STRAFTER(STR(?s), STR(lb:))) != 32) }}"))
        linked = len(ask(data, f"""SELECT DISTINCT ?s WHERE {{ ?s a {cls} {{ ?s owl:sameAs ?w }} UNION {{ ?s skos:exactMatch ?w }}
                                   FILTER(STRSTARTS(STR(?w), "http://www.wikidata.org/entity/")) }}"""))
        report["authority"][cls] = {"total": total, "wikidata": linked}

    # 3. OWL 2 RL reasoning -----------------------------------------------------
    g = Graph()
    for t in onto:
        g.add(t)
    for t in data:
        g.add(t)
    before = len(g)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics, axiomatic_triples=False, datatype_axioms=False).expand(g)
    inconsistent = [str(s) for s in g.subjects(RDF.type, OWL.Nothing)]
    errors = [str(o) for o in g.objects(None, URIRef("http://www.daml.org/2002/03/agents/agent-ont#error"))]
    examples = {
        "Laura Bassi is also a crm:E21_Person (owl:equivalentClass)":
            bool(ask(g, "ASK { lb:laura_bassi a crm:E21_Person }") and ask(g, "ASK { lb:laura_bassi a crm:E21_Person }")[0]),
        "Voltaire lbo:correspondedWith Laura Bassi (symmetric property)":
            bool(ask(g, "ASK { lb:voltaire lbo:correspondedWith lb:laura_bassi }")[0]),
        "Benedict XIV foaf:knows Laura Bassi (lbo:patronOf ⊑ foaf:knows)":
            bool(ask(g, "ASK { lb:benedict_xiv foaf:knows lb:laura_bassi }")[0]),
        "Bologna is a schema:Place (owl:equivalentClass)":
            bool(ask(g, "ASK { lb:bologna a schema:Place }")[0]),
        "The 1732 theses are a fabio:Expression (rdfs:subClassOf)":
            bool(ask(g, "ASK { lb:philosophica_studia a fabio:Expression }")[0]),
    }
    report["reasoning"] = {"asserted": before, "after_closure": len(g), "inferred": len(g) - before,
                           "inconsistencies": inconsistent + errors, "expected_inferences": examples}

    # output ---------------------------------------------------------------------
    ok = all(c["ok"] for c in report["checks"]) and not (inconsistent or errors) and all(examples.values())
    report["ok"] = ok
    (ROOT / "docs" / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = ["# Validation of the RDF dataset", "",
             f"Generated by `scripts/validate.py` on `data/laura_bassi.ttl` ({report['triples']} triples) "
             "and `models/ontology.ttl`.", "",
             f"**Result: {'all checks passed' if ok else 'some checks failed'}.**", "",
             "## Structure and domain/range", "", "| Check | Result |", "|---|---|"]
    for c in report["checks"]:
        lines.append(f"| {c['check']} | {'✓' if c['ok'] else '✗ ' + '; '.join(c['failures'])} |")
    lines += ["", "## Authority control (links to Wikidata)", "", "| Class | Resources | Linked to Wikidata |", "|---|---|---|"]
    for cls, v in report["authority"].items():
        lines.append(f"| {cls} | {v['total']} | {v['wikidata']} |")
    r = report["reasoning"]
    lines += ["", "## OWL 2 RL reasoning (owlrl)", "",
              f"- Asserted triples (ontology + data): {r['asserted']}",
              f"- After the deductive closure: {r['after_closure']} ({r['inferred']} inferred)",
              f"- Inconsistencies: {len(r['inconsistencies']) or 'none'}", "",
              "| Expected inference | Found |", "|---|---|"]
    for k, v in examples.items():
        lines.append(f"| {k} | {'✓' if v else '✗'} |")
    (ROOT / "docs" / "validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
