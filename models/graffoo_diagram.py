"""Draw the conceptual model of the project in Graffoo notation (SVG).

Graffoo conventions (https://essepuntato.it/graffoo/):
  class            yellow rectangle, solid border
  datatype         green rhomboid, solid border
  object property  blue line, filled circle at the domain, filled arrow at the range
  data property    green line, empty circle at the domain, empty arrow at the range
  class axiom      black labelled arrow (e.g. rdfs:subClassOf)
  additional axioms light-blue folded box with Manchester syntax
  ontology         transparent box with dotted border and light-blue heading

Run:  python models/graffoo_diagram.py   ->  models/conceptual_model_graffoo.svg
"""
from pathlib import Path
import math

W, H = 1760, 1300
FONT = "Helvetica, Arial, sans-serif"
BLUE, GREEN, BLACK = "#1f4fbf", "#2b8a3e", "#222"

# ---------------------------------------------------------------- nodes
# id: (label, kind, x, y)   kind: class | datatype
NODES = {
    "P":   ("foaf:Person", "class", 760, 560),
    "P2":  ("foaf:Person", "class", 760, 170),
    "O":   ("foaf:Organization", "class", 1390, 330),
    "PL":  ("crm:E53_Place", "class", 1390, 800),
    "EV":  ("crm:E5_Event", "class", 760, 1000),
    "EX":  ("fabio:Expression", "class", 250, 560),
    "TH":  ("fabio:Thesis", "class", 95, 370),
    "BK":  ("fabio:Book", "class", 245, 370),
    "JA":  ("fabio:JournalArticle", "class", 420, 370),
    "JO":  ("fabio:Journal", "class", 420, 230),
    "Q":   ("schema:Quotation", "class", 300, 120),
    "CO":  ("skos:Concept", "class", 250, 1000),
    "DOC": ("foaf:Document", "class", 530, 1210),
    "D1":  ("xsd:date", "datatype", 470, 720),
    "D2":  ("xsd:date", "datatype", 1100, 1130),
    "L1":  ("rdfs:Literal", "datatype", 80, 700),
    "L2":  ("rdfs:Literal", "datatype", 90, 120),
}

# ---------------------------------------------------------------- edges
# (from, to, label, kind, bend, label_t, label_dy)
#   kind: obj | data | axiom ; bend = perpendicular offset of the control point
EDGES = [
    # Person <-> Person (drawn between two copies of foaf:Person)
    ("P", "P2", "schema:spouse", "obj", -480, .3, 0),
    ("P", "P2", "schema:colleague", "obj", -330, .5, 30),
    ("P", "P2", "rel:mentorOf", "obj", -110, .5, 0),
    ("P", "P2", "lbo:patronOf", "obj", 110, .5, 30),
    ("P", "P2", "lbo:correspondedWith", "obj", 330, .5, 0),
    ("P", "P2", "lbo:precededBy", "obj", 480, .3, 0),
    # Person -> Organization / Place
    ("P", "O", "schema:memberOf", "obj", 0, .55, 0),
    ("P", "PL", "schema:birthPlace", "obj", -240, .55, 0),
    ("P", "PL", "schema:deathPlace", "obj", -80, .55, 0),
    ("P", "PL", "dbo:restingPlace", "obj", 80, .55, 0),
    ("P", "PL", "schema:nationality", "obj", 240, .55, 0),
    ("O", "PL", "schema:location", "obj", 0, .5, 0),
    ("PL", "PL", "crm:P89_falls_within", "loop", 0, 0, 0),
    # Event
    ("EV", "P", "crm:P11_had_participant", "obj", 0, .5, 0),
    ("EV", "O", "crm:P14_carried_out_by", "obj", 120, .8, 0),
    ("EV", "PL", "crm:P7_took_place_at", "obj", 0, .5, 0),
    ("EV", "EX", "crm:P16_used_specific_object", "obj", -120, .55, 0),
    ("EV", "CO", "dcterms:subject", "obj", 0, .5, 0),
    # Works
    ("EX", "P", "dcterms:creator", "obj", 0, .5, 0),
    ("EX", "CO", "dcterms:subject", "obj", 0, .5, 0),
    ("JA", "JO", "dcterms:isPartOf", "obj", 0, .5, 0),
    ("Q", "P2", "dcterms:creator", "obj", -40, .5, 0),
    ("Q", "P2", "schema:about", "obj", 40, .5, 0),
    ("P", "CO", "schema:knowsAbout", "obj", -150, .45, 0),
    ("DOC", "CO", "dcterms:subject", "obj", 0, .5, 0),
    ("DOC", "P", "dcterms:subject", "obj", 0, .2, 0),
    # data properties
    ("P", "D1", "schema:birthDate", "data", -40, .5, 0),
    ("P", "D1", "schema:deathDate", "data", 40, .5, 0),
    ("EX", "D1", "dcterms:date", "data", 0, .55, 0),
    ("EV", "D2", "dcterms:date", "data", 0, .5, 0),
    ("EX", "L1", "dcterms:title", "data", 0, .5, 0),
    ("Q", "L2", "schema:text", "data", 0, .5, 0),
    # class axioms
    ("TH", "EX", "rdfs:subClassOf", "axiom", 0, .3, 0),
    ("BK", "EX", "rdfs:subClassOf", "axiom", 0, .62, 0),
    ("JA", "EX", "rdfs:subClassOf", "axiom", 0, .3, 0),
]

