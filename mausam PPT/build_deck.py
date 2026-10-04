#!/usr/bin/env python3
"""SIH26076 final deck: edit the OFFICIAL template in place (stdlib only).

Reads:  mausam PPT/SIH2026-IDEA-Presentation-Format.pptx  (official, untouched)
Writes: mausam PPT/SIH26076-Mausam-FINAL.pptx            (6 slides, instruction slide dropped)

Rules honoured:
- 6-slide structure kept; every required pointer keeps its exact wording.
- Everything added is a native editable object (p:sp text boxes / shapes,
  p:pic pictures, rightArrow connectors). No flattened slides, no rasterized
  text. Screenshots are embedded as movable/resizable p:pic objects.
- Slide size, masters, footers, logos untouched.
- No invented statistics anywhere.
"""
import re
import shutil
import struct
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
TPL = HERE / "SIH2026-IDEA-Presentation-Format.pptx"
OUT = HERE / "SIH26076-Mausam-FINAL.pptx"
EV = Path(__file__).resolve().parent.parent / "Mausam" / "docs" / "evidence"

# Fill before upload (SIH portal values).
TEAM_ID = "195697"
TEAM_NAME = "Zencoderss"

EMU = 914400
NAVY = "003366"     # Mausam/IMD authority blue (our label, not a brand claim)
BLUE = "4F81BD"     # template accent1
LIGHT = "EAF1F8"    # card fill
PALE = "F2F2F2"
AMBER = "F79646"
GREEN = "9BBB59"
RED = "C0504D"
INK = "1A1A1A"
WHITE = "FFFFFF"
GREY = "595959"


def E(v):
    return int(round(v * EMU))


def run(t, sz=12, b=False, color=INK, font="Arial"):
    bb = ' b="1"' if b else ""
    # ECMA-376 order: solidFill BEFORE latin/ea/cs, else renderers drop it.
    return (
        f'<a:r><a:rPr lang="en-US" sz="{sz * 100}"{bb} dirty="0">'
        f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
        f'<a:latin typeface="{font}"/><a:ea typeface="{font}"/>'
        f'<a:cs typeface="{font}"/></a:rPr>'
        f"<a:t>{escape(t)}</a:t></a:r>"
    )


def para(runs, algn="l", marL=0):
    rs = "".join(runs)
    return (
        f'<a:p><a:pPr algn="{algn}" marL="{marL}">'
        '<a:lnSpc><a:spcPct val="100000"/></a:lnSpc></a:pPr>' + rs + "</a:p>"
    )


def shape(sid, name, geom, x, y, w, h, paras, fill=None, line=None,
          anchor="t", wrap="square", adj=None):
    """One native editable p:sp. paras = list of <a:p> strings."""
    fxml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
    lxml = (f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{line}"/>'
            "</a:solidFill></a:ln>" if line else '<a:ln><a:noFill/></a:ln>')
    adjx = f"<a:avLst>{adj}</a:avLst>" if adj else "<a:avLst/>"
    tx = "".join(paras)
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{escape(name)}"/>'
        '<p:cNvSpPr><a:spLocks noChangeAspect="0"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>'
        f"<p:spPr><a:xfrm><a:off x=\"{E(x)}\" y=\"{E(y)}\"/>"
        f"<a:ext cx=\"{E(w)}\" cy=\"{E(h)}\"/></a:xfrm>"
        f'<a:prstGeom prst="{geom}">{adjx}</a:prstGeom>{fxml}{lxml}</p:spPr>'
        f'<p:txBody><a:bodyPr anchor="{anchor}" wrap="{wrap}">'
        "<a:normAutofit/></a:bodyPr>"
        '<a:lstStyle/>' + tx + "</p:txBody></p:sp>"
    )


def label(sid, x, y, w, h, text, sz=10, b=True, color=NAVY, algn="l"):
    return shape(sid, "lbl", "rect", x, y, w, h,
                 [para([run(text, sz, b, color)], algn=algn)], fill=None)


def card(sid, x, y, w, h, title, lines, tsz=12, lsz=10, fill=WHITE,
         border="4F81BD", title_color=INK):
    ps = [para([run(title, tsz, True, title_color)])]
    for ln in lines:
        ps.append(para([run(ln, lsz, False, GREY if ln.startswith("(") else INK)]))
    return shape(sid, "card", "roundRect", x, y, w, h, ps,
                 fill=fill, line=border, anchor="t")


