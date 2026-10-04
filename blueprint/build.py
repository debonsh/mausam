#!/usr/bin/env python3
"""Build SIH 2026 Solution Blueprint PDF: md -> styled HTML -> Chromium PDF, 2-pass TOC."""
import html as H
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent
PARTS = [ROOT / f"content-0{i}.md" for i in range(1, 6)]

CSS = """
@page { size: A4; margin: 20mm 17mm 19mm 17mm;
  @bottom-left { content: "SIH 2026 — Solution Blueprint"; font-size: 8pt; color: #8a94a6; font-family: sans-serif; }
  @bottom-right { content: counter(page); font-size: 8pt; color: #8a94a6; font-family: sans-serif; } }
* { box-sizing: border-box; }
body { font-family: "Noto Sans","DejaVu Sans",Verdana,sans-serif; font-size: 10pt; line-height: 1.55; color: #1c2333; }
h1 { font-size: 19pt; color: #0b3d91; border-bottom: 3px solid #0b3d91; padding-bottom: 6px; margin-top: 0; page-break-before: always; }
h2 { font-size: 13.5pt; color: #123a6d; margin-top: 22px; border-left: 5px solid #2f80ed; padding-left: 10px; }
h3 { font-size: 11pt; color: #1a4d8f; margin-top: 16px; }
table { border-collapse: collapse; width: 100%; margin: 10px 0 14px 0; font-size: 8.7pt; }
th { background: #0b3d91; color: #fff; text-align: left; padding: 6px 8px; }
td { border: 1px solid #c9d4e6; padding: 5px 8px; vertical-align: top; }
tr:nth-child(even) td { background: #f2f6fc; }
.arch { display: table; width: 100%; margin: 12px 0; }
.arow { display: table-row; }
.abox { display: table-cell; background: #eaf1fb; border: 2px solid #0b3d91; border-radius: 6px; padding: 7px 9px; font-size: 8.6pt; font-weight: bold; text-align: center; color: #0b3d91; vertical-align: middle; }
.abox span { display: block; font-weight: normal; color: #33415c; font-size: 7.8pt; margin-top: 3px; }
.aarrow { display: table-cell; vertical-align: middle; text-align: center; font-size: 14pt; color: #0b3d91; padding: 0 2px; }
.callout { border: 2px solid #b7791f; background: #fdf3e0; border-radius: 6px; padding: 10px 12px; margin: 12px 0; font-size: 9.3pt; }
blockquote { border-left: 4px solid #27ae60; background: #eef8f1; margin: 12px 0; padding: 8px 12px; font-size: 9.5pt; }
code { font-family: "DejaVu Sans Mono",monospace; font-size: 8.8pt; background: #eef1f6; padding: 1px 4px; border-radius: 3px; }
ul, ol { margin: 6px 0 10px 0; padding-left: 22px; }
li { margin-bottom: 3px; }
hr { border: none; border-top: 1px solid #c9d4e6; margin: 14px 0; }
.toc h2.toc-title { border: none; padding: 0; font-size: 17pt; color: #0b3d91; }
.toc-part { font-weight: bold; font-size: 10.5pt; color: #0b3d91; margin-top: 12px; }
.toc-row { display: flex; justify-content: space-between; font-size: 9.3pt; padding: 2.5px 0; border-bottom: 1px dotted #c9d4e6; }
.toc-row span:last-child { min-width: 3em; text-align: right; font-variant-numeric: tabular-nums; }
.pagebreak { page-break-before: always; }
.cover { height: 100%; display: flex; flex-direction: column; justify-content: center; }
.cover h1 { border: none; font-size: 34pt; line-height: 1.15; }
.cover .sub { font-size: 13pt; color: #33415c; margin-top: 10px; }
.cover .meta { margin-top: 26px; font-size: 9.5pt; color: #5a6b8a; }
.cover .bar { width: 120px; height: 6px; background: #2f80ed; margin: 18px 0; }
"""

COVER = """<div class="cover">
<h1>SIH 2026<br>Solution Blueprint</h1>
<div class="bar"></div>
<div class="sub">Four problem statements. One engineering-grade plan.<br>Zero invented facts.</div>
<div class="meta">SIH26156 · ULPF / NTRO &nbsp;&nbsp; SIH26076 · Mausam / IMD &nbsp;&nbsp; SIH26087 · NCCT / Cooperation &nbsp;&nbsp; SIH26138 · Green Fleet / Egreen Quanta<br><br>
Built from the verified SIH 2026 scrape (sih.gov.in, 2026-10-02) + authoritative external sources.<br>October 2026</div>
</div>"""


def inline(s: str) -> str:
    s = H.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", s)
    return s