# additional axioms (Manchester syntax): (x, y, lines)
AXIOMS = [
    (30, 1225, ["Class: foaf:Person", "  EquivalentTo: crm:E21_Person"]),
    (1250, 160, ["Class: foaf:Organization", "  EquivalentTo: crm:E74_Group"]),
    (1250, 905, ["Class: crm:E53_Place", "  EquivalentTo: schema:Place"]),
    (1000, 20, ["ObjectProperty: lbo:patronOf",
                "  SubPropertyOf: foaf:knows",
                "ObjectProperty: lbo:correspondedWith",
                "  Characteristics: Symmetric",
                "  SubPropertyOf: foaf:knows",
                "ObjectProperty: lbo:precededBy",
                "  SubPropertyOf: dcterms:relation"]),
    (30, 1130, ["Every individual is linked to authority files:",
                 "  owl:sameAs  → Wikidata, VIAF",
                 "  skos:exactMatch → LCSH (concepts)"]),
]

PREFIXES = [
    "lbo:     <https://xenia2525.github.io/laura-bassi-lod/ontology#>",
    "foaf:    <http://xmlns.com/foaf/0.1/>",
    "schema:  <https://schema.org/>",
    "crm:     <http://www.cidoc-crm.org/cidoc-crm/>",
    "fabio:   <http://purl.org/spar/fabio/>",
    "skos:    <http://www.w3.org/2004/02/skos/core#>",
    "dcterms: <http://purl.org/dc/terms/>",
    "rel:     <http://purl.org/vocab/relationship/>",
    "dbo:     <http://dbpedia.org/ontology/>",
    "xsd:     <http://www.w3.org/2001/XMLSchema#>",
]

# ---------------------------------------------------------------- geometry
def size(label, kind):
    w = max(96, 7.6 * len(label) + 24)
    return (w + 16, 34) if kind == "datatype" else (w, 36)


def boundary(nid, tx, ty):
    """Point on the border of node nid in the direction of (tx, ty)."""
    label, kind, x, y = NODES[nid]
    w, h = size(label, kind)
    dx, dy = tx - x, ty - y
    if dx == 0 and dy == 0:
        return x, y
    s = min((w / 2) / abs(dx) if dx else 1e9, (h / 2) / abs(dy) if dy else 1e9)
    return x + dx * s, y + dy * s


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size_=12, anchor="middle", weight="normal", fill="#111", halo=True):
    halo_attr = 'paint-order="stroke" stroke="#fff" stroke-width="4" stroke-linejoin="round"' if halo else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size_}" '
            f'text-anchor="{anchor}" font-weight="{weight}" fill="{fill}" {halo_attr}>{esc(t)}</text>')


# ---------------------------------------------------------------- drawing
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       """<defs>
  <marker id="objEnd" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#1f4fbf"/></marker>
  <marker id="objStart" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7"><circle cx="5" cy="5" r="4" fill="#1f4fbf"/></marker>
  <marker id="dataEnd" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="10" markerHeight="10" orient="auto-start-reverse"><path d="M1,1 L9,5 L1,9 z" fill="#fff" stroke="#2b8a3e" stroke-width="1.4"/></marker>
  <marker id="dataStart" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="8" markerHeight="8"><circle cx="5" cy="5" r="3.6" fill="#fff" stroke="#2b8a3e" stroke-width="1.4"/></marker>
  <marker id="axEnd" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#222"/></marker>
</defs>""",
       f'<rect width="{W}" height="{H}" fill="#fff"/>']

# ontology box
out.append(f'<rect x="12" y="12" width="{W-24}" height="{H-24}" fill="none" stroke="#333" stroke-dasharray="2 4" stroke-width="1.5"/>')
out.append(f'<rect x="12" y="12" width="560" height="30" fill="#cfe2ff" stroke="#333" stroke-dasharray="2 4"/>')
out.append(text(24, 32, "Ontology: https://xenia2525.github.io/laura-bassi-lod/ontology", 13, "start", "bold", halo=False))

# edges first (so nodes are drawn on top)
for a, b, label, kind, bend, lt, ldy in EDGES:
    color = {"obj": BLUE, "data": GREEN, "axiom": BLACK, "loop": BLUE}[kind]
    if kind == "loop":
        _, k, x, y = NODES[a]
        w, h = size(NODES[a][0], k)
        sx, sy = x + w / 2, y - 8
        ex, ey = x + w / 2, y + 8
        out.append(f'<path d="M{sx},{sy} C{sx+90},{sy-70} {ex+90},{ey+70} {ex},{ey}" fill="none" stroke="{BLUE}" '
                   f'stroke-width="1.6" marker-start="url(#objStart)" marker-end="url(#objEnd)"/>')
        out.append(text(sx + 78, y + 4, label, 12, "start", fill=BLUE))
        continue
    _, _, x1, y1 = NODES[a]
    _, _, x2, y2 = NODES[b]
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    L = math.hypot(x2 - x1, y2 - y1)
    nx, ny = -(y2 - y1) / L, (x2 - x1) / L
    cx, cy = mx + nx * bend, my + ny * bend
    sx, sy = boundary(a, cx, cy)
    ex, ey = boundary(b, cx, cy)
    marks = {"obj": ('url(#objStart)', 'url(#objEnd)'),
             "data": ('url(#dataStart)', 'url(#dataEnd)'),
             "axiom": ('none', 'url(#axEnd)')}[kind]
    out.append(f'<path d="M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}" fill="none" stroke="{color}" '
               f'stroke-width="1.6" marker-start="{marks[0]}" marker-end="{marks[1]}"/>')
    t = lt
    lx = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cx + t ** 2 * ex
    ly = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy + t ** 2 * ey + ldy
    out.append(text(lx, ly + 4, label, 12, weight="bold" if kind == "axiom" else "normal", fill=color))

# nodes
for nid, (label, kind, x, y) in NODES.items():
    w, h = size(label, kind)
    if kind == "class":
        out.append(f'<rect x="{x-w/2:.1f}" y="{y-h/2:.1f}" width="{w:.1f}" height="{h}" fill="#fff3a6" stroke="#111" stroke-width="1.4"/>')
    else:
        k = 10
        pts = f"{x-w/2+k},{y-h/2} {x+w/2},{y-h/2} {x+w/2-k},{y+h/2} {x-w/2},{y+h/2}"
        out.append(f'<polygon points="{pts}" fill="#b7e4c7" stroke="#111" stroke-width="1.4"/>')
    out.append(text(x, y + 4.5, label, 13, weight="bold", halo=False))

# additional axioms (folded light-blue boxes)
for x, y, lines in AXIOMS:
    w = max(len(l) for l in lines) * 7.2 + 24
    h = len(lines) * 17 + 14
    f = 12
    out.append(f'<path d="M{x},{y} h{w-f} l{f},{f} v{h-f} h{-w} z" fill="#dbeafe" stroke="#333" stroke-width="1"/>')
    out.append(f'<path d="M{x+w-f},{y} v{f} h{f}" fill="none" stroke="#333" stroke-width="1"/>')
    for i, l in enumerate(lines):
        out.append(f'<text x="{x+10}" y="{y+22+i*17}" font-family="Menlo, Consolas, monospace" font-size="12" fill="#111" xml:space="preserve">{esc(l)}</text>')

# prefixes box
px, py = 1225, 1015
pw, ph = 515, len(PREFIXES) * 16 + 34
out.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#fff" stroke="#333"/>')
out.append(f'<rect x="{px}" y="{py}" width="{pw}" height="22" fill="#eee" stroke="#333"/>')
out.append(text(px + 10, py + 16, "Prefixes", 12, "start", "bold", halo=False))
for i, p in enumerate(PREFIXES):
    out.append(f'<text x="{px+10}" y="{py+40+i*16}" font-family="Menlo, Consolas, monospace" font-size="11" fill="#111" xml:space="preserve">{esc(p)}</text>')

# legend
lx, ly = 1225, 1225
out.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+50}" y2="{ly}" stroke="{BLUE}" stroke-width="1.6" marker-start="url(#objStart)" marker-end="url(#objEnd)"/>')
out.append(text(lx + 60, ly + 4, "object property", 12, "start", halo=False))
out.append(f'<line x1="{lx+180}" y1="{ly}" x2="{lx+230}" y2="{ly}" stroke="{GREEN}" stroke-width="1.6" marker-start="url(#dataStart)" marker-end="url(#dataEnd)"/>')
out.append(text(lx + 240, ly + 4, "data property", 12, "start", halo=False))
out.append(f'<line x1="{lx+350}" y1="{ly}" x2="{lx+400}" y2="{ly}" stroke="{BLACK}" stroke-width="1.6" marker-end="url(#axEnd)"/>')
out.append(text(lx + 410, ly + 4, "class axiom", 12, "start", halo=False))
out.append(text(lx, ly + 30, "Graffoo notation · the two foaf:Person boxes are the same class", 11, "start", fill="#555", halo=False))

out.append("</svg>")
dest = Path(__file__).with_name("conceptual_model_graffoo.svg")
dest.write_text("\n".join(out), encoding="utf-8")
print("written", dest)
