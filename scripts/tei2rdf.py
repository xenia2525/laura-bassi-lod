"""XML/TEI → RDF for the Laura Bassi project.

Reads data/laura_bassi.xml and produces an RDF dataset that instantiates the
conceptual model (models/ontology.ttl) for every entity and relation encoded in
the TEI:

  listPerson/person   → foaf:Person        (+ birth/death dates, authority links)
  listOrg/org         → foaf:Organization
  listPlace/place     → crm:E53_Place
  listEvent/event     → crm:E5_Event       (+ dcterms:date)
  listBibl/bibl       → fabio:Thesis | fabio:Expression | fabio:Book | fabio:JournalArticle
  taxonomy/category   → skos:Concept       (+ skos:exactMatch to Wikidata and LCSH)
  text//q             → schema:Quotation
  sourceDesc/bibl     → foaf:Document      (+ schema:mentions every annotated entity)
  listRelation        → one triple per active/passive pair, using @ref as the property

Authority control: @sameAs and idno[@type='VIAF'|'LC'] → owl:sameAs.
Authors without a local entry get a URI minted from the MD5 hash of their name
(the approach used in the TESR lab).

Usage (from the repository root):
    pip install lxml rdflib
    python scripts/tei2rdf.py
Output: data/laura_bassi.ttl and data/laura_bassi.jsonld
"""
from pathlib import Path
import hashlib
import re

from lxml import etree
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, FOAF, OWL, RDF, RDFS, SKOS, XSD

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "laura_bassi.xml"
OUT_TTL = ROOT / "data" / "laura_bassi.ttl"
OUT_JSONLD = ROOT / "data" / "laura_bassi.jsonld"

LB = Namespace("https://xenia2525.github.io/laura-bassi-lod/resource/")
LBO = Namespace("https://xenia2525.github.io/laura-bassi-lod/ontology#")
SCHEMA = Namespace("https://schema.org/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
FABIO = Namespace("http://purl.org/spar/fabio/")
REL = Namespace("http://purl.org/vocab/relationship/")
DBO = Namespace("http://dbpedia.org/ontology/")

TEI = {"t": "http://www.tei-c.org/ns/1.0"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

BIBL_CLASS = {
    "thesis": FABIO.Thesis,
    "book": FABIO.Book,
    "journalArticle": FABIO.JournalArticle,
    "article": FABIO.Expression,
    "webPage": FOAF.Document,
}


def text(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip() if el is not None else None


def uri(pointer):
    """'#bologna' → lb:bologna"""
    return LB[pointer.lstrip("#")]


def minted(label):
    return LB[hashlib.md5(label.encode("utf-8")).hexdigest()]


def typed_date(value):
    """ISO value of @when → literal with the most precise XSD type."""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return Literal(value, datatype=XSD.date)
    if re.fullmatch(r"\d{4}-\d{2}", value):
        return Literal(value, datatype=XSD.gYearMonth)
    if re.fullmatch(r"\d{4}", value):
        return Literal(value, datatype=XSD.gYear)
    return Literal(value, datatype=XSD.dateTime)


def lang_of(el, default="en"):
    return el.get(XML_LANG) or default


def authority_links(g, subject, el):
    if el.get("sameAs"):
        g.add((subject, OWL.sameAs, URIRef(el.get("sameAs"))))
    for idno in el.findall("t:idno", TEI):
        if idno.get("type") in ("VIAF", "LC") and idno.text:
            g.add((subject, OWL.sameAs, URIRef(idno.text.strip())))


def build_graph(tree):
    g = Graph()
    for prefix, ns in [("lb", LB), ("lbo", LBO), ("schema", SCHEMA), ("crm", CRM), ("fabio", FABIO),
                       ("rel", REL), ("dbo", DBO), ("foaf", FOAF), ("dcterms", DCTERMS),
                       ("skos", SKOS), ("owl", OWL)]:
        g.bind(prefix, ns)

    # ---------------------------------------------------------------- people
    for p in tree.iterfind(".//t:standOff/t:listPerson/t:person", TEI):
        s = LB[p.get(XML_ID)]
        g.add((s, RDF.type, FOAF.Person))
        names = p.findall("t:persName", TEI)
        main = next((n for n in names if n.get("type") == "short"), names[0])
        g.add((s, RDFS.label, Literal(text(main), lang="en")))
        for n in names:
            g.add((s, FOAF.name, Literal(text(n))))
        for el, prop in (("t:birth", SCHEMA.birthDate), ("t:death", SCHEMA.deathDate)):
            event = p.find(el, TEI)
            if event is not None and event.get("when"):
                g.add((s, prop, typed_date(event.get("when"))))
        for occ in p.findall("t:occupation", TEI):
            g.add((s, SCHEMA.jobTitle, Literal(text(occ), lang="en")))
        authority_links(g, s, p)

    # ---------------------------------------------------------------- organisations
    for o in tree.iterfind(".//t:standOff/t:listOrg/t:org", TEI):
        s = LB[o.get(XML_ID)]
        g.add((s, RDF.type, FOAF.Organization))
        names = o.findall("t:orgName", TEI)
        g.add((s, RDFS.label, Literal(text(names[0]), lang=lang_of(names[0]))))
        for n in names[1:]:
            g.add((s, SKOS.altLabel, Literal(text(n), lang=lang_of(n))))
        authority_links(g, s, o)

    # ---------------------------------------------------------------- places
    for pl in tree.iterfind(".//t:standOff/t:listPlace/t:place", TEI):
        s = LB[pl.get(XML_ID)]
        g.add((s, RDF.type, CRM.E53_Place))
        names = pl.findall("t:placeName", TEI)
        g.add((s, RDFS.label, Literal(text(names[0]), lang=lang_of(names[0]))))
        for n in names[1:]:
            g.add((s, SKOS.altLabel, Literal(text(n), lang=lang_of(n))))
        authority_links(g, s, pl)

    # ---------------------------------------------------------------- events
    for ev in tree.iterfind(".//t:standOff/t:listEvent/t:event", TEI):
        s = LB[ev.get(XML_ID)]
        g.add((s, RDF.type, CRM.E5_Event))
        g.add((s, RDFS.label, Literal(text(ev.find("t:label", TEI)), lang="en")))
        if ev.get("when"):
            g.add((s, DCTERMS.date, typed_date(ev.get("when"))))

    # ---------------------------------------------------------------- works and bibliography
    for b in tree.iterfind(".//t:standOff/t:listBibl/t:bibl", TEI):
        s = LB[b.get(XML_ID)]
        g.add((s, RDF.type, BIBL_CLASS.get(b.get("type"), FABIO.Expression)))
        title = b.find("t:title", TEI)
        g.add((s, DCTERMS.title, Literal(text(title), lang=lang_of(title))))
        g.add((s, RDFS.label, Literal(text(title), lang=lang_of(title))))
        date = b.find("t:date", TEI)
        if date is not None and date.get("when"):
            g.add((s, DCTERMS.date, typed_date(date.get("when"))))
        for author in b.findall("t:author", TEI):
            if author.get("ref"):
                g.add((s, DCTERMS.creator, uri(author.get("ref"))))
            else:  # author without a local record: mint a URI from the name
                a = minted(text(author))
                g.add((a, RDF.type, FOAF.Person))
                g.add((a, RDFS.label, Literal(text(author))))
                g.add((s, DCTERMS.creator, a))
        journal = b.find("t:title[@level='j']", TEI)
        if journal is not None:
            j = minted(text(journal))
            g.add((j, RDF.type, FABIO.Journal))
            g.add((j, DCTERMS.title, Literal(text(journal))))
            g.add((j, RDFS.label, Literal(text(journal))))
            g.add((s, DCTERMS.isPartOf, j))
        for idno in b.findall("t:idno", TEI):
            if idno.get("type") == "DOI":
                g.add((s, OWL.sameAs, URIRef("https://doi.org/" + idno.text.strip())))
            elif idno.get("type") == "ISBN":
                g.add((s, DCTERMS.identifier, Literal("ISBN " + idno.text.strip())))
        if b.get("sameAs"):
            g.add((s, OWL.sameAs, URIRef(b.get("sameAs"))))

    # ---------------------------------------------------------------- concepts
    scheme = LB["subjects"]
    g.add((scheme, RDF.type, SKOS.ConceptScheme))
    g.add((scheme, RDFS.label, Literal("Subjects of the Laura Bassi project", lang="en")))
    for c in tree.iterfind(".//t:classDecl//t:category", TEI):
        s = LB[c.get(XML_ID)]
        g.add((s, RDF.type, SKOS.Concept))
        g.add((s, SKOS.inScheme, scheme))
        label = text(c.find("t:catDesc", TEI))
        g.add((s, SKOS.prefLabel, Literal(label, lang="en")))
        g.add((s, RDFS.label, Literal(label, lang="en")))
        for target in (c.get("sameAs"), c.get("corresp")):
            if target:
                g.add((s, SKOS.exactMatch, URIRef(target)))

    # ---------------------------------------------------------------- quotations
    for q in tree.iterfind(".//t:text//t:q", TEI):
        s = LB[q.get(XML_ID)]
        g.add((s, RDF.type, SCHEMA.Quotation))
        g.add((s, SCHEMA.text, Literal(text(q).strip('"'), lang="en")))
        g.add((s, RDFS.label, Literal("Quotation: " + text(q)[:60].strip('"') + "…", lang="en")))
        if q.get("who"):
            g.add((s, DCTERMS.creator, uri(q.get("who"))))

    # ---------------------------------------------------------------- the source document
    src_el = tree.find(".//t:sourceDesc/t:bibl", TEI)
    src = LB[src_el.get(XML_ID)]
    g.add((src, RDF.type, FOAF.Document))
    g.add((src, DCTERMS.title, Literal("Laura Bassi – Wikipedia", lang="en")))
    g.add((src, RDFS.label, Literal("Wikipedia page 'Laura Bassi'", lang="en")))
    g.add((src, DCTERMS.date, Literal(src_el.find("t:date", TEI).get("when"), datatype=XSD.dateTime)))
    g.add((src, FOAF.page, URIRef(src_el.find("t:ptr", TEI).get("target"))))
    g.add((src, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by-sa/4.0/")))
    for el in tree.iterfind(".//t:text//*[@ref]", TEI):
        if el.get("ref").startswith("#"):
            g.add((src, SCHEMA.mentions, uri(el.get("ref"))))

    # ---------------------------------------------------------------- relations
    for r in tree.iterfind(".//t:standOff/t:listRelation/t:relation", TEI):
        prop = URIRef(r.get("ref"))
        if r.get("mutual"):
            members = r.get("mutual").split()
            for a in members:
                for b in members:
                    if a != b:
                        g.add((uri(a), prop, uri(b)))
        else:
            for a in r.get("active").split():
                for b in r.get("passive").split():
                    g.add((uri(a), prop, uri(b)))

    return g


def main():
    tree = etree.parse(str(SOURCE))
    g = build_graph(tree)
    g.serialize(destination=str(OUT_TTL), format="turtle")
    g.serialize(destination=str(OUT_JSONLD), format="json-ld", indent=2)
    subjects = {s for s in g.subjects() if str(s).startswith(str(LB))}
    print(f"{len(g)} triples about {len(subjects)} resources")
    print(f"written {OUT_TTL.relative_to(ROOT)} and {OUT_JSONLD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
