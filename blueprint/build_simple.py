#!/usr/bin/env python3
"""Build the short, plain-language 4-PS PDF (no TOC, no page-number pass)."""
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import CSS, COVER, convert, render  # noqa: E402

ROOT = pathlib.Path(__file__).parent
WORK = ROOT / "build_tmp"
WORK.mkdir(exist_ok=True)

SHORT_COVER = """<div class="cover">
<h1>SIH 2026<br>Four Solutions, Simply</h1>
<div class="bar"></div>
<div class="sub">Four problem statements. Four solutions in plain language.<br>Basic roadmap for each.</div>
<div class="meta">SIH26156 ULPF / NTRO &nbsp;·&nbsp; SIH26076 Mausam / IMD &nbsp;·&nbsp; SIH26087 NCCT &nbsp;·&nbsp; SIH26138 Green Fleet<br><br>
October 2026</div>
</div>"""

CSS_SHORT = CSS.replace("h1 { font-size: 19pt;", "h1 { font-size: 16pt;")
CSS_SHORT += "\ntable { font-size: 9pt; }\ntd, th { padding: 5px 7px; }\n"

body, _ = convert((ROOT / "simple.md").read_text(encoding="utf-8"))
html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS_SHORT}</style></head><body>{body}</body></html>'
(WORK / "simple.html").write_text(html, encoding="utf-8")
render(WORK / "simple.html", WORK / "simple.pdf")

(WORK / "cover.html").write_text(
    f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS_SHORT}</style></head><body>{SHORT_COVER}</body></html>',
    encoding="utf-8")
render(WORK / "cover.html", WORK / "cover.pdf")

final = ROOT / "SIH2026-Four-Solutions-Simple.pdf"
subprocess.run(["qpdf", "--empty", "--pages", str(WORK / "cover.pdf"), str(WORK / "simple.pdf"),
                "--", str(final)], check=True)
print(subprocess.run(["pdfinfo", str(final)], capture_output=True, text=True, check=True).stdout)