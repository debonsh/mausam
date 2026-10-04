#!/usr/bin/env python3
"""Build the SIH26076 idea-submission deck (official 6-slide template + our fill).

Usage: python3 build.py
Needs: network (template download, first run), soffice on PATH.
Output: SIH26076-idea-6slides.pdf next to this script.
Stdlib only. No invented statistics anywhere in the deck.
"""
import re
import shutil
import struct
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
TEMPLATE_URL = "https://www.sih.gov.in/letters/2026/SIH2026-IDEA-Presentation-Format.pptx"
EVIDENCE = HERE.parent / "evidence"

TEXTS = {
    1: [
        ("Problem Statement ID \u2013", "Problem Statement ID \u2013 SIH26076"),
        ("Problem Statement Title-", "Personalised homepage for the Mausam mobile application"),
        ("Theme-", "Theme \u2013 Smart Automation"),
        ("PS Category- Software/Hardware", "PS Category \u2013 Software"),
        ("Team ID-", "Team ID \u2013 [as registered on the portal]"),
        ("Team Name (Registered on portal)", "Team Name \u2013 [to be filled before upload]"),
    ],
    2: [
        ("IDEA TITLE", "Mausam home: actions with proof"),
        ("Detailed explanation of the proposed solution",
         "Decision stack on a map + bottom sheet"),
        (" How it addresses the problem",
         " Every value shows source, station and age"),
        ("Innovation and uniqueness of the solution ",
         "Honest gaps; labelled adapters; planner"),
    ],
    3: [
        ("Technologies to be used (e.g. programming languages, frameworks, hardware)",
         "Vanilla PWA; offline-first, age always shown"),
        ("Methodology and process for implementation (Flow Charts/Images/ working prototype)",
         "Deterministic engine with byte-identical replay"),
    ],
    4: [
        ("Analysis of the feasibility of the idea",
         "Mock runs on real IMD captures; keyed API needs the host"),
        ("Potential challenges and risks",
         "CPCB reachability, undocumented fields, iOS push limits"),
        ("Strategies", "Labelled fallbacks; stated grain; Android demo + inbox"),
        (" for overcoming these challenges", ""),
    ],
    5: [
        ("Potential impact on the target audience",
         "Actions with evidence, not bare charts"),
        ("Benefits of the solution (social, economic, environmental, etc.)",
         "Lineage, replay and gap cards are the moat"),
    ],
}

REFERENCES = [
    "IMD API reference + portal user guide (key, hourly JWT, static IP): api.imd.gov.in",
    "CPCB real-time AQI (GODL): data.gov.in; XKDR India Air Quality DB (CC BY 4.0)",
    "Copernicus CAMS atmosphere data store: ads.atmosphere.copernicus.eu",
    "MeitY UX4G design system; PIB Mausam note; Pai et al. 2014 rainfall climatology",
    "Mock, fixtures, replay tests: Mausam/app, docs/evidence",
]

# slide -> [(png path, x, y, w)]; h follows the PNG aspect. Inches.
IMAGES = {
    2: [(EVIDENCE / "ticket-02-engine-hero.png", 10.6, 2.55, 1.9)],
    3: [(EVIDENCE / "ticket-04-provenance.png", 10.7, 1.45, 2.0)],
    5: [],
}

EMU = 914400


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(26)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", path
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def pic_xml(pic_id, rid, x, y, w, h):
    return (
        f'<p:pic><p:nvPicPr><p:cNvPr id="{pic_id}" name="mock{pic_id}"/>'
        "<p:cNvPicPr><a:picLocks noChangeAspect=\"1\"/></p:cNvPicPr></p:nvPicPr>"
        f"<p:blipFill><a:blip r:embed=\"{rid}\"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>"
        f"<p:spPr><a:xfrm><a:off x=\"{x}\" y=\"{y}\"/><a:ext cx=\"{w}\" cy=\"{h}\"/>"
        "</a:xfrm><a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom></p:spPr></p:pic>"
    )


def set_run_text(slide_xml, old, new):
    old_e, new_e = escape(old), escape(new)
    pat = re.compile(r"(<a:t>)" + re.escape(old_e) + r"(</a:t>)")
    assert pat.search(slide_xml), f"run not found: {old!r}"
    return pat.sub(r"\1" + new_e + r"\2", slide_xml, count=1)


