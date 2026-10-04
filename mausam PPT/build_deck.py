#!/usr/bin/env python3
"""SIH26076 final deck: edit the OFFICIAL template in place (stdlib only).

Reads:  mausam PPT/SIH2026-IDEA-Presentation-Format.pptx  (official, untouched)
Writes: mausam PPT/SIH26076-Mausam-FINAL.pptx            (6 slides, instruction slide dropped)

Design language mirrors the team's Canva reference deck (pills, chips, black-
bordered pastel panels, yellow caption chips, red/blue word emphasis) while
staying inside the official SIH template: masters, footers, SIH logo, six
slides, and every required pointer word-for-word.

Everything added is a native editable object (p:sp / p:pic / rightArrow).
No flattened slides, no rasterized text, no invented statistics.
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
EV = HERE.parent / "Mausam" / "docs" / "evidence"

TEAM_ID = "195697"
TEAM_NAME = "Zencoderss"
DEMO = ("https://mausam-sih26076-devanshdhangar70-7520s-projects"
        ".vercel.app/")
DEMO_QR = HERE / "demo-qr.png"

EMU = 914400
NAVY = "003366"        # authority navy (pills, chips)
BLUE = "4F81BD"        # template accent1
PANEL = "D9EAFB"       # light-blue panel (reference deck)
PINK = "FBE1EE"        # pink panel (reference deck)
PINKCHIP = "E5399A"
GREEN = "2E9E4F"       # reference green pill
GREENBR = "5AAA46"
YELLOW = "F6E43B"      # highlight caption chip
AMBER = "F79646"
ORANGE = "F26522"
ORANGE2 = "D9480F"     # deep orange panel (white text passes contrast)
RED = "D92B2B"         # red lead-in emphasis
BLUEKEY = "1A44E8"     # blue key-phrase emphasis
LIGHT = "EAF1F8"
PALE = "F2F2F2"
INK = "1A1A1A"
WHITE = "FFFFFF"
GREY = "595959"
BLACK = "000000"

PILLFONT = "Arial Black"
BODYFONT = "Arial"
SW = 13.333            # slide width, inches


def E(v):
    return int(round(v * EMU))


def run(t, sz=12, b=False, color=INK, font=BODYFONT, u=None):
    bb = ' b="1"' if b else ""
    uu = f' u="{u}"' if u else ""
    # ECMA-376 order: solidFill BEFORE latin/ea/cs, else renderers drop it.
    return (
        f'<a:r><a:rPr lang="en-US" sz="{int(sz * 100)}"{bb}{uu} dirty="0">'
        f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
        f'<a:latin typeface="{font}"/><a:ea typeface="{font}"/>'
        f'<a:cs typeface="{font}"/></a:rPr>'
        f"<a:t>{escape(t)}</a:t></a:r>"
    )


def para(runs, algn="l", spc_aft=None):
    rs = "".join(runs)
    aft = (f'<a:spcAft><a:spcPts val="{int(spc_aft * 100)}"/></a:spcAft>'
           if spc_aft else "")
    return (
        f'<a:p><a:pPr algn="{algn}">'
        '<a:lnSpc><a:spcPct val="100000"/></a:lnSpc>' + aft +
        "</a:pPr>" + rs + "</a:p>"
    )


def shape(sid, name, geom, x, y, w, h, paras, fill=None, line=None,
          anchor="t", wrap="square", adj=None, lw=12700):
    fxml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
    lxml = (f'<a:ln w="{lw}"><a:solidFill><a:srgbClr val="{line}"/>'
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


STADIUM = '<a:gd name="adj" fmla="val 50000"/>'


def arrow(sid, x, y, w, h, fill=BLUE):
    return shape(sid, "arr", "rightArrow", x, y, w, h, [EMPTY_PARA],
                 fill=fill, anchor="ctr")


def next_id(xml):
    return max(int(v) for v in re.findall(r'cNvPr id="(\d+)"', xml)) + 1


EMPTY_PARA = ('<a:p><a:pPr><a:lnSpc><a:spcPct val="100000"/></a:lnSpc>'
              '</a:pPr></a:p>')


def empty_shape(xml, name):
    """Blank a shape's text and park its frame as a 100x100 EMU husk."""
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
    pat = re.compile(
        r'<p:(?:sp|pic)\b(?:(?!</p:(?:sp|pic)>).)*?'
        r'<p:cNvPr id="\d+" name="' + re.escape(name) + r'".*?'
        r'</p:(?:sp|pic)>', re.S)
    m = pat.search(xml)
    assert m, f"shape not found for removal: {name}"
    return xml[:m.start()] + xml[m.end():]


