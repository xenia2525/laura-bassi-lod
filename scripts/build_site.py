"""Builds the data used by the project website (index.html).

Reads the RDF dataset and the TEI/XSLT sources and writes assets/site-data.js,
which defines window.SITE = { graph, events, stats, snippets }.
Generating the data from the real files keeps the report in sync with them.

Usage (from the repository root):  python scripts/build_site.py
"""
from pathlib import Path
import json
import re

from lxml import etree
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
LB = "https://xenia2525.github.io/laura-bassi-lod/resource/"
SCHEMA = Namespace("https://schema.org/")
# descriptions and images retrieved from Wikidata / Wikimedia Commons (see docs/wikidata_cache.json)
CACHE = json.loads((ROOT / "docs" / "wikidata_cache.json").read_text(encoding="utf-8"))

TYPE_OF = {
    "http://xmlns.com/foaf/0.1/Person": "person",
    "http://xmlns.com/foaf/0.1/Organization": "org",
    "http://www.cidoc-crm.org/cidoc-crm/E53_Place": "place",
    "http://www.cidoc-crm.org/cidoc-crm/E5_Event": "event",
    "http://purl.org/spar/fabio/Thesis": "work",
    "http://purl.org/spar/fabio/Book": "work",
    "http://purl.org/spar/fabio/JournalArticle": "work",
    "http://purl.org/spar/fabio/Expression": "work",
    "http://purl.org/spar/fabio/Journal": "work",
    "http://www.w3.org/2004/02/skos/core#Concept": "concept",
    "https://schema.org/Quotation": "work",
    "http://xmlns.com/foaf/0.1/Document": "document",
}
SKIP_PROPS = {str(RDF.type), "https://schema.org/mentions", str(SKOS.inScheme)}


def curie(u):
    for prefix, ns in [("schema:", "https://schema.org/"), ("crm:", "http://www.cidoc-crm.org/cidoc-crm/"),
                       ("dcterms:", "http://purl.org/dc/terms/"), ("rel:", "http://purl.org/vocab/relationship/"),
                       ("dbo:", "http://dbpedia.org/ontology/"),
                       ("lbo:", "https://xenia2525.github.io/laura-bassi-lod/ontology#")]:
        if u.startswith(ns):
            return prefix + u[len(ns):]
    return u


def build_graph(g):
    nodes, edges = {}, []
    for s, _, t in g.triples((None, RDF.type, None)):
        if str(s).startswith(LB) and str(t) in TYPE_OF:
            sid = str(s)[len(LB):]
            if len(sid) == 32:  # authors/journals minted with md5: not shown in the orrery
                continue
            label = g.value(s, RDFS.label) or g.value(s, SKOS.prefLabel) or sid
            wd = next((str(o) for o in g.objects(s, OWL.sameAs) if "wikidata" in str(o)), None)
            wd = wd or next((str(o) for o in g.objects(s, SKOS.exactMatch) if "wikidata" in str(o)), None)
            node = {"id": sid, "label": str(label), "type": TYPE_OF[str(t)], "wikidata": wd}
            born, died = g.value(s, SCHEMA.birthDate), g.value(s, SCHEMA.deathDate)
            if born and died:
                node["dates"] = f"{str(born)[:4]}–{str(died)[:4]}"
            date = g.value(s, DCTERMS.date)
            if date and node["type"] in ("event", "work"):
                node["dates"] = str(date)[:10]
            jobs = sorted(str(j) for j in g.objects(s, SCHEMA.jobTitle))
            if jobs:
                node["role"] = ", ".join(jobs)
            cached = CACHE.get(wd.rsplit("/", 1)[-1], {}) if wd else {}
            if cached.get("description"):
                node["description"] = cached["description"]
            if cached.get("image"):
                im = cached["image"]
                name = im["file"].replace(" ", "_")
                node["image"] = {
                    "src": "https://commons.wikimedia.org/wiki/Special:FilePath/" + quote(name) + "?width=480",
                    "page": "https://commons.wikimedia.org/wiki/File:" + quote(name),
                    "credit": ", ".join(x for x in (im["artist"], im["date"]) if x) + f" ({im['license']})",
                }
            nodes[sid] = node
    for s, p, o in g:
        if str(p) in SKIP_PROPS or not isinstance(o, URIRef):
            continue
        a, b = str(s)[len(LB):], str(o)[len(LB):]
        if a in nodes and b in nodes and a != b:
            edges.append({"s": a, "t": b, "p": curie(str(p))})
    nodes.pop("source_page", None)
    edges = [e for e in edges if e["s"] in nodes and e["t"] in nodes]
    # one edge per unordered pair + property is enough for the drawing
    seen, unique = set(), []
    for e in edges:
        key = (frozenset((e["s"], e["t"])), e["p"])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return list(nodes.values()), unique


