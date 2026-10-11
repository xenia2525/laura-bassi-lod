"""XML/TEI → HTML: applies scripts/tei2html.xsl to data/laura_bassi.xml.

Usage (from the repository root):
    pip install lxml
    python scripts/tei2html.py
Output: output/laura_bassi.html
"""
from pathlib import Path
import lxml.etree as ET

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "laura_bassi.xml"
STYLESHEET = ROOT / "scripts" / "tei2html.xsl"
OUTPUT = ROOT / "output" / "laura_bassi.html"


def main():
    dom = ET.parse(str(SOURCE))
    transform = ET.XSLT(ET.parse(str(STYLESHEET)))
    result = transform(dom)
    for entry in transform.error_log:
        print("XSLT:", entry)
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_bytes(ET.tostring(result, pretty_print=True, method="html",
                                   doctype="<!DOCTYPE html>", encoding="UTF-8"))
    print(f"written {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