def arrow(sid, x, y, w, h, fill=BLUE):
    return shape(sid, "arr", "rightArrow", x, y, w, h, [EMPTY_PARA],
                 fill=fill, anchor="ctr")


def next_id(xml):
    return max(int(v) for v in re.findall(r'cNvPr id="(\d+)"', xml)) + 1


EMPTY_PARA = ('<a:p><a:pPr><a:lnSpc><a:spcPct val="100000"/></a:lnSpc>'
              '</a:pPr></a:p>')


def empty_shape(xml, name):
    """Blank the text of a shape (by cNvPr name) and collapse its frame.

    Used for the inherited pointer boxes whose zone the visuals take over.
    The exact pointer wording is re-emitted verbatim in compact labels, and
    the husk is parked invisible so it cannot overlap anything.
    """
    pat = re.compile(
        r'(<p:(?:sp|graphicFrame)\b(?:(?!</p:(?:sp|graphicFrame)>).)*?'
        r'<p:cNvPr id="\d+" name="' + re.escape(name) + r'".*?'
        r'<p:txBody>.*?<a:lstStyle/>)(.*?)'
        r'(</p:txBody>)', re.S)
    m = pat.search(xml)
    assert m, f"shape not found: {name}"
    xml = xml[:m.start(2)] + EMPTY_PARA + xml[m.end(2):]
    px = re.compile(
        r'(<p:cNvPr id="\d+" name="' + re.escape(name) + r'".*?'
        r'<a:xfrm><a:off x=")\d+(" y=")\d+(".*?'
        r'<a:ext cx=")\d+(" cy=")\d+(")', re.S)
    m2 = px.search(xml)
    assert m2, f"xfrm not found: {name}"
    xml = (xml[:m2.start()] +
           m2.group(1) + str(E(12.95)) + m2.group(2) + str(E(6.60)) +
           m2.group(3) + "100" + m2.group(4) + "100" +
           m2.group(5) + xml[m2.end():])
    return xml


def remove_shape(xml, name):
    """Delete a whole p:sp / p:pic element by cNvPr name (template art)."""
    pat = re.compile(
        r'<p:(?:sp|pic)\b(?:(?!</p:(?:sp|pic)>).)*?'
        r'<p:cNvPr id="\d+" name="' + re.escape(name) + r'".*?'
        r'</p:(?:sp|pic)>', re.S)
    m = pat.search(xml)
    assert m, f"shape not found for removal: {name}"
    return xml[:m.start()] + xml[m.end():]


def move_shape(xml, name, x=None, y=None):
    """Move a template shape's frame (keeps its text/styles untouched)."""
    pat = re.compile(
        r'(<p:cNvPr id="\d+" name="' + re.escape(name) + r'".*?'
        r'<a:off x=")\d+(" y=")\d+(")', re.S)
    m = pat.search(xml)
    assert m, f"xfrm not found for move: {name}"
    full = m.group(0)
    if x is not None:
        full = re.sub(r'<a:off x="\d+"', f'<a:off x="{E(x)}"', full)
    if y is not None:
        full = re.sub(r'y="\d+"', f'y="{E(y)}"', full, count=1)
    return xml[:m.start()] + full + xml[m.end():]


def set_run_size(xml, needle, sz):
    """Set sz (in points*100 units below: pass e.g. 2000) of the run
    containing needle text. Operates per <a:r> element."""
    out = []
    pos = 0
    changed = False
    for m in re.finditer(r"<a:r>.*?</a:r>", xml, re.S):
        frag = m.group(0)
        if f"<a:t>{escape(needle)}</a:t>" in frag or f"<a:t>{needle}</a:t>" in frag:
            frag = re.sub(r'sz="\d+"', f'sz="{sz}"', frag, count=1)
            changed = True
        out.append(xml[pos:m.start()])
        out.append(frag)
        pos = m.end()
    out.append(xml[pos:])
    assert changed, f"run not found for resize: {needle!r}"
    return "".join(out)