def build_events(g):
    q = """
    PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?e ?label ?date ?placeLabel ?byLabel
    WHERE {
      ?e a crm:E5_Event ; rdfs:label ?label ; dcterms:date ?date .
      OPTIONAL { ?e crm:P7_took_place_at/rdfs:label ?placeLabel }
      OPTIONAL { ?e crm:P14_carried_out_by/rdfs:label ?byLabel }
    }"""
    events = {}
    for r in g.query(q):
        ev = events.setdefault(str(r.e), {"id": str(r.e)[len(LB):], "label": str(r.label),
                                          "date": str(r.date), "place": [], "by": []})
        for key, val in (("place", r.placeLabel), ("by", r.byLabel)):
            if val is not None and str(val) not in ev[key]:
                ev[key].append(str(val))
    rows = [dict(e, place=", ".join(e["place"]), by=", ".join(e["by"])) for e in events.values()]
    return sorted(rows, key=lambda r: r["date"])


def snippet(path, start, end=None, max_lines=40):
    lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
    i = next(n for n, l in enumerate(lines) if start in l)
    j = next((n for n, l in enumerate(lines[i + 1:], i + 1) if end and end in l), i + max_lines)
    block = lines[i:j + 1]
    indent = min(len(l) - len(l.lstrip()) for l in block if l.strip())
    return "\n".join(l[indent:] for l in block)


def main():
    g = Graph().parse(ROOT / "data" / "laura_bassi.ttl")
    tei = etree.parse(str(ROOT / "data" / "laura_bassi.xml"))
    ns = {"t": "http://www.tei-c.org/ns/1.0"}
    nodes, edges = build_graph(g)
    ttl = (ROOT / "data" / "laura_bassi.ttl").read_text(encoding="utf-8")
    bassi_ttl = re.search(r"^lb:laura_bassi .*?\.\n", ttl, re.S | re.M).group(0)

    site = {
        "graph": {"nodes": nodes, "edges": edges},
        "events": build_events(g),
        "stats": {
            "annotations": int(tei.xpath("count(//t:body//*[@ref])", namespaces=ns)),
            "entities": len(tei.xpath("//t:standOff//*[@xml:id] | //t:category[@xml:id]", namespaces=ns)),
            "wikidata": len(tei.xpath("//*[@sameAs][starts-with(@sameAs,'http://www.wikidata.org')]", namespaces=ns)),
            "relations": len(tei.xpath("//t:relation", namespaces=ns)),
            "triples": len(g),
            "words": len(" ".join(tei.xpath("//t:body//text()", namespaces=ns)).split()),
        },
        "snippets": {
            "tei_text": snippet("data/laura_bassi.xml", '<p><rs type="event" ref="#academy_election_1732">', max_lines=0),
            "tei_person": snippet("data/laura_bassi.xml", '<person xml:id="laura_bassi"', "</person>"),
            "tei_relation": "\n".join([
                snippet("data/laura_bassi.xml", 'name="spouse"', max_lines=0),
                snippet("data/laura_bassi.xml", 'name="patronOf"', max_lines=0),
                snippet("data/laura_bassi.xml", 'active="#thesis_defence_1732" passive="#sala_anziani"', max_lines=0),
            ]),
            "xslt": snippet("scripts/tei2html.xsl", "<!-- annotated entities", "</xsl:template>"),
            "python_rdf": snippet("scripts/tei2rdf.py", "# ---------------------------------------------------------------- relations", "return g"),
            "ttl": bassi_ttl.strip(),
        },
    }
    validation = ROOT / "docs" / "validation.json"
    if validation.exists():
        site["validation"] = json.loads(validation.read_text(encoding="utf-8"))
    out = ROOT / "assets" / "site-data.js"
    out.parent.mkdir(exist_ok=True)
    out.write_text("window.SITE = " + json.dumps(site, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(f"written {out.relative_to(ROOT)}: {len(nodes)} nodes, {len(edges)} edges, {len(site['events'])} events")


if __name__ == "__main__":
    main()