def png_size(path):
    d = Path(path).read_bytes()
    assert d[:8] == b"\x89PNG\r\n\x1a\n", f"not a PNG: {path}"
    w, h = struct.unpack(">II", d[16:24])
    return w, h


def cw(text, sz=8):
    """Approximate chip width for a single-line label."""
    return 0.066 * (sz / 8.0) * len(text) + 0.44


class Slide:
    def __init__(self, root, num, media_counter):
        self.num = num
        self.p = root / f"ppt/slides/slide{num}.xml"
        self.rels_p = root / f"ppt/slides/_rels/slide{num}.xml.rels"
        self.xml = self.p.read_text(encoding="utf-8")
        self.rels = self.rels_p.read_text(encoding="utf-8")
        self.sid = next_id(self.xml)
        self.root = root
        self.media_counter = media_counter

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

    def team(self):
        """Team-name oval: widen it and shrink the run so 'Zencoderss'
        stays on one line (the template's 14-char placeholder wrapped)."""
        m = re.search(r"<p:sp>(?:(?!</p:sp>).)*?<a:t>Your Team Name</a:t>"
                      r".*?</p:sp>", self.xml, re.S)
        assert m, "team oval not found"
        blk = m.group(0)
        blk = re.sub(r'<a:ext cx="\d+" cy="\d+"/>',
                     f'<a:ext cx="{E(1.95)}" cy="{E(0.88)}"/>', blk, count=1)
        blk = blk.replace(
            '<a:rPr lang="en-US" dirty="0"/>',
            '<a:rPr lang="en-US" sz="1100" dirty="0">'
            '<a:solidFill><a:srgbClr val="003366"/></a:solidFill></a:rPr>', 1)
        blk = blk.replace("<a:t>Your Team Name</a:t>",
                          f"<a:t>{escape(TEAM_NAME)}</a:t>", 1)
        self.xml = self.xml[:m.start()] + blk + self.xml[m.end():]

    def heading(self, title, fill, title_names):
        """Blank the inherited serif heading, draw a Canva-style pill."""
        for n in title_names:
            self.xml = empty_shape(self.xml, n)
        w = 0.25 * len(title) + 1.0
        x = (SW - w) / 2
        self.box("heading_pill", "roundRect", x, 0.18, w, 0.74,
                 [para([run(title, 24, True, WHITE, PILLFONT)], algn="ctr")],
                 fill=fill, anchor="ctr", adj=STADIUM)

    def chip(self, x, y, w, h, text, fill=NAVY, sz=8, color=WHITE,
             border=None, lw=12700, algn="ctr"):
        self.box("chip", "roundRect", x, y, w, h,
                 [para([run(text, sz, True, color)], algn=algn)],
                 fill=fill, line=border, anchor="ctr", adj=STADIUM, lw=lw)

    def panel(self, x, y, w, h, paras, fill=PANEL, border=BLACK, lw=19050,
              anchor="t"):
        self.box("panel", "roundRect", x, y, w, h, paras, fill=fill,
                 line=border, anchor=anchor, lw=lw)

    def pic(self, name, src, x, y, w, h=None, border=BLACK):
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
        ln = (f'<a:ln w="19050"><a:solidFill><a:srgbClr val="{border}"/>'
              "</a:solidFill></a:ln>" if border else "<a:ln><a:noFill/></a:ln>")
        frag = (
            f'<p:pic><p:nvPicPr><p:cNvPr id="{self.sid}" name="{escape(name)}"/>'
            '<p:cNvPicPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/>'
            '<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/>'
            f'<a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm>'
            '<a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>'
            f"<a:noFill/>{ln}</p:spPr></p:pic>"
        )
        self.add(frag)
        return h

    def save(self):
        self.p.write_text(self.xml, encoding="utf-8")
        self.rels_p.write_text(self.rels, encoding="utf-8")


def caption(s, x, y, w, text, sz=7.5, fill=YELLOW):
    """Yellow highlight caption chip (reference deck's screenshot labels)."""
    s.chip(x, y, w, 0.32, text, fill=fill, sz=sz, color=BLACK)


# ---------------------------------------------------------------- title page
def slide1(root, media):
    s = Slide(root, 1, media)
    # Template scaffolding out: 'TITLE PAGE' + the inherited serif banner.
    # Re-emitted below as a navy pill (identical wording).
    s.xml = empty_shape(s.xml, "Subtitle 3")
    s.heading("SMART INDIA HACKATHON 2026", NAVY, ["Title 7"])
    s.xml = empty_shape(s.xml, "TextBox 9")   # fields re-emitted below
    # Template decorations (bulb freeform + cropped watermark) are ghost art
    # behind the fields panel; keep the locked white Rectangle 24.
    s.xml = remove_shape(s.xml, "Freeform: Shape 26")
    s.xml = remove_shape(s.xml, "Picture 4")

    # Fields panel: red labels + navy values (reference deck's title layout).
    s.panel(0.66, 2.15, 8.30, 2.50,
            [para([run("Problem Statement ID \u2013 ", 15, True, RED),
                   run("SIH26076", 15, True, NAVY)]),
             para([run("Problem Statement Title \u2013 ", 15, True, RED),
                   run("Personalised homepage for the Mausam mobile "
                       "application", 15, True, NAVY)]),
             para([run("Theme \u2013 ", 15, True, RED),
                   run("Smart Automation", 15, True, NAVY)]),
             para([run("PS Category \u2013 ", 15, True, RED),
                   run("Software", 15, True, NAVY)]),
             para([run("Team ID \u2013 ", 15, True, RED),
                   run(TEAM_ID, 15, True, NAVY)]),
             para([run("Team Name \u2013 ", 15, True, RED),
                   run(TEAM_NAME, 15, True, NAVY)]),
             para([run("Organisation \u2013 ", 15, True, RED),
                   run("Ministry of Earth Sciences (IMD)", 15, True, NAVY)])],
            fill=PALE, lw=19050)

    s.box("accent", "rect", 0.66, 4.88, 8.30, 0.09, [EMPTY_PARA], fill=AMBER)
    s.box("ideatitle", "rect", 0.66, 5.02, 8.30, 0.60,
          [para([run("Mausam home: actions with proof", 30, True, NAVY,
                     PILLFONT)])], fill=None)
    s.box("tagline", "rect", 0.66, 5.66, 8.30, 0.62,
          [para([run("Every number shows its source, station, issue time and "
                     "age. Every advisory can be re-derived by hand.",
                     13, False, GREY)])], fill=None)

    s.pic("productshot", EV / "mobile-home.png", 9.40, 1.25, 2.45, 5.30)
    caption(s, 9.15, 6.60, 2.95,
            "WORKING PROTOTYPE \u00b7 HOME (ILLUSTRATIVE)", sz=7)
    # Live demo: QR + URL (bottom-left, the block's only free band).
    s.pic("demoqr", DEMO_QR, 0.66, 6.34, 0.58, 0.58, border=None)
    s.box("demolink", "rect", 1.38, 6.34, 7.58, 0.58,
          [para([run("LIVE DEMO   ", 10, True, NAVY, PILLFONT),
                 run(DEMO, 9, True, BLUEKEY, u="sng")]),
           para([run("Guest-first PWA \u00b7 works offline \u00b7 English and "
                     "Hindi", 8.5, False, GREY)])], fill=None)
    s.save()