def png_size(path):
    d = Path(path).read_bytes()
    assert d[:8] == b"\x89PNG\r\n\x1a\n", f"not a PNG: {path}"
    w, h = struct.unpack(">II", d[16:24])
    return w, h


class Slide:
    def __init__(self, root, num, media_counter):
        self.num = num
        self.p = root / f"ppt/slides/slide{num}.xml"
        self.rels_p = root / f"ppt/slides/_rels/slide{num}.xml.rels"
        self.xml = self.p.read_text(encoding="utf-8")
        self.rels = self.rels_p.read_text(encoding="utf-8")
        self.sid = next_id(self.xml)
        self.root = root
        self.media_counter = media_counter  # shared list [n]

    def add(self, frag):
        assert "</p:spTree>" in self.xml
        self.xml = self.xml.replace("</p:spTree>", frag + "</p:spTree>", 1)

    def box(self, *a, **k):
        self.sid += 1
        self.add(shape(self.sid, *a, **k))

    def text(self, old, new):
        pat = re.compile(r"(<a:t>)" + re.escape(escape(old)) + r"(</a:t>)")
        assert pat.search(self.xml), f"run not found: {old!r}"
        self.xml = pat.sub(r"\1" + escape(new) + r"\2", self.xml, count=1)

    def pic(self, name, src, x, y, w, h=None):
        """Embed a PNG as an editable, movable p:pic (keeps aspect if h=None)."""
        iw, ih = png_size(src)
        if h is None:
            h = w * ih / iw
        self.media_counter[0] += 1
        fname = f"image{self.media_counter[0]}.png"
        (self.root / "ppt" / "media" / fname).write_bytes(Path(src).read_bytes())
        rids = [int(v) for v in re.findall(r'Id="rId(\d+)"', self.rels)]
        rid = f"rId{max(rids) + 1}"
        self.rels = self.rels.replace(
            "</Relationships>",
            f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org'
            f'/officeDocument/2006/relationships/image" Target="../media/{fname}"/>'
            "</Relationships>", 1)
        self.sid += 1
        frag = (
            f'<p:pic><p:nvPicPr><p:cNvPr id="{self.sid}" name="{escape(name)}"/>'
            '<p:cNvPicPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/>'
            '<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/>'
            f'<a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm>'
            '<a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>'
            '<a:noFill/><a:ln><a:noFill/></a:ln></p:spPr></p:pic>'
        )
        self.add(frag)
        return h

    def save(self):
        self.p.write_text(self.xml, encoding="utf-8")
        self.rels_p.write_text(self.rels, encoding="utf-8")