def main():
    work = HERE / "work"
    if work.exists():
        shutil.rmtree(work)
    (work / "tpl").mkdir(parents=True)
    tpl_zip = work / "template.pptx"
    if not tpl_zip.exists():
        print("downloading template…")
        req = urllib.request.Request(TEMPLATE_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r, open(tpl_zip, "wb") as f:
            shutil.copyfileobj(r, f)
    with zipfile.ZipFile(tpl_zip) as z:
        z.extractall(work / "tpl")
    root = work / "tpl"

    for num, pairs in TEXTS.items():
        p = root / f"ppt/slides/slide{num}.xml"
        xml = p.read_text(encoding="utf-8")
        for old, new in pairs:
            xml = set_run_text(xml, old, new)
        xml = xml.replace(escape("Your Team Name"), escape("[Team Name]"))
        p.write_text(xml, encoding="utf-8")

    # References: clone the single bullet paragraph.
    p6 = root / "ppt/slides/slide6.xml"
    xml6 = p6.read_text(encoding="utf-8")
    paras = re.findall(r"<a:p>.*?</a:p>", xml6, re.S)
    bullet = next(x for x in paras if "Details / Links" in x)
    fresh = "".join(
        re.sub(r"<a:t>.*?</a:t>", f"<a:t>{escape(r)}</a:t>", bullet, count=1)
        for r in REFERENCES
    )
    xml6 = xml6.replace(bullet, fresh, 1)
    xml6 = xml6.replace(escape("Your Team Name"), escape("[Team Name]"))
    p6.write_text(xml6, encoding="utf-8")

    # Images.
    media = root / "ppt/media"
    media.mkdir(exist_ok=True)
    diagram = HERE / "diagram.png"
    twoup = HERE / "honesty-twoup.png"
    assert diagram.exists() and twoup.exists(), "export diagram.png + honesty-twoup.png first (see ticket 07)"
    IMAGES[3].append((diagram, 0.7, 4.35, 5.6))
    IMAGES[5].append((twoup, 9.7, 1.45, 2.9))
    n = 0
    for num, specs in IMAGES.items():
        if not specs:
            continue
        sp = root / f"ppt/slides/slide{num}.xml"
        sxml = sp.read_text(encoding="utf-8")
        relsp = root / f"ppt/slides/_rels/slide{num}.xml.rels"
        rxml = relsp.read_text(encoding="utf-8")
        for src, x, y, w in specs:
            n += 1
            wpx, hpx = png_size(src)
            h = w * hpx / wpx
            shutil.copy(src, media / f"mock{n}.png")
            rid = f"rIdMock{n}"
            assert rid not in rxml
            rxml = rxml.replace(
                "</Relationships>",
                f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/mock{n}.png"/></Relationships>',
            )
            pic = pic_xml(100 + n, rid, int(x * EMU), int(y * EMU), int(w * EMU), int(h * EMU))
            assert "</p:spTree>" in sxml
            sxml = sxml.replace("</p:spTree>", pic + "</p:spTree>", 1)
        relsp.write_text(rxml, encoding="utf-8")
        sp.write_text(sxml, encoding="utf-8")

    # Drop the instruction slide (7): file, rel, sldId, content-type.
    (root / "ppt/slides/slide7.xml").unlink(missing_ok=True)
    (root / "ppt/slides/_rels/slide7.xml.rels").unlink(missing_ok=True)
    pres_rel = root / "ppt/_rels/presentation.xml.rels"
    pr = pres_rel.read_text(encoding="utf-8")
    m = re.search(r'<Relationship Id="(rId\d+)"[^>]*Target="slides/slide7.xml"', pr)
    assert m, "slide7 rel not found"
    pr = pr.replace(m.group(0), "")
    pres_rel.write_text(pr, encoding="utf-8")
    pres = root / "ppt/presentation.xml"
    px = pres.read_text(encoding="utf-8")
    px = re.sub(rf'<p:sldId[^>]*{m.group(1)}[^>]*/>', "", px)
    assert "slide7" not in px
    pres.write_text(px, encoding="utf-8")
    ct = root / "[Content_Types].xml"
    cx = ct.read_text(encoding="utf-8")
    cx = re.sub(r'<Override PartName="/ppt/slides/slide7.xml"[^>]*/>', "", cx)
    ct.write_text(cx, encoding="utf-8")

    out_pptx = HERE / "SIH26076-idea-6slides.pptx"
    with zipfile.ZipFile(out_pptx, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted((root).rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(root))
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(HERE), str(out_pptx)],
        check=True, capture_output=True,
    )
    pdf = HERE / "SIH26076-idea-6slides.pdf"
    assert pdf.exists(), "pdf conversion failed"
    print("wrote", pdf, pdf.stat().st_size, "bytes")


if __name__ == "__main__":
    sys.exit(main())