# ------------------------------------------------------------------ hero (2)
def slide2(root, media):
    s = Slide(root, 2, media)
    s.team()
    s.xml = empty_shape(s.xml, "TextBox 8")
    s.heading("IDEA TITLE", GREEN, ["Title 1"])
    s.box("ideatitle", "rect", 0.67, 1.00, 12.00, 0.34,
          [para([run("Mausam home: actions with proof", 16, True, NAVY,
                     PILLFONT)], algn="ctr")], fill=None)

    # Left column: exact pointer wording as navy chips + light-blue panels.
    px, pw = 0.67, 4.25
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
    y = 1.55
    for head, body in rows:
        s.chip(px, y, min(cw(head, 7.5), pw), 0.28, head, sz=7.5)
        s.panel(px, y + 0.30, pw, 0.68,
                [para([run(body, 9.5, False, INK)])], fill=PANEL)
        y += 1.12

    # Center: two real screenshots, black frames + yellow caption chips.
    s.pic("shot-home", EV / "mobile-home.png", 5.15, 1.55, 1.70, 3.68)
    s.pic("shot-prov", EV / "ticket-04-provenance.png", 7.05, 1.55, 1.70, 3.68)
    caption(s, 5.15, 5.30, 1.70, "HOME \u00b7 MAP + ACTIONS", sz=7)
    caption(s, 7.05, 5.30, 1.70, "TAP \u24d8 \u2192 PROVENANCE", sz=7)

    # Right: hero differentiator + support cards + persona chips.
    rx, rw = 9.00, 3.65
    s.panel(rx, 1.55, rw, 1.30,
            [para([run("Source on every number", 13, True, WHITE)]),
             para([run("station + issue time + age on each reading; tap "
                       "\u24d8 for the full provenance sheet", 9.5, False,
                       WHITE)])],
            fill=NAVY, border=NAVY)
    sup = [("Advice you can replay", "same data \u2192 same card, byte-identical"),
           ("Honest gaps, no guesses", "no data \u2192 a gap card, never a zero")]
    dy = 3.02
    for t, d in sup:
        s.panel(rx, dy, rw, 1.00,
                [para([run(t, 11, True, INK)]),
                 para([run(d, 9.5, False, GREY)])], fill=PANEL)
        dy += 1.14
    s.chip(rx, 5.44, rw, 0.34,
           "PERSONAS  \u00b7  Commuter \u00b7 Farmer \u00b7 Health",
           fill=PINKCHIP, sz=8)

    # Hook banner: the memorable sentence, white on navy.
    s.panel(0.67, 6.18, 11.98, 0.70,
            [para([run("Every number on this screen can tell you where it "
                       "came from, when it was issued, and how old it is. "
                       "Every advisory can be re-derived by hand.",
                       11, True, WHITE)], algn="ctr")],
            fill=NAVY, border=NAVY, anchor="ctr")
    s.save()