# ---------------------------------------------------------------- title page
def slide1(root, media):
    s = Slide(root, 1, media)
    pairs = [
        ("Problem Statement ID \u2013", "Problem Statement ID \u2013 SIH26076"),
        ("Problem Statement Title-",
         "Personalised homepage for the Mausam mobile application"),
        ("Theme-", "Theme \u2013 Smart Automation"),
        ("PS Category- Software/Hardware", "PS Category \u2013 Software"),
        ("Team ID-", f"Team ID \u2013 {TEAM_ID}"),
        ("Team Name (Registered on portal)",
         f"Team Name \u2013 {TEAM_NAME}"),
    ]
    for old, new in pairs:
        s.text(old, new)
    # The template justifies these bullets (rivers + wrap collisions):
    # left-align, tighten to 85% spacing, shrink runs so the block ends
    # above our title.
    s.xml = s.xml.replace('algn="just"', 'algn="l"')
    s.xml = s.xml.replace(
        '<a:pPr marL="285750" indent="-285750" algn="l">',
        '<a:pPr marL="285750" indent="-285750" algn="l">'
        '<a:lnSpc><a:spcPct val="100000"/></a:lnSpc>'
        '<a:spcBef><a:spcPts val="0"/></a:spcBef>'
        '<a:spcAft><a:spcPts val="0"/></a:spcAft>')
    # The template sets 200% line spacing on these bullets: collapse it.
    s.xml = s.xml.replace(
        'indent="-285750" algn="l"><a:lnSpc><a:spcPct val="100000"/>'
        '</a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef>'
        '<a:spcAft><a:spcPts val="0"/></a:spcAft>'
        '<a:lnSpc><a:spcPct val="200000"/></a:lnSpc>',
        'indent="-285750" algn="l"><a:lnSpc><a:spcPct val="100000"/>'
        '</a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef>'
        '<a:spcAft><a:spcPts val="0"/></a:spcAft>')
    for needle in ("Problem Statement ID \u2013 SIH26076",
                   "Theme \u2013 Smart Automation",
                   "PS Category \u2013 Software",
                   f"Team ID \u2013 {TEAM_ID}",
                   f"Team Name \u2013 {TEAM_NAME}"):
        s.xml = set_run_size(s.xml, needle, 1700)
    # Long title must hold one line: 15pt guarantees it in this box.
    s.xml = set_run_size(
        s.xml, "Personalised homepage for the Mausam mobile application",
        1500)
    # Stock hexagon + lightbulb make room for the real product screenshot.
    s.xml = remove_shape(s.xml, "Picture 4")
    s.xml = remove_shape(s.xml, "Freeform: Shape 26")
    # Idea title below the field block, larger than any template bullet.
    s.box("accent", "rect", 0.67, 4.55, 5.60, 0.09, [EMPTY_PARA],
          fill=AMBER)
    s.box("ideatitle", "rect", 0.67, 4.68, 5.60, 0.55,
          [para([run("Mausam home: actions with proof", 28, True, NAVY,
                      "Times New Roman")])], fill=None)
    s.box("tagline", "rect", 0.67, 5.27, 5.60, 0.60,
          [para([run("Every number shows its source, station, issue time "
                      "and age. Every advisory can be re-derived by hand.",
                      12, False, GREY)])], fill=None)
    # Real product screenshot, right side (editable picture object).
    s.pic("productshot", EV / "mobile-home.png", 9.30, 0.55, 2.55, 5.55)
    s.box("shotcap", "rect", 9.05, 6.15, 3.05, 0.55,
          [para([run("Working prototype home (illustrative screenshot). "
                      "Map + action cards with IMD provenance on every "
                      "number.", 9, False, GREY)], algn="ctr")],
          fill=None)
    s.save()


# ------------------------------------------------------------------ hero (2)
def slide2(root, media):
    s = Slide(root, 2, media)
    s.text("Your Team Name", TEAM_NAME)
    # Pointer box inherits the full canvas: blank it (exact wording is
    # re-emitted verbatim in the compact labels below).
    s.xml = empty_shape(s.xml, "TextBox 8")
    # Idea title under the heading (heading box ends y=1.25; keep clear).
    s.box("ideatitle", "rect", 0.67, 1.32, 9.60, 0.34,
          [para([run("Mausam home: actions with proof", 22, True, NAVY,
                      "Times New Roman")])], fill=None)
    # Left column: exact pointer labels + concise fill (9pt caps labels).
    px, pw = 0.67, 3.85
    rows = [
        ("Proposed Solution (Describe your Idea/Solution/Prototype)",
         "A home screen that adapts to you: map on top, action cards below."),
        ("Detailed explanation of the proposed solution",
         "Onboarding picks your persona. The home reorders: the farmer sees "
         "sowing first, the commuter sees fog first."),
        ("How it addresses the problem",
         "Every card says what to do, shows the readings behind it, and "
         "names its source, station and age."),
        ("Innovation and uniqueness of the solution",
         "Source on every number. Replayable advice. Honest gaps where data "
         "is missing. A grounded bot that never invents numbers."),
    ]
    y = 1.72
    for head, body in rows:
        s.box("ptr", "rect", px, y, pw, 0.26,
              [para([run(head.upper(), 9, True, NAVY)])], fill=None)
        y += 0.26
        s.box("fill", "rect", px, y, pw, 0.52,
              [para([run(body, 11, False)])], fill=None)
        y += 0.62
    # Center: two REAL screenshots with a tap-to-prove caption strip.
    s.pic("shot-home", EV / "mobile-home.png", 4.75, 1.72, 1.85, 3.85)
    s.pic("shot-prov", EV / "ticket-04-provenance.png", 6.80, 1.72, 1.85, 3.85)
    s.box("shotcap", "rect", 4.70, 5.60, 4.00, 0.34,
          [para([run("number on screen \u2192 tap \u24d8 \u2192 source \u00b7 "
                      "station \u00b7 issue time \u00b7 age", 10, True, NAVY)],
                algn="ctr")],
          fill=None)
    # Right: 1 hero differentiator + 2 support (chatbot moved to slide 3).
    s.box("hero", "roundRect", 9.00, 1.72, 3.65, 1.25,
          [para([run("Source on every number", 13, True, NAVY)]),
           para([run("station + issue time + age on each reading; tap \u24d8 "
                      "for the full provenance sheet", 10, False, GREY)])],
          fill=LIGHT, line=AMBER, anchor="t")
    sup = [
        ("Advice you can replay", "same data \u2192 same card, byte-identical"),
        ("Honest gaps, no guesses", "no data \u2192 a gap card, never a zero"),
    ]
    dy = 3.10
    for t, d in sup:
        s.box("diff", "roundRect", 9.00, dy, 3.65, 0.95,
              [para([run(t, 11, True)]),
               para([run(d, 10, False, GREY)])],
              fill=LIGHT, line=BLUE, anchor="t")
        dy += 1.05
    # Hook banner, full width (the memorable sentence).
    s.box("hook", "roundRect", 0.67, 6.00, 11.98, 0.78,
          [para([run("Every number on this screen can tell you where it came "
                      "from, when it was issued, and how old it is. Every "
                      "advisory can be re-derived by hand.",
                      11, True, NAVY)], algn="ctr")],
          fill=LIGHT, line=NAVY, anchor="ctr")
    s.save()


# ------------------------------------------------------------ technical (3)
def slide3(root, media):
    s = Slide(root, 3, media)
    s.text("Your Team Name", TEAM_NAME)
    s.xml = empty_shape(s.xml, "TextBox 8")
    # Compact labels, exact pointer text.
    s.box("ptr1", "rect", 0.67, 1.22, 12.00, 0.28,
          [para([run("Technologies to be used (e.g. programming languages, "
                     "frameworks, hardware)", 10, True, NAVY)])], fill=None)
    # Pipeline: 6 boxes + 5 arrows. GATEWAY is the critical path: amber ring.
    steps = [
        ("IMD DATA", "28 keyed APIs\nWFS \u00b7 CAP feed", BLUE),
        ("\u2605 GATEWAY", "Static-IP host\nkey + hourly JWT", BLUE),
        ("FUSION", "Normalize\nCPCB AQI \u00b7 CAMS UV", BLUE),
        ("INTELLIGENCE", "Advisory + window\nengines \u00b7 replay", BLUE),
        ("BACKEND", "Bundle API\npush \u00b7 ledger", BLUE),
        ("HOMEPAGE", "Offline PWA\nEN/HI \u00b7 WCAG AA", NAVY),
    ]
    x, y0, bw, bh, gap = 0.45, 1.55, 1.78, 1.40, 0.30
    for i, (t, d, fill) in enumerate(steps):
        s.box("pipe", "roundRect", x, y0, bw, bh,
              [para([run(t, 12, True, WHITE)], algn="ctr"),
               para([run(d, 10, False, WHITE)], algn="ctr")],
              fill=fill, line=(AMBER if i == 1 else None), anchor="ctr")
        if i < 5:
            s.sid += 1
            s.add(arrow(s.sid, x + bw + 0.02, y0 + bh / 2 - 0.14, gap - 0.04,
                        0.28))
        x += bw + gap
    # Tech stack as chips under the stage they belong to (single axis).
    chips = ["Vanilla JS PWA", "Leaflet maps", "FastAPI",
             "Firebase auth + Web Push", "Grounded bot + templates"]
    cx = 0.45
    for c in chips:
        s.box("chip", "roundRect", cx, 3.05, 2.32, 0.40,
              [para([run(c, 10, False)], algn="ctr")],
              fill=PALE, line="BBBBBB", anchor="ctr")
        cx += 2.44
    # Methodology pointer (verbatim), then a 3-stage timeline diagram.
    s.box("ptr2", "rect", 0.67, 3.55, 7.60, 0.30,
          [para([run("Methodology and process for implementation (Flow Charts/"
                     "Images/ working prototype)", 10, True, NAVY)])], fill=None)
    stages = [
        ("Mock today", "real captures\n32 tests green"),
        ("Live pipeline", "keyed APIs\nstatic IP + JWT"),
        ("Finale", "3 personas \u00b7 push\nlabelled adapters"),
    ]
    mx = 0.67
    for i, (t, d) in enumerate(stages):
        s.box("stage", "roundRect", mx, 3.90, 2.30, 1.00,
              [para([run(t, 11, True, WHITE)], algn="ctr"),
               para([run(d, 9, False, WHITE)], algn="ctr")],
              fill=NAVY if i == 0 else BLUE, anchor="ctr")
        if i < 2:
            s.sid += 1
            s.add(arrow(s.sid, mx + 2.32, 4.26, 0.34, 0.28, fill=GREEN))
        mx += 2.68
    # Replay loop + what-AI-does two-up.
    s.box("replay", "roundRect", 0.67, 5.05, 4.00, 0.95,
          [para([run("REPLAY  logged inputs \u2192 rule chain \u2192 "
                      "byte-identical card \u21ba", 10, True, NAVY)],
                algn="ctr")],
          fill=LIGHT, line=NAVY, anchor="ctr")
    s.box("ainote", "roundRect", 4.80, 5.05, 3.47, 0.95,
          [para([run("AI only where justified: grounded bot + template "
                      "fallback. No model invents weather.", 10, False, INK)],
                algn="ctr")],
          fill=LIGHT, line=GREEN, anchor="ctr")
    # Working prototype screenshot, right (template permits it here).
    s.box("protohead", "rect", 8.60, 3.55, 4.05, 0.30,
          [para([run("Working prototype (illustrative screenshot)", 10, True,
                      NAVY)], algn="ctr")], fill=None)
    s.pic("shot-proto", EV / "ticket-02-engine-hero.png", 9.55, 3.90, 1.35,
          2.60)
    s.box("protocap", "rect", 8.60, 6.52, 4.05, 0.28,
          [para([run("replay reproduces this card byte-identically",
                      9, False, GREY)], algn="ctr")], fill=None)
    s.save()


# ----------------------------------------------------------- feasibility (4)
def slide4(root, media):
    s = Slide(root, 4, media)
    s.text("Your Team Name", TEAM_NAME)
    s.xml = empty_shape(s.xml, "TextBox 8")
    s.box("feas", "rect", 0.67, 1.22, 12.00, 0.58,
          [para([run("Analysis of the feasibility of the idea", 10, True,
                      NAVY)]),
           para([run("The mock runs offline on real captured IMD payloads. "
                      "32 tests green. Each risk below has a working "
                      "fallback.", 12, False)])],
          fill=None)
    rows = [
        ("Keyed API needs a static-IP host",
         "Run on saved captures + public WFS meanwhile"),
        ("CPCB feed may be unreachable",
         "Labelled mirror fallback, else an honest gap card"),
        ("Some IMD fields are undocumented",
         "Documented fallbacks; the screen states its data grain"),
        ("iOS limits push alerts",
         "Demo on Android; the inbox keeps every alert"),
    ]
    y = 1.84
    s.box("h1", "rect", 0.67, y, 5.85, 0.32,
          [para([run("Potential challenges and risks", 10, True, NAVY)],
                algn="l")], fill=None)
    s.box("h2", "rect", 6.85, y, 5.80, 0.32,
          [para([run("Strategies for overcoming these challenges", 10, True,
                      NAVY)], algn="l")], fill=None)
    y += 0.34
    for ch, fix in rows:
        s.box("ch", "roundRect", 0.67, y, 5.55, 0.66,
              [para([run(ch, 11, False)])], fill=PALE, line=RED, anchor="ctr")
        s.sid += 1
        s.add(arrow(s.sid, 6.28, y + 0.19, 0.50, 0.28, fill=GREEN))
        s.box("fix", "roundRect", 6.85, y, 5.80, 0.66,
              [para([run(fix, 11, False)])], fill=LIGHT, line=GREEN,
               anchor="ctr")
        y += 0.78
    # Feasibility timeline across the freed band.
    tl = [("Day 1", "static-IP host\n+ key registration"), ("Week 1", "captured-payload\nmock (done)"),
          ("Week 3", "live keyed\npipeline"), ("Finale", "demo: 3 personas\npush + adapters")]
    tx = 0.67
    for i, (t, d) in enumerate(tl):
        s.box("tl", "roundRect", tx, 5.42, 2.78, 0.62,
              [para([run(t + "  \u00b7  " + d.replace("\n", " "), 10, True,
                          WHITE)], algn="ctr")],
              fill=AMBER if i == 0 else BLUE, anchor="ctr")
        if i < 3:
            s.sid += 1
            s.add(arrow(s.sid, tx + 2.80, 5.63, 0.30, 0.20, fill=GREY))
        tx += 3.12
    # Viability strip (the header promises it).
    s.box("viab", "roundRect", 0.67, 6.12, 11.98, 0.66,
          [para([run("Viability: one container on a static-IP VM \u00b7 one "
                      "IMD API account (2 DEV + 2 PROD keys, attribution "
                      "ledger on request) \u00b7 no paid services \u00b7 IMD "
                      "data with attribution; CPCB/CAMS labelled adapters.",
                      10, False, INK)], algn="ctr")],
          fill=LIGHT, line=NAVY, anchor="ctr")
    s.save()