def convert(md: str):
    """Returns (html, toc_entries[(level, text)])."""
    lines = md.split("\n")
    out, toc = [], []
    i, n = 0, len(lines)
    paras = []

    def flush_para():
        if paras:
            out.append("<p>" + inline(" ".join(paras)) + "</p>")
            paras.clear()

    while i < n:
        ln = lines[i]
        s = ln.strip()
        if not s:
            flush_para()
            i += 1
            continue
        if s.startswith("<"):
            flush_para()
            out.append(ln)
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            flush_para()
            lvl, txt = len(m.group(1)), m.group(2).strip()
            if lvl <= 2:
                toc.append((lvl, re.sub(r"\*+", "", txt)))
            out.append(f"<h{lvl}>{inline(txt)}</h{lvl}>")
            i += 1
            continue
        if re.match(r"^---+$", s):
            flush_para()
            out.append("<hr>")
            i += 1
            continue
        if s.startswith(">"):
            flush_para()
            qs = []
            while i < n and lines[i].strip().startswith(">"):
                qs.append(lines[i].strip()[1:].strip())
                i += 1
            out.append("<blockquote><p>" + inline(" ".join(qs)) + "</p></blockquote>")
            continue
        if s.startswith("|"):
            flush_para()
            tbl = []
            while i < n and lines[i].strip().startswith("|"):
                tbl.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            if len(tbl) >= 2 and all(re.match(r"^:?-{2,}:?$", c) for c in tbl[1]):
                head, body = tbl[0], tbl[2:]
                h = "<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
                for row in body:
                    row += [""] * (len(head) - len(row))
                    h += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row[: len(head)]) + "</tr>"
                out.append(h + "</tbody></table>")
            else:
                for row in tbl:
                    paras.append(" | ".join(row))
                flush_para()
            continue
        if re.match(r"^(\d+[.)]|[-*])\s+", s):
            flush_para()
            ordered = bool(re.match(r"^\d+[.)]\s+", s))
            items = []
            while i < n and re.match(r"^(\d+[.)]|[-*])\s+", lines[i].strip()):
                items.append(re.sub(r"^(\d+[.)]|[-*])\s+", "", lines[i].strip()))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        paras.append(s)
        i += 1
    flush_para()
    return "\n".join(out), toc


def page(html_body: str, toc_html: str, cover: bool) -> str:
    c = COVER if cover else ""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{c}{toc_html}{html_body}</body></html>"""


def render(html_path: pathlib.Path, pdf_path: pathlib.Path):
    subprocess.run(
        ["chromium", "--headless", "--no-sandbox", "--disable-gpu",
         "--print-to-pdf=" + str(pdf_path), "--print-to-pdf-no-header",
         "file://" + str(html_path)],
        check=True, capture_output=True, text=True, timeout=180)


def page_text(pdf: pathlib.Path, p: int) -> str:
    r = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-layout",
                        str(pdf), "-"], capture_output=True, text=True, check=True)
    return r.stdout


def main():
    md = "\n\n".join(p.read_text(encoding="utf-8") for p in PARTS)
    body, toc = convert(md)
    work = ROOT / "build_tmp"
    work.mkdir(exist_ok=True)

    # Pass 1: body with TOC lacking page numbers
    toc_rows = []
    for lvl, t in toc:
        cls = "toc-part" if lvl == 1 else "toc-row"
        if lvl == 1:
            toc_rows.append(f'<div class="{cls}">{H.escape(t)}</div>')
        else:
            toc_rows.append(f'<div class="{cls}"><span>{H.escape(t)}</span><span>…</span></div>')
    toc_html = '<div class="toc"><h2 class="toc-title">Contents</h2>' + "\n".join(toc_rows) + '</div><div class="pagebreak"></div>'
    MARK = "ZZCONTENTSTARTZZ"
    (work / "pass1.html").write_text(page(f'<span>{MARK}</span>' + body, toc_html, False), encoding="utf-8")
    render(work / "pass1.html", work / "pass1.pdf")

    total = int(subprocess.run(["pdfinfo", str(work / "pass1.pdf")], capture_output=True,
                               text=True, check=True).stdout.split("Pages:")[1].split()[0])
    # Content starts at the unique marker page (TOC itself contains all titles, so it is excluded)
    start = None
    for p in range(1, total + 1):
        if MARK in page_text(work / "pass1.pdf", p):
            start = p
            break
    assert start is not None, "could not locate content start"
    # Map each heading to a page, scanning forward
    pages, cur = [], start
    for lvl, t in toc:
        key = t.split("—")[0].strip()[:28] if "—" in t else t[:40]
        found = None
        for p in range(cur, total + 1):
            if key in page_text(work / "pass1.pdf", p):
                found = p
                break
        if found is None:  # fallback: substring of first 15 chars
            for p in range(cur, total + 1):
                if t[:15] in page_text(work / "pass1.pdf", p):
                    found = p
                    break
        pages.append(found or cur)
        cur = found or cur

    # Pass 2: TOC with real page numbers (+1 for cover page added later)
    toc_rows = []
    for (lvl, t), pg in zip(toc, pages):
        if lvl == 1:
            toc_rows.append(f'<div class="toc-part">{H.escape(t)}</div>')
        else:
            toc_rows.append(f'<div class="toc-row"><span>{H.escape(t)}</span><span>{pg + 1}</span></div>')
    toc_html = '<div class="toc"><h2 class="toc-title">Contents</h2>' + "\n".join(toc_rows) + '</div><div class="pagebreak"></div>'
    (work / "final.html").write_text(page(body, toc_html, False), encoding="utf-8")
    render(work / "final.html", work / "body.pdf")
    (work / "cover.html").write_text(
        f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{COVER}</body></html>',
        encoding="utf-8")
    render(work / "cover.html", work / "cover.pdf")
    final = ROOT / "SIH2026-Solution-Blueprint.pdf"
    subprocess.run(["qpdf", "--empty", "--pages", str(work / "cover.pdf"), str(work / "body.pdf"),
                    "--", str(final)], check=True)
    info = subprocess.run(["pdfinfo", str(final)], capture_output=True, text=True, check=True).stdout
    print(info)
    print("TOC entries:", len(toc), "| content starts at final page:", start + 1)


if __name__ == "__main__":
    sys.exit(main())