# ------------------------------------------------------------ technical (3)
def slide3(root, media):
    s = Slide(root, 3, media)
    s.team()
    s.xml = empty_shape(s.xml, "TextBox 8")
    s.heading("TECHNICAL APPROACH", NAVY, ["Title 1"])
    s.chip(0.67, 1.02, 7.60, 0.34,
           "Technologies to be used (e.g. programming languages, "
           "frameworks, hardware)", sz=8)

    # Pipeline: 6 boxes + 5 arrows. GATEWAY = critical path (amber ring).
    # Left column only (ends 8.34) so the prototype column at 8.60 stays clear.
    steps = [
        ("IMD DATA", "28 keyed APIs\nWFS \u00b7 CAP feed", BLUE),
        ("\u2605 GATEWAY", "Static-IP host\nkey + hourly JWT", BLUE),
        ("FUSION", "Normalize\nCPCB AQI \u00b7 CAMS UV", BLUE),
        ("INTELLIGENCE", "Advisory + window\nengines \u00b7 replay", BLUE),
        ("BACKEND", "Bundle API\npush \u00b7 ledger", BLUE),
        ("HOMEPAGE", "Offline PWA\nEN/HI \u00b7 WCAG AA", NAVY),
    ]
    x, y0, bw, bh, gap = 0.42, 1.52, 1.17, 1.40, 0.18
    for i, (t, d, fill) in enumerate(steps):
        s.box("pipe", "roundRect", x, y0, bw, bh,
              [para([run(t, 8 if len(t) > 10 else 10, True, WHITE)],
                    algn="ctr"),
               para([run(d, 8.5, False, WHITE)], algn="ctr")],
              fill=fill, line=(AMBER if i == 1 else BLACK),
              anchor="ctr", lw=(28575 if i == 1 else 12700))
        if i < 5:
            s.sid += 1
            s.add(arrow(s.sid, x + bw + 0.02, y0 + bh / 2 - 0.14, gap - 0.04,
                        0.28))
        x += bw + gap

    # Tech chips directly under the stage they belong to.
    chips = ["Vanilla JS PWA", "Leaflet maps", "FastAPI",
             "Firebase auth + Web Push", "Grounded bot + templates"]
    cx = 0.42
    for c in chips:
        s.chip(cx, 3.00, 1.50, 0.38, c, fill=PANEL, sz=7.5, color=INK,
               border=BLACK, lw=19050)
        cx += 1.605

    s.chip(0.67, 3.48, 7.60, 0.34,
           "Methodology and process for implementation (Flow Charts/"
           "Images/ working prototype)", sz=8)

    # 3-stage methodology timeline (the template asks for a flow chart).
    stages = [
        ("Mock today", "real captures\n32 tests green"),
        ("Live pipeline", "keyed APIs\nstatic IP + JWT"),
        ("Finale", "3 personas \u00b7 push\nlabelled adapters"),
    ]
    mx = 0.67
    for i, (t, d) in enumerate(stages):
        s.box("stage", "roundRect", mx, 3.90, 2.30, 0.95,
              [para([run(t, 11, True, WHITE)], algn="ctr"),
               para([run(d, 9, False, WHITE)], algn="ctr")],
              fill=NAVY if i == 0 else BLUE, line=BLACK, anchor="ctr",
              lw=12700)
        if i < 2:
            s.sid += 1
            s.add(arrow(s.sid, mx + 2.32, 4.24, 0.34, 0.28, fill=GREENBR))
        mx += 2.68

    # Replay loop + AI two-up (paired answers to "why is AI here").
    s.panel(0.67, 5.05, 3.90, 1.55,
            [para([run("REPLAY", 11, True, NAVY)], algn="ctr"),
             para([run("logged inputs \u2192 rule chain \u2192 "
                       "byte-identical card \u21ba", 10, False, INK)],
                  algn="ctr")],
            fill=YELLOW, border=BLACK, anchor="ctr", lw=19050)
    s.panel(4.77, 5.05, 3.55, 1.55,
            [para([run("AI only where justified", 11, True, NAVY)], algn="ctr"),
             para([run("grounded bot + template fallback. No model invents "
                       "weather.", 10, False, INK)], algn="ctr")],
            fill=PANEL, border=BLACK, anchor="ctr", lw=19050)

    # Working prototype + assistant preview, side by side (right column).
    s.chip(8.60, 1.02, 4.05, 0.34,
           "WORKING PROTOTYPE \u00b7 ASSISTANT DESIGN PREVIEW", fill=GREEN,
           sz=8)
    s.pic("shot-proto", EV / "ticket-02-engine-hero.png", 9.00, 1.52, 1.60,
          3.46)
    s.pic("shot-ai", EV / "mausam-ai-assistant.png", 10.75, 1.52, 1.47, 3.45)
    caption(s, 9.00, 5.06, 1.60, "BYTE-IDENTICAL REPLAY", sz=6.5)
    caption(s, 10.75, 5.06, 1.47, "MAUSAM[AI] \u00b7 DESIGN", sz=6.5)
    s.panel(8.60, 5.52, 4.05, 1.08,
            [para([run("Mock runs offline on captured IMD payloads; the "
                       "keyed gateway is the Day-1 critical path.",
                       9.5, False, INK)], algn="ctr")],
            fill=PANEL, border=BLACK, anchor="ctr", lw=19050)
    s.save()


# ----------------------------------------------------------- feasibility (4)
def slide4(root, media):
    s = Slide(root, 4, media)
    s.team()
    s.xml = empty_shape(s.xml, "TextBox 8")
    s.heading("FEASIBILITY AND VIABILITY", GREEN, ["Title 1"])
    s.chip(0.67, 1.02, 4.70, 0.34, "Analysis of the feasibility of the idea",
           sz=8)
    s.box("feas", "rect", 0.67, 1.44, 11.98, 0.32,
          [para([run("The mock runs offline on real captured IMD payloads. ",
                     11, False, INK),
                 run("32 tests green.", 11, True, GREEN),
                 run(" Each risk below has a working fallback.", 11, False,
                     INK)])], fill=None)

    s.chip(0.67, 1.86, 4.90, 0.34, "Potential challenges and risks", sz=8)
    s.chip(6.85, 1.86, 5.30, 0.34,
           "Strategies for overcoming these challenges", sz=8)

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
    y = 2.32
    for ch, fix in rows:
        s.panel(0.95, y, 5.35, 0.66,
                [para([run(ch, 10.5, False, INK)])], fill=PINK, border=RED,
                anchor="ctr", lw=19050)
        s.box("badge", "ellipse", 0.57, y + 0.14, 0.38, 0.38,
              [para([run("!", 13, True, WHITE)], algn="ctr")], fill=RED,
              anchor="ctr")
        s.sid += 1
        s.add(arrow(s.sid, 6.36, y + 0.19, 0.44, 0.28, fill=GREENBR))
        s.panel(6.85, y, 5.75, 0.66,
                [para([run(fix, 10.5, False, INK)])], fill=PANEL,
                border=GREENBR, anchor="ctr", lw=19050)
        s.box("badge", "ellipse", 6.47, y + 0.14, 0.38, 0.38,
              [para([run("\u2713", 13, True, WHITE)], algn="ctr")],
              fill=GREENBR, anchor="ctr")
        y += 0.78

    # Feasibility timeline (the critical path, named).
    tl = [("Day 1", "static-IP host + key registration"),
          ("Week 1", "captured-payload mock (done)"),
          ("Week 3", "live keyed pipeline"),
          ("Finale", "demo: 3 personas, push, adapters")]
    tx = 0.67
    for i, (t, d) in enumerate(tl):
        fill = ORANGE2 if i == 0 else NAVY
        s.box("tl", "roundRect", tx, 5.58, 2.78, 0.62,
              [para([run(t + "  \u00b7  " + d, 9.5, True, WHITE)],
                    algn="ctr")],
              fill=fill, line=BLACK, anchor="ctr", lw=12700)
        if i < 3:
            s.sid += 1
            s.add(arrow(s.sid, tx + 2.80, 5.79, 0.30, 0.20, fill=GREY))
        tx += 3.12

    # Viability: the yellow key-highlight box from the reference deck.
    s.panel(0.67, 6.30, 11.98, 0.62,
            [para([run("Viability: ", 10, True, RED),
                   run("one container on a static-IP VM \u00b7 one IMD API "
                       "account (2 DEV + 2 PROD keys, attribution ledger on "
                       "request) \u00b7 no paid services \u00b7 IMD data with "
                       "attribution; CPCB/CAMS labelled adapters.",
                       10, False, INK)], algn="ctr")],
            fill=YELLOW, border=BLACK, anchor="ctr", lw=19050)
    s.save()


# ---------------------------------------------------------------- impact (5)
def slide5(root, media):
    s = Slide(root, 5, media)
    s.team()
    s.xml = empty_shape(s.xml, "TextBox 8")
    s.heading("IMPACT AND BENEFITS", NAVY, ["Title 1"])

    # IMPACT: pointer chip + panel with the persona matrix.
    s.chip(0.67, 1.02, 5.10, 0.34,
           "Potential impact on the target audience", sz=8)
    s.panel(0.67, 1.46, 7.75, 2.60, [EMPTY_PARA], fill=PANEL)
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
        s.chip(0.85, y, 1.55, 0.70, p, sz=11)
        s.sid += 1
        s.add(arrow(s.sid, 2.50, y + 0.21, 0.38, 0.28, fill=ORANGE))
        s.panel(2.98, y, 2.55, 0.70,
                [para([run(act, 9.5, False, INK)], algn="ctr")],
                fill=WHITE, border=BLACK, anchor="ctr", lw=19050)
        s.sid += 1
        s.add(arrow(s.sid, 5.62, y + 0.21, 0.38, 0.28, fill=ORANGE))
        s.panel(6.10, y, 2.15, 0.70,
                [para([run("we measure:", 7.5, True, GREY)], algn="ctr"),
                 para([run(meas, 9, False, INK)], algn="ctr")],
                fill=WHITE, border=GREENBR, anchor="ctr", lw=19050)
        y += 0.82

    # BENEFITS: pointer chip + pink panel, red lead-ins (reference style).
    s.chip(0.67, 4.24, 7.75, 0.34,
           "Benefits of the solution (social, economic, environmental, etc.)",
           sz=8)
    benefits = [
        ("Earlier action: ", "each card states what to do and how fast."),
        ("Traceable trust: ", "every reading names source, station and age."),
        ("Works offline: ", "the home shell keeps the last forecast."),
        ("Hindi + English: ", "warning text is human-reviewed, never raw "
                              "machine translation."),
        ("Honest gaps: ", "missing data shows as a gap, never a fake zero."),
    ]
    s.panel(0.67, 4.68, 7.75, 2.24,
            [para([run("\u25cf  ", 11, True, PINKCHIP),
                   run(lead, 11, True, RED), run(rest, 11, False, INK)],
                  spc_aft=12)
             for lead, rest in benefits],
            fill=PINK, border=BLACK, lw=19050)

    # Right: Hindi/offline proof + the no-invented-numbers stance.
    s.pic("shot-hi", EV / "ticket-21-onboarding-language-hi.png",
          9.75, 1.46, 1.80, 3.90)
    caption(s, 8.65, 5.46, 4.00, "HINDI ONBOARDING \u00b7 OFFLINE SHELL",
            sz=7.5)
    s.panel(8.65, 5.88, 4.00, 1.04,
            [para([run("No invented statistics. Impact is measured in the "
                       "pilot.", 11, True, WHITE)], algn="ctr")],
            fill=NAVY, border=NAVY, anchor="ctr")
    s.save()