# ---------------------------------------------------------------- impact (5)
def slide5(root, media):
    s = Slide(root, 5, media)
    s.text("Your Team Name", TEAM_NAME)
    s.xml = empty_shape(s.xml, "TextBox 8")
    s.box("imp", "rect", 0.67, 1.22, 9.00, 0.35,
          [para([run("Potential impact on the target audience", 10, True,
                      NAVY)])], fill=None)
    # Persona -> action -> measurable outcome (deep personas, no filler).
    rows = [
        ("Commuter", "Fog window + \u201cleave 20 min early\u201d",
         "time to state the action"),
        ("Farmer", "Agromet + sowing window,\nrainfall vs normal",
         "action recalled after 5 min"),
        ("Health", "Heat card + \u201cIMD does not\npublish pollen\u201d",
         "% reading the gap as a gap"),
    ]
    y = 1.62
    for p, act, meas in rows:
        s.box("per", "roundRect", 0.67, y, 2.00, 0.95,
              [para([run(p, 12, True, WHITE)], algn="ctr")], fill=NAVY,
              anchor="ctr")
        s.sid += 1
        s.add(arrow(s.sid, 2.73, y + 0.33, 0.40, 0.28, fill=AMBER))
        s.box("act", "roundRect", 3.19, y, 3.10, 0.95,
              [para([run(act, 11, False)], algn="ctr")], fill=WHITE,
              line=BLUE, anchor="ctr")
        s.sid += 1
        s.add(arrow(s.sid, 6.35, y + 0.33, 0.40, 0.28, fill=AMBER))
        s.box("meas", "roundRect", 6.81, y, 2.80, 0.95,
              [para([run("we measure:", 9, True, GREY)], algn="ctr"),
               para([run(meas, 10, False, INK)], algn="ctr")],
              fill=LIGHT, line=GREEN, anchor="ctr")
        y += 1.08
    # Offline + Hindi proof screenshot.
    s.pic("shot-hi", EV / "ticket-21-onboarding-language-hi.png",
          9.95, 1.62, 1.70, 3.30)
    s.box("hicap", "rect", 9.75, 4.95, 2.10, 0.50,
          [para([run("Hindi onboarding +\noffline shell (illustrative)",
                      9, False, GREY)], algn="ctr")], fill=None)
    # Benefits pointer (verbatim) + honest measurement line.
    s.box("ben", "rect", 0.67, 5.55, 11.98, 1.15,
          [para([run("Benefits of the solution (social, economic, "
                      "environmental, etc.)", 10, True, NAVY)]),
           para([run("Warning text is human-reviewed, never raw machine "
                      "translation. No invented statistics: impact is measured "
                      "in the pilot \u2014 can users state the action, how "
                      "fast, does every card replay.", 11, False)])],
          fill=None)
    s.save()


