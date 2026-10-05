#!/usr/bin/env python3
"""SIH26076 final deck: edit the OFFICIAL template in place (stdlib only).

Reads:  mausam PPT/SIH2026-IDEA-Presentation-Format.pptx  (official, untouched)
Writes: mausam PPT/SIH26076-Mausam-FINAL.pptx            (6 slides, instruction slide dropped)

Design: "clean & official" - white slides, navy + azure, one Arial type scale,
strict grid, sharp hairline cards. Template masters, footer bar, SIH logo,
six slides, and every required pointer kept word-for-word in a quiet chip band.

Grid (inches): margin 0.67 | kicker 1.20 | headline 1.46 | rule 2.06
               content 2.20-6.40 | pointer chips 6.46-6.76 | footer 6.95

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
NAVY = "0B3C7A"        # primary
AZURE = "0B6BCB"       # accent (kickers, markers, links)
ARR = "9DC3E6"         # arrow fill
AMBER = "B45309"       # critical-path note (passes contrast at 7.5pt)
INK = "1F2933"
GREY = "5B6570"
LINE = "D8DEE4"        # hairline
PANEL = "F5F7FA"       # card fill
WHITE = "FFFFFF"

BODYFONT = "Arial"
SW = 13.333            # slide width, inches
M = 0.67               # left/right margin
CW = 11.99             # content width


def E(v):
    return int(round(v * EMU))


def run(t, sz=12, b=False, color=INK, font=BODYFONT, u=None, spc=None):
    bb = ' b="1"' if b else ""
    uu = f' u="{u}"' if u else ""
    ss = f' spc="{int(spc * 100)}"' if spc else ""
    # ECMA-376 order: solidFill BEFORE latin/ea/cs, else renderers drop it.
    return (
        f'<a:r><a:rPr lang="en-US" sz="{int(sz * 100)}"{bb}{uu}{ss} dirty="0">'
        f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
        f'<a:latin typeface="{font}"/><a:ea typeface="{font}"/>'
        f'<a:cs typeface="{font}"/></a:rPr>'
        f"<a:t>{escape(t)}</a:t></a:r>"
    )


def para(runs, algn="l", spc_aft=None, lnspc=100000):
    rs = "".join(runs)
    aft = (f'<a:spcAft><a:spcPts val="{int(spc_aft * 100)}"/></a:spcAft>'
           if spc_aft else "")
    return (
        f'<a:p><a:pPr algn="{algn}">'
        f'<a:lnSpc><a:spcPct val="{int(lnspc)}"/></a:lnSpc>' + aft +
        "</a:pPr>" + rs + "</a:p>"
    )


def shape(sid, name, geom, x, y, w, h, paras, fill=None, line=None,
          anchor="t", wrap="square", adj=None, lw=12700, ins=None):
    fxml = (f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
            if fill else "<a:noFill/>")
    lxml = (f'<a:ln w="{lw}"><a:solidFill><a:srgbClr val="{line}"/>'
            "</a:solidFill></a:ln>" if line else '<a:ln><a:noFill/></a:ln>')
    adjx = f"<a:avLst>{adj}</a:avLst>" if adj else "<a:avLst/>"
    insx = ""
    if ins is not None:
        insx = (f' lIns="{E(ins)}" rIns="{E(ins)}"'
                f' tIns="{E(ins * 0.5)}" bIns="{E(ins * 0.5)}"')
    tx = "".join(paras)
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{escape(name)}"/>'
        '<p:cNvSpPr><a:spLocks noChangeAspect="0"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>'
        f"<p:spPr><a:xfrm><a:off x=\"{E(x)}\" y=\"{E(y)}\"/>"
        f"<a:ext cx=\"{E(w)}\" cy=\"{E(h)}\"/></a:xfrm>"
        f'<a:prstGeom prst="{geom}">{adjx}</a:prstGeom>{fxml}{lxml}</p:spPr>'
        f'<p:txBody><a:bodyPr anchor="{anchor}" wrap="{wrap}"{insx}>'
        "<a:normAutofit/></a:bodyPr>"
        '<a:lstStyle/>' + tx + "</p:txBody></p:sp>"
    )


def arrow(sid, x, y, w, h, fill=ARR):
    return shape(sid, "arr", "rightArrow", x, y, w, h, [EMPTY_PARA],
                 fill=fill, anchor="ctr")


def next_id(xml):
    return max(int(v) for v in re.findall(r'cNvPr id="(\d+)"', xml)) + 1


EMPTY_PARA = ('<a:p><a:pPr><a:lnSpc><a:spcPct val="100000"/></a:lnSpc>'
              '</a:pPr></a:p>')


def empty_shape(xml, name):
    """Blank a shape's text and park its frame as a 100x100 EMU husk.

    Operates on the shape block itself: the old global regex could not match
    a negative x offset and silently husked the NEXT shape instead."""
    pat = re.compile(
        r'<p:(?:sp|graphicFrame)\b(?:(?!</p:(?:sp|graphicFrame)>).)*?'
        r'<p:cNvPr id="\d+" name="' + re.escape(name) + r'".*?'
        r'</p:(?:sp|graphicFrame)>', re.S)
    m = pat.search(xml)
    assert m, f"shape not found: {name}"
    blk = m.group(0)
    tpat = re.compile(r'(<p:txBody>.*?<a:lstStyle/>)(.*?)(</p:txBody>)', re.S)
    tm = tpat.search(blk)
    assert tm, f"txBody not found: {name}"
    blk = blk[:tm.start(2)] + EMPTY_PARA + blk[tm.end(2):]
    if "<a:off " in blk:
        blk, n1 = re.subn(r'<a:off x="-?\d+" y="-?\d+"/>',
                          f'<a:off x="{E(12.95)}" y="{E(6.60)}"/>', blk, count=1)
        blk, n2 = re.subn(r'<a:ext cx="\d+" cy="\d+"/>',
                          '<a:ext cx="100" cy="100"/>', blk, count=1)
        assert n1 == 1 and n2 == 1, f"xfrm not found: {name}"
    return xml[:m.start()] + blk + xml[m.end():]


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
    """Approximate one-line width of a regular-weight chip label."""
    return 0.059 * (sz / 8.0) * len(text) + 0.40


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

    def team(self):
        """Team-name oval: widen it, recolour it to the deck system, and
        shrink the run so 'Zencoderss' stays on one line."""
        m = re.search(r"<p:sp>(?:(?!</p:sp>).)*?<a:t>Your Team Name</a:t>"
                      r".*?</p:sp>", self.xml, re.S)
        assert m, "team oval not found"
        blk = m.group(0)
        blk = re.sub(r'<a:ext cx="\d+" cy="\d+"/>',
                     f'<a:ext cx="{E(1.95)}" cy="{E(0.88)}"/>', blk, count=1)
        blk = blk.replace(
            "</a:prstGeom></p:spPr>",
            "</a:prstGeom>"
            '<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
            f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{NAVY}"/>'
            "</a:solidFill></a:ln></p:spPr>", 1)
        blk = blk.replace(
            '<a:rPr lang="en-US" dirty="0"/>',
            '<a:rPr lang="en-US" sz="1100" dirty="0">'
            f'<a:solidFill><a:srgbClr val="{NAVY}"/></a:solidFill></a:rPr>', 1)
        blk = blk.replace("<a:t>Your Team Name</a:t>",
                          f"<a:t>{escape(TEAM_NAME)}</a:t>", 1)
        self.xml = self.xml[:m.start()] + blk + self.xml[m.end():]

    def pic(self, name, src, x, y, w=None, h=None, border=NAVY, lw=9525):
        iw, ih = png_size(src)
        if w is None:
            w = h * iw / ih
        elif h is None:
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
        ln = (f'<a:ln w="{lw}"><a:solidFill><a:srgbClr val="{border}"/>'
              "</a:solidFill></a:ln>" if border else "<a:ln><a:noFill/></a:ln>")
        frag = (
            f'<p:pic><p:nvPicPr><p:cNvPr id="{self.sid}" name="{escape(name)}"/>'
            '<p:cNvPicPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/>'
            '<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/>'
            f'<a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f"<a:noFill/>{ln}</p:spPr></p:pic>"
        )
        self.add(frag)
        return h

    def save(self):
        self.p.write_text(self.xml, encoding="utf-8")
        self.rels_p.write_text(self.rels, encoding="utf-8")


# ------------------------------------------------------------- shared frame
def kick(s, text, y=1.20):
    s.box("kicker", "rect", M, y, CW, 0.26,
          [para([run(text, 9.5, True, AZURE, spc=1.6)])], fill=None, ins=0)


def head(s, text, y=1.46, sz=26, w=CW):
    s.box("headline", "rect", M, y, w, 0.58,
          [para([run(text, sz, True, NAVY)], lnspc=95000)], fill=None, ins=0)


def rule(s, x, y, w, color=LINE, h=0.014):
    s.box("rule", "rect", x, y, w, h, [EMPTY_PARA], fill=color)


def card(s, x, y, w, h, paras, accent=None, fill=PANEL, line=LINE,
         anchor="t", pad=0.18, lw=6350):
    s.box("card", "rect", x, y, w, h, paras, fill=fill, line=line,
          anchor=anchor, lw=lw, ins=pad)
    if accent:
        s.box("accent", "rect", x, y, 0.05, h, [EMPTY_PARA], fill=accent)


def note(s, x, y, w, h, paras):
    """Transparent text block, no insets."""
    s.box("text", "rect", x, y, w, h, paras, fill=None, ins=0)


def pointer_band(s, strings):
    """Template pointers, word-for-word, as a quiet outlined chip row."""
    y, h, gap, maxw = 6.46, 0.30, 0.10, CW
    sz = 8.0
    while sz > 6.0:
        widths = [cw(t, sz) for t in strings]
        if sum(widths) + gap * (len(widths) - 1) <= maxw:
            break
        sz -= 0.5
    x = M
    for t, w in zip(strings, widths):
        s.box("ptr", "rect", x, y, w, h,
              [para([run(t, sz, False, GREY)], algn="ctr")],
              fill=WHITE, line=LINE, anchor="ctr", lw=6350)
        x += w + gap
    total = x - gap
    assert total <= M + maxw + 1e-6, f"pointer band overflow: {total:.2f}"


def frame(s, kicker, title):
    """Standard body-slide frame: oval, kicker, headline, rule, pointers."""
    s.team()
    s.xml = empty_shape(s.xml, "Title 1")
    s.xml = empty_shape(s.xml, "TextBox 8")
    kick(s, kicker)
    head(s, title)
    rule(s, M, 2.06, CW, NAVY, 0.022)


# ---------------------------------------------------------------- title page
def slide1(root, media):
    s = Slide(root, 1, media)
    # Template scaffolding out; fields are re-emitted below (info only).
    s.xml = empty_shape(s.xml, "Subtitle 3")
    s.xml = empty_shape(s.xml, "Title 7")
    s.xml = empty_shape(s.xml, "TextBox 9")
    # Template decorations (bulb freeform + cropped watermark) are ghost art;
    # keep the locked white Rectangle 24 and the SIH logo (Picture 1).
    s.xml = remove_shape(s.xml, "Freeform: Shape 26")
    s.xml = remove_shape(s.xml, "Picture 4")

    kick(s, "SMART INDIA HACKATHON 2026", y=1.34)
    head(s, "Mausam home: actions with proof", y=1.64, sz=34, w=10.0)
    s.box("accent", "rect", M, 2.46, 1.60, 0.07, [EMPTY_PARA], fill=AMBER)

    # Fields panel: grey label above, navy value under (fixed grid).
    py, ph = 2.72, 2.86
    card(s, M, py, CW, ph, [EMPTY_PARA])
    px, pw = M + 0.28, CW - 0.56
    note(s, px, py + 0.22, pw, 0.22,
         [para([run("Problem Statement Title-", 9.5, False, GREY)])])
    note(s, px, py + 0.44, pw, 0.46,
         [para([run("Personalised homepage for the 'Mausam' mobile "
                    "application", 17, True, NAVY)], lnspc=95000)])
    rule(s, px, py + 1.02, pw, LINE, 0.012)

    cols = [px, px + 3.81, px + 7.62]
    colw = 3.60
    rows = [
        (py + 1.18, [
            ("Problem Statement ID –", "SIH26076"),
            ("Theme-", "Smart Automation"),
            ("PS Category- Software/Hardware", "Software"),
        ]),
        (py + 1.88, [
            ("Team ID-", TEAM_ID),
            ("Team Name (Registered on portal)", TEAM_NAME),
            ("Organisation", "Ministry of Earth Sciences (IMD)"),
        ]),
    ]
    for ry, fields in rows:
        for cx, (label, value) in zip(cols, fields):
            note(s, cx, ry, colw, 0.20,
                 [para([run(label, 9.5, False, GREY)])])
            note(s, cx, ry + 0.20, colw, 0.36,
                 [para([run(value, 14, True, NAVY)], lnspc=95000)])

    rule(s, M, 5.68, CW, LINE, 0.012)
    note(s, M, 5.84, 10.2, 0.34,
         [para([run("Every number shows its source, station, issue time and "
                    "age. Every advisory can be re-derived by hand.",
                    13, False, GREY)])])

    # Live demo: QR + URL (bottom band).
    s.pic("demoqr", DEMO_QR, M, 6.32, 0.62, 0.62, border=LINE)
    note(s, 1.47, 6.34, 9.4, 0.60,
         [para([run("LIVE DEMO   ", 10, True, NAVY),
                run(DEMO, 9.5, True, AZURE, u="sng")]),
          para([run("Guest-first PWA · works offline · English and Hindi",
                    9, False, GREY)], spc_aft=4)])
    s.save()


# ------------------------------------------------------------ the idea (2)
def slide2(root, media):
    s = Slide(root, 2, media)
    frame(s, "THE IDEA",
          "One home screen that adapts to you — and shows its work")

    note(s, M, 2.20, CW, 0.34,
         [para([run("The Mausam home shows a number with no context: no "
                    "station, no issue time, no age — so advice is trusted "
                    "or ignored at random.", 13, True, INK)], lnspc=100000)])

    # Who / what / why.
    colw = (CW - 0.36) / 3
    cols = [
        ("WHO IT AFFECTS",
         "Commuters in fog, farmers at sowing, parents in a heat wave — "
         "anyone reading one number and acting on it."),
        ("WHAT'S BROKEN TODAY",
         "A one-size homepage: readings shown without source, station, "
         "issue time or age."),
        ("WHY IT MATTERS",
         "A wrong-day sowing or a late departure costs money and safety — "
         "and the app cannot be questioned."),
    ]
    cy = 2.66
    for i, (label, body) in enumerate(cols):
        cx = M + i * (colw + 0.18)
        card(s, cx, cy, colw, 0.92,
             [para([run(label, 8, True, AZURE, spc=1.2)], spc_aft=5),
              para([run(body, 10, False, INK)], lnspc=108000)],
             accent=AZURE)

    # The four mandated pointers as cards.
    blocks = [
        ("Proposed Solution (Describe your Idea/Solution/Prototype)",
         "A home screen that adapts to you: map on top, action cards below."),
        ("Detailed explanation of the proposed solution",
         "Onboarding picks your persona; the home reorders — the farmer "
         "sees sowing first, the commuter sees fog first."),
        (" How it addresses the problem",
         "Every card says what to do and shows the readings behind it: "
         "source, station, issue time and age."),
        ("Innovation and uniqueness of the solution ",
         "Source on every number · replayable advice · honest gap cards · "
         "a grounded bot that never invents figures."),
    ]
    bw = (CW - 0.19) / 2
    bh = 1.24
    for i, (label, body) in enumerate(blocks):
        bx = M + (i % 2) * (bw + 0.19)
        by = 3.75 + (i // 2) * (bh + 0.16)
        card(s, bx, by, bw, bh,
             [para([run(label, 7.5, True, AZURE, spc=0.8)], spc_aft=6),
              para([run(body, 11, False, INK)], lnspc=112000)],
             accent=NAVY, anchor="ctr")

    # The four pointers ARE these card labels, verbatim - no chip row here.
    s.save()


# ------------------------------------------------- technical approach (3)
def slide3(root, media):
    s = Slide(root, 3, media)
    frame(s, "TECHNICAL APPROACH", "IMD data in, verified decisions out")

    lw_, rx, rw = 7.40, 8.30, 4.36

    note(s, M, 2.20, lw_, 0.52,
         [para([run("One deterministic pipeline: IMD keyed APIs → engine → "
                    "decision stack, every value carrying its source, "
                    "station, issue time and age.", 13, True, NAVY)],
               lnspc=104000)])

    # Flow: four steps + arrows.
    steps = [
        ("IMD INPUT", "28 keyed APIs\nWFS · CAP feed"),
        ("GATEWAY", "static IP host\nkey + hourly JWT"),
        ("ENGINE", "rules · replay\nlabelled adapters"),
        ("HOMEPAGE", "PWA · EN/HI\noffline shell"),
    ]
    bw, gap = 1.595, 0.34
    bx, by, bh = M, 2.84, 1.00
    for i, (t, d) in enumerate(steps):
        paras = [para([run(t, 9.5, True, NAVY)], algn="ctr", spc_aft=4)]
        paras += [para([run(p, 8, False, GREY)], algn="ctr", lnspc=104000)
                  for p in d.split("\n")]
        card(s, bx, by, bw, bh, paras,
             fill=WHITE, line=NAVY if i == 1 else LINE, pad=0.10,
             anchor="ctr")
        if i < 3:
            s.sid += 1
            s.add(arrow(s.sid, bx + bw + 0.04, by + 0.38, 0.26, 0.24))
        bx += bw + gap
    note(s, M + bw + gap, 3.88, bw, 0.20,
         [para([run("Day-1 critical path", 7.5, True, AMBER)], algn="ctr")])

    # Tech stack, grouped.
    gw = (lw_ - 0.32) / 3
    groups = [
        ("CLIENT", "Vanilla JS PWA · Leaflet maps · service worker"),
        ("SERVER", "FastAPI · push · attribution ledger"),
        ("DATA & APIs", "IMD keyed · WFS · CAP · CPCB · CAMS"),
    ]
    for i, (label, items) in enumerate(groups):
        gx = M + i * (gw + 0.16)
        card(s, gx, 4.20, gw, 1.00,
             [para([run(label, 8, True, AZURE, spc=1.2)], spc_aft=5),
              para([run(items, 9, False, INK)], lnspc=110000)])

    # Methodology, three stages.
    note(s, M, 5.34, lw_, 0.20,
         [para([run("METHODOLOGY", 8, True, AZURE, spc=1.4)])])
    stages = [
        ("Mock today", "real captures\n32 tests green"),
        ("Live pipeline", "keyed APIs\nstatic IP + JWT"),
        ("Finale", "3 personas · push\nlabelled adapters"),
    ]
    sw_, sgap = 2.30, 0.25
    sx, sy, sh = M, 5.56, 0.80
    for i, (t, d) in enumerate(stages):
        paras = [para([run(t, 10, True, NAVY)], spc_aft=3)]
        paras += [para([run(p, 8.5, False, GREY)], lnspc=104000)
                  for p in d.split("\n")]
        card(s, sx, sy, sw_, sh, paras,
             accent=AZURE, pad=0.14, anchor="ctr")
        if i < 2:
            s.sid += 1
            s.add(arrow(s.sid, sx + sw_ + 0.03, sy + 0.28, 0.19, 0.22))
        sx += sw_ + sgap

    # Right column: working prototype + assistant preview.
    ph = 3.55
    pw1, pw2 = ph / 2.164, ph / 2.350
    gap2 = 0.20
    x0 = rx + (rw - (pw1 + pw2 + gap2)) / 2
    s.pic("shot-proto", EV / "ticket-02-engine-hero.png", x0, 2.20, w=pw1, h=ph)
    x1 = x0 + pw1 + gap2
    s.pic("shot-ai", EV / "mausam-ai-assistant.png", x1, 2.20, w=pw2, h=ph)
    note(s, x0, 5.82, pw1, 0.22,
         [para([run("WORKING PROTOTYPE", 7, True, GREY, spc=0.6)],
               algn="ctr")])
    note(s, x1, 5.82, pw2, 0.22,
         [para([run("ASSISTANT · DESIGN", 7, True, GREY, spc=0.6)],
               algn="ctr")])
    note(s, rx, 6.06, rw, 0.34,
         [para([run("The mock runs offline on captured IMD payloads; the "
                    "keyed gateway is the Day-1 critical path.",
                    9, False, GREY)], lnspc=106000)])

    pointer_band(s, [
        "Technologies to be used (e.g. programming languages, frameworks, "
        "hardware)",
        "Methodology and process for implementation (Flow Charts/Images/ "
        "working prototype)",
    ])
    s.save()


# ------------------------------------------- feasibility and viability (4)
def slide4(root, media):
    s = Slide(root, 4, media)
    frame(s, "FEASIBILITY AND VIABILITY",
          "Every risk already has a working fallback")

    lw_, rx = 5.60, 6.90
    rw = 12.66 - rx
    note(s, M, 2.20, lw_, 0.24,
         [para([run("CHALLENGE", 8.5, True, AZURE, spc=1.4)])])
    note(s, rx, 2.20, rw, 0.24,
         [para([run("HOW WE HANDLE IT", 8.5, True, AZURE, spc=1.4)])])
    rule(s, M, 2.50, CW, NAVY, 0.016)

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
    y = 2.58
    for i, (risk, fix) in enumerate(rows):
        note(s, M, y, lw_, 0.56, [para([run(risk, 11, False, INK)])])
        note(s, rx, y, rw, 0.56, [para([run(fix, 11, False, INK)])])
        y += 0.56
        if i < 3:
            rule(s, M, y - 0.03, CW, LINE, 0.01)

    # Build order timeline.
    note(s, M, 4.96, CW, 0.20,
         [para([run("BUILD ORDER", 8.5, True, AZURE, spc=1.4)])])
    rule(s, M, 5.36, CW, LINE, 0.014)
    tl = [("Day 1", "static-IP host + key registration", True),
          ("Week 1", "captured-payload mock (done)", False),
          ("Week 3", "live keyed pipeline", False),
          ("Finale", "3 personas · push · labelled adapters", False)]
    seg = CW / 4
    for i, (t, d, hot) in enumerate(tl):
        cx = M + (i + 0.5) * seg
        s.box("dot", "ellipse", cx - 0.07, 5.30, 0.14, 0.14,
              [EMPTY_PARA], fill=AMBER if hot else NAVY)
        note(s, cx - seg / 2, 5.48, seg, 0.24,
             [para([run(t, 11, True, NAVY)], algn="ctr")])
        note(s, cx - seg / 2, 5.70, seg, 0.34,
             [para([run(d, 9, False, GREY)], algn="ctr", lnspc=104000)])

    card(s, M, 6.00, CW, 0.40,
         [para([run("Viability: ", 10, True, NAVY),
                run("one container on a static-IP VM · one IMD API account "
                    "(2 DEV + 2 PROD keys, attribution ledger on request) · "
                    "no paid services · IMD data with attribution; CPCB/CAMS "
                    "labelled adapters.", 10, False, INK)], algn="ctr")],
         accent=NAVY, anchor="ctr", pad=0.20)

    pointer_band(s, [
        "Analysis of the feasibility of the idea",
        "Potential challenges and risks",
        "Strategies for overcoming these challenges",
    ])
    s.save()


# ----------------------------------------------------- impact & benefits (5)
def slide5(root, media):
    s = Slide(root, 5, media)
    frame(s, "IMPACT AND BENEFITS", "Earlier action, traceable trust")

    personas = [
        ("Commuter", "Fog window plus “leave 20 min early”, stated as an "
                     "action, not a number.",
         "Recall of the action after the alert"),
        ("Farmer", "Agromet sowing window and rainfall against normal, in "
                   "the order he works.",
         "Action recalled minutes later"),
        ("Health", "Heat card — and “IMD does not publish pollen” where the "
                   "data is missing.",
         "Readers treating the gap as a gap"),
    ]
    colw = (CW - 0.36) / 3
    for i, (name, action, measure) in enumerate(personas):
        cx = M + i * (colw + 0.18)
        card(s, cx, 2.20, colw, 1.60,
             [para([run(name, 13, True, NAVY)], spc_aft=6),
              para([run(action, 10.5, False, INK)], lnspc=112000,
                   spc_aft=8),
              para([run("WE MEASURE", 7.5, True, AZURE, spc=1.2)],
                   spc_aft=3),
              para([run(measure, 9.5, False, GREY)], lnspc=106000)],
             accent=NAVY, pad=0.20, anchor="ctr")

    note(s, M, 4.00, CW, 0.22,
         [para([run("BENEFITS", 8.5, True, AZURE, spc=1.4)])])
    benefits = [
        ("Earlier action — ", "each card states what to do and how fast."),
        ("Traceable trust — ", "every reading names its source, station and "
                               "age."),
        ("Works offline — ", "the home shell keeps the last forecast."),
        ("Hindi + English — ", "warning text is human-reviewed, never raw "
                               "machine translation."),
        ("Honest gaps — ", "missing data shows as a gap, never a fake zero."),
    ]
    bw = (CW - 0.19) / 2
    for col, group in enumerate((benefits[:3], benefits[3:])):
        bx = M + col * (bw + 0.19)
        note(s, bx, 4.24, bw, 1.60,
             [para([run("■  ", 8, True, AZURE),
                    run(lead, 10.5, True, NAVY),
                    run(rest, 10.5, False, INK)], lnspc=112000, spc_aft=24)
              for lead, rest in group])

    card(s, M, 5.86, CW, 0.48,
         [para([run("Scalability — ", 10.5, True, WHITE),
                run("stateless engine, labelled adapters per source, "
                    "personas as configuration: a new state needs data, not "
                    "a rewrite.", 10.5, False, WHITE)], algn="ctr")],
         fill=NAVY, line=NAVY, anchor="ctr", pad=0.20)

    pointer_band(s, [
        "Potential impact on the target audience",
        "Benefits of the solution (social, economic, environmental, etc.)",
    ])
    s.save()


# ------------------------------------------------------- references (6)
def slide6(root, media):
    s = Slide(root, 6, media)
    frame(s, "RESEARCH AND REFERENCES",
          "Official sources, labelled adapters, no invented numbers")

    lw_ = 7.60
    refs = [
        ("IMD API reference + portal user guide (key, hourly JWT, static IP)",
         "api.imd.gov.in"),
        ("CPCB real-time AQI, GODL", "data.gov.in"),
        ("Copernicus CAMS atmosphere data store",
         "ads.atmosphere.copernicus.eu"),
        ("MeitY UX4G design system + PIB Mausam note (2023)",
         "ux4g.gov.in · pib.gov.in"),
        ("Pai, N. et al. (2014), IMD Pune gridded rainfall 0.25°",
         "published dataset"),
        ("Mausam app: existing Damini lightning + Meghdoot crop modules",
         "mausam.imd.gov.in"),
        ("Working mock, fixtures, replay tests (32 pass)",
         "Mausam/docs/evidence (illustrative)"),
        ("Live demo – deployed PWA, guest-first, works offline",
         DEMO.removeprefix("https://")),
    ]
    y = 2.20
    for i, (title, link) in enumerate(refs, 1):
        note(s, M, y, lw_, 0.24,
             [para([run(f"{i}.  ", 10, True, AZURE),
                    run(title, 10.5, False, INK)])])
        note(s, M + 0.32, y + 0.22, lw_ - 0.32, 0.20,
             [para([run(link, 9, False, GREY, u="sng")])])
        y += 0.44
        rule(s, M, y - 0.05, lw_, LINE, 0.01)

    card(s, M, 5.84, lw_, 0.56,
         [para([run("How we differ — ", 9.5, True, NAVY),
                run("Damini and Meghdoot show values; we show values with "
                    "source, station, issue time and age, plus replayable "
                    "advice and honest gap cards.", 9.5, False, INK)],
               lnspc=106000)],
         accent=AZURE, pad=0.14, anchor="ctr")

    rx, rw = 8.55, 4.11
    note(s, rx, 2.20, rw, 0.22,
         [para([run("SOURCE MAP", 8.5, True, AZURE, spc=1.4)])])
    sources = [
        ("IMD", "official · keyed API"),
        ("CPCB", "official · labelled adapter"),
        ("Copernicus CAMS", "official · labelled"),
        ("MeitY UX4G", "design standard"),
        ("Our mock", "32 tests · replay"),
    ]
    y = 2.50
    for name, desc in sources:
        note(s, rx, y, rw, 0.24,
             [para([run(name + "  ", 10, True, NAVY),
                    run(desc, 9, False, GREY)])])
        y += 0.40
        rule(s, rx, y - 0.08, rw, LINE, 0.01)

    s.pic("demoqr", DEMO_QR, rx, 4.78, 1.00, 1.00, border=LINE)
    note(s, rx + 1.18, 4.80, rw - 1.18, 1.00,
         [para([run("Scan to try the live demo", 10.5, True, NAVY)],
               spc_aft=4),
          para([run(DEMO, 8, True, AZURE, u="sng")], lnspc=104000,
               spc_aft=4),
          para([run("Guest-first PWA · offline · EN/HI", 8.5, False, GREY)])])

    note(s, rx, 5.94, rw, 0.46,
         [para([run("Official, verifiable sources; local mock paths are "
                    "labelled (illustrative). No fabricated statistics.",
                    9.5, False, GREY)], lnspc=106000)])

    pointer_band(s, ["Details / Links of the reference and research work"])
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
    for ev in ["ticket-02-engine-hero.png", "mausam-ai-assistant.png"]:
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