# -------------------------------------------------------------- references (6)
def slide6(root, media):
    s = Slide(root, 6, media)
    s.team()
    s.xml = empty_shape(s.xml, "TextBox 8")
    s.heading("RESEARCH  AND REFERENCES", GREEN, ["Title 1"])
    s.chip(0.67, 1.02, 6.40, 0.34,
           "Details / Links of the reference and research work", sz=8)

    # Source-map tiles: instantly answers "research-backed or invented".
    tiles = [
        ("IMD", "official \u00b7 keyed API"),
        ("CPCB", "official \u00b7 labelled adapter"),
        ("Copernicus", "official \u00b7 labelled"),
        ("MeitY UX4G", "design standard"),
        ("Our mock", "32 tests \u00b7 replay"),
    ]
    tx = 0.67
    for t, d in tiles:
        s.box("tile", "roundRect", tx, 1.46, 2.32, 0.72,
              [para([run(t, 11, True, WHITE)], algn="ctr"),
               para([run(d, 9, False, WHITE)], algn="ctr")],
              fill=NAVY if t in ("IMD", "Our mock") else BLUE, line=BLACK,
              anchor="ctr", lw=12700)
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
         "Mausam/docs/evidence (illustrative)"),
        ("Live demo \u2013 deployed PWA, guest-first, works offline",
         DEMO.removeprefix("https://")),
    ]
    s.panel(0.67, 2.32, 11.98, 3.05,
            [para([run(f"{i}.  {t}  ", 11, True, WHITE),
                   run(link, 11, True, "FFE08A", u="sng")], spc_aft=14)
             for i, (t, link) in enumerate(refs, 1)],
            fill=ORANGE2, border=BLACK, anchor="ctr", lw=28575)

    s.chip(0.67, 5.94, 2.40, 0.44, "REFERENCES", fill=GREEN, sz=12)
    s.box("note", "rect", 3.35, 5.98, 9.30, 0.40,
          [para([run("Official, verifiable sources; local mock paths are "
                     "labelled (illustrative). No fabricated statistics.",
                     10.5, False, INK)])], fill=None)
    s.save()


def drop_instruction_slide(root):
    (root / "ppt/slides/slide7.xml").unlink(missing_ok=True)
    (root / "ppt/slides/_rels/slide7.xml.rels").unlink(missing_ok=True)
    # slide7's speaker notes die with it, or their rels dangle.
    (root / "ppt/notesSlides/notesSlide6.xml").unlink(missing_ok=True)
    (root / "ppt/notesSlides/_rels/notesSlide6.xml.rels").unlink(missing_ok=True)
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
    cxt = re.sub(r'<Override PartName="/ppt/notesSlides/notesSlide6.xml"'
                 r'[^>]*/>', "", cxt)
    ct.write_text(cxt, encoding="utf-8")


def main():
    assert TPL.exists(), f"template missing: {TPL}"
    for ev in ["mobile-home.png", "ticket-04-provenance.png",
               "ticket-02-engine-hero.png",
               "ticket-21-onboarding-language-hi.png",
               "mausam-ai-assistant.png"]:
        assert (EV / ev).exists(), f"evidence missing: {ev}"
    assert DEMO_QR.exists(), f"demo QR missing: {DEMO_QR}"
    work = HERE / "build_tmp"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    with zipfile.ZipFile(TPL) as z:
        z.extractall(work)
    media = [2]  # template ships image1 + image2
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