# -------------------------------------------------------------- references (6)
def slide6(root, media):
    s = Slide(root, 6, media)
    s.text("Your Team Name", TEAM_NAME)
    # Pull the title up so the top half is usable (wording untouched).
    s.xml = move_shape(s.xml, "Title 1", y=0.30)
    s.xml = move_shape(s.xml, "TextBox 8", x=12.95, y=6.60)
    # Source-map tiles across the top.
    tiles = [
        ("IMD", "official \u00b7 keyed API"),
        ("CPCB", "official \u00b7 labelled adapter"),
        ("Copernicus", "official \u00b7 labelled"),
        ("MeitY UX4G", "design standard"),
        ("Our mock", "32 tests \u00b7 replay"),
    ]
    tx = 0.67
    for t, d in tiles:
        s.box("tile", "roundRect", tx, 1.05, 2.32, 0.72,
              [para([run(t, 11, True, WHITE)], algn="ctr"),
               para([run(d, 9, False, WHITE)], algn="ctr")],
              fill=NAVY if t in ("IMD", "Our mock") else BLUE, anchor="ctr")
        tx += 2.44
    refs = [
        ("IMD API reference + portal user guide (key, hourly JWT, static IP)",
         "api.imd.gov.in"),
        ("CPCB real-time AQI, GODL", "data.gov.in"),
        ("Copernicus CAMS atmosphere data store",
         "ads.atmosphere.copernicus.eu"),
        ("MeitY UX4G design system + PIB Mausam note (2023)",
         "ux4g.gov.in \u00b7 pib.gov.in"),
        ("Pai, N. et al. (2014), IMD Pune gridded rainfall 0.25\u00b0",
         "published dataset"),
        ("Mausam app: existing Damini lightning + Meghdoot crop modules",
         "mausam.imd.gov.in"),
        ("Working mock, fixtures, replay tests (32 pass)",
         "submission folder Mausam/docs/evidence (illustrative)"),
    ]
    y = 1.90
    for i, (t, link) in enumerate(refs, 1):
        s.box("ref", "roundRect", 0.67, y, 11.98, 0.62,
              [para([run(f"{i}.  {t}", 10, False),
                     run(f"  {link}", 10, False, BLUE)])],
              fill=PALE if i % 2 else WHITE,
              line="CCCCCC", anchor="t")
        y += 0.68
    s.save()


def drop_instruction_slide(root):
    (root / "ppt/slides/slide7.xml").unlink(missing_ok=True)
    (root / "ppt/slides/_rels/slide7.xml.rels").unlink(missing_ok=True)
    pr = root / "ppt/_rels/presentation.xml.rels"
    txt = pr.read_text(encoding="utf-8")
    m = re.search(r'<Relationship Id="(rId\d+)"[^>]*Target="slides/slide7.xml"',
                  txt)
    assert m, "slide7 rel not found"
    pr.write_text(txt.replace(m.group(0), ""), encoding="utf-8")
    px = root / "ppt/presentation.xml"
    pxt = px.read_text(encoding="utf-8")
    pxt = re.sub(rf'<p:sldId[^>]*{m.group(1)}[^>]*/>', "", pxt)
    assert "slide7" not in pxt
    px.write_text(pxt, encoding="utf-8")
    ct = root / "[Content_Types].xml"
    cxt = ct.read_text(encoding="utf-8")
    cxt = re.sub(r'<Override PartName="/ppt/slides/slide7.xml"[^>]*/>', "",
                 cxt)
    ct.write_text(cxt, encoding="utf-8")


def main():
    assert TPL.exists(), f"template missing: {TPL}"
    for ev in ["mobile-home.png", "ticket-04-provenance.png",
               "ticket-02-engine-hero.png",
               "ticket-21-onboarding-language-hi.png"]:
        assert (EV / ev).exists(), f"evidence missing: {ev}"
    work = HERE / "build_tmp"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    with zipfile.ZipFile(TPL) as z:
        z.extractall(work)
    # template ships image1+image2 -> next embedded image is image3.
    media = [2]
    slide1(work, media)
    slide2(work, media)
    slide3(work, media)
    slide4(work, media)
    slide5(work, media)
    slide6(work, media)
    drop_instruction_slide(work)
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(work.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(work))
    shutil.rmtree(work)
    print("wrote", OUT, OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    sys.exit(main())
