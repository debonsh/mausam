#!/usr/bin/env python3
"""SIH 2026 — four solutions. Dark, refined terminal-briefing PDF.

Design: dense scannable briefing for a hackathon team. One accent (green),
amber reserved for warnings/demo moments, everything else quiet.
Flowcharts are CSS pipelines — no ASCII box art.
"""
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).parent
WORK = ROOT / "build_tmp"
WORK.mkdir(exist_ok=True)

CSS = r"""
@page { size: A4; margin: 0; }
body { background:#0a0e13; color:#d3dbe6; font-family:"DejaVu Sans Mono","Noto Sans Mono",monospace; font-size:9pt; line-height:1.58; margin:0; padding:10mm 12mm 13mm 12mm; }
.pgfoot { position:fixed; bottom:6mm; left:12mm; right:12mm; font-size:7pt; color:#33404f; }
.pgfoot .l { float:left; } .pgfoot .r { float:right; }

h1.sec { font-size:13pt; color:#eef3f9; font-weight:bold; border-bottom:1px solid #1c2836; padding:16px 0 7px 0; margin:18px 0 8px 0; }
h1.sec:first-of-type { margin-top:0; padding-top:0; }
h1.sec .n { color:#00e5a0; }
h2 { font-size:9.5pt; color:#7aa7e8; text-transform:uppercase; letter-spacing:1.2px; margin:14px 0 5px 0; font-weight:bold; }
p { margin:5px 0; } strong { color:#f2f6fb; } em { color:#8b98a8; font-style:normal; }
code { background:#141c26; color:#7ee787; padding:0 4px; border-radius:3px; font-size:8.6pt; }
ul { margin:5px 0 8px 0; padding-left:0; list-style:none; }
ul li { margin-bottom:4px; padding-left:14px; position:relative; }
ul li:before { content:"–"; position:absolute; left:0; color:#3d4c5e; }
.meta-line { color:#66788d; font-size:8.4pt; margin:2px 0 4px 0; }
.meta-line b { color:#9fb0c3; font-weight:normal; }
/* pipeline diagrams */
.pipe { display:table; width:100%; margin:10px 0 4px 0; }
.prow { display:table-row; }
.node { display:table-cell; border:1px solid #26374a; border-radius:6px; background:#0d131b; padding:6px 8px; text-align:center; vertical-align:middle; }
.node .t { display:block; color:#00e5a0; font-size:8.6pt; font-weight:bold; }
.node .s { display:block; color:#7d8ea3; font-size:7.4pt; margin-top:2px; line-height:1.4; }
.node.hot { border-color:#8a6a2a; } .node.hot .t { color:#ffb454; }
.node.cool { border-color:#2c4a6e; } .node.cool .t { color:#7aa7e8; }
.node.bad { border-color:#7a3330; } .node.bad .t { color:#ff7b72; }
.parr { display:table-cell; vertical-align:middle; text-align:center; color:#00e5a0; font-size:12pt; padding:0 4px; width:22px; }
.vcon { text-align:center; color:#3d4c5e; font-size:9pt; margin:1px 0; }
.vcon b { color:#00e5a0; font-weight:normal; }
/* week strip */
.weeks { display:table; width:100%; margin:10px 0 8px 0; border:1px solid #22303f; border-radius:6px; }
.wrow { display:table-row; }
.wk { display:table-cell; text-align:center; padding:6px 3px 7px 3px; border-right:1px solid #1a2534; vertical-align:top; }
.wk:last-child { border-right:none; }
.wk .n { display:block; color:#00e5a0; font-size:8.6pt; font-weight:bold; }
.wk .l { display:block; color:#cfd8e3; font-size:8pt; margin-top:1px; }
.wk .d { display:block; color:#66788d; font-size:7pt; margin-top:2px; line-height:1.45; }
/* roadmap table */
table.road { border-collapse:collapse; width:100%; margin:6px 0 8px 0; font-size:8.3pt; }
table.road td { border:none; border-top:1px solid #18222f; padding:3.5px 6px 3.5px 0; vertical-align:top; }
table.road tr:last-child td { border-bottom:1px solid #18222f; }
td.wn { color:#00e5a0; width:20px; font-weight:bold; }
td.wb { color:#c6d0dd; } td.wgo { color:#66788d; }
/* panels */
.panel { background:#0d131b; border:1px solid #22303f; border-radius:6px; padding:8px 12px; margin:10px 0; }
.panel.key { border-left:3px solid #00e5a0; }
.panel.warn { border-left:3px solid #ffb454; }
.panel .ph { font-size:8.6pt; font-weight:bold; letter-spacing:.6px; }
.panel.key .ph { color:#00e5a0; } .panel.warn .ph { color:#ffb454; }
.panel .pn { color:#66788d; font-size:8.2pt; margin-top:4px; }
/* overview table */
table.ov { border-collapse:collapse; width:100%; margin:8px 0; font-size:8.4pt; }
table.ov th { text-align:left; color:#66788d; font-weight:normal; text-transform:uppercase; letter-spacing:1px; font-size:7.6pt; padding:0 8px 5px 0; border-bottom:1px solid #22303f; }
table.ov td { padding:6px 8px 6px 0; border-bottom:1px solid #141c26; vertical-align:top; }
table.ov .ps { color:#00e5a0; font-weight:bold; white-space:nowrap; }
table.ov .sl { color:#ffb454; font-weight:bold; }
/* cover */
.cover { min-height:calc(100vh - 19mm);} display:flex; flex-direction:column; justify-content:center; }
.cover .prompt { color:#00e5a0; font-size:10pt; margin-bottom:14px; }
.cover h1 { font-size:31pt; line-height:1.22; color:#f2f6fb; margin:0; font-weight:bold; }
.cover h1 .g { color:#00e5a0; }
.cover .rule { width:72px; height:3px; background:#00e5a0; margin:20px 0; }
.cover .sub { color:#8b98a8; font-size:10pt; line-height:1.9; }
.cover .grid { display:table; margin-top:22px; font-size:8.4pt; }
.cover .grow { display:table-row; } .cover .gc { display:table-cell; padding:3px 18px 3px 0; color:#66788d; }
.cover .gc b { color:#d3dbe6; font-weight:normal; }
.cover .foot { margin-top:26px; color:#3d4c5e; font-size:8pt; }
"""


def node(title, sub="", cls=""):
    s = f'<span class="s">{sub}</span>' if sub else ""
    return f'<div class="node {cls}"><span class="t">{title}</span>{s}</div>'


def pipe(nodes, arrow="→"):
    """nodes: list of node html; returns one pipeline row."""
    cells = []
    for i, n in enumerate(nodes):
        cells.append(n)
        if i < len(nodes) - 1:
            cells.append(f'<div class="parr">{arrow}</div>')
    return '<div class="pipe"><div class="prow">' + "".join(cells) + "</div></div>"


def vdown(label=""):
    t = f' &nbsp;<b>{label}</b>' if label else ""
    return f'<div class="vcon">▼{t}</div>'


def weeks(items):
    """items: [(n, label, desc)]."""
    c = "".join(
        f'<div class="wk"><span class="n">{n}</span><span class="l">{l}</span><span class="d">{d}</span></div>'
        for n, l, d in items)
    return f'<div class="weeks"><div class="wrow">{c}</div></div>'


def road(rows):
    b = "".join(f'<tr><td class="wn">{a}</td><td class="wb">{c}</td><td class="wgo">→ {d}</td></tr>'
                for a, c, d in rows)
    return f'<table class="road"><tbody>{b}</tbody></table>'


def panel(kind, head, body, note=None):
    n = f'<div class="pn">{note}</div>' if note else ""
    return f'<div class="panel {kind}"><div class="ph">{head}</div><div>{body}</div>{n}</div>'


P = []
A = P.append

# ══════════ cover ══════════
A(f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="pgfoot"><span class="l">sih2026 · four solutions</span></div>
<div class="cover">
<div class="prompt">$ sih2026 --brief --plain-language</div>
<h1>Four problems.<br>Four solutions<span class="g">.</span><br>No hand-waving<span class="g">.</span></h1>
<div class="rule"></div>
<div class="sub">Problem in plain words → the one idea that wins → how it works →<br>week-by-week roadmap → the demo moment. Nothing else.</div>
<div class="grid">
<div class="grow"><div class="gc"><b>SIH26156</b> · ULPF / NTRO</div><div class="gc"><b>SIH26076</b> · Mausam / IMD</div></div>
<div class="grow"><div class="gc"><b>SIH26087</b> · NCCT / Cooperation</div><div class="gc"><b>SIH26138</b> · Green Fleet</div></div>
</div>
<div class="foot">deadline 05 oct 2026 · october 2026</div>
</div>

<h1 class="sec"><span class="n">00</span> &nbsp;overview</h1>
<table class="ov">
<thead><tr><th>PS</th><th>organisation</th><th>the problem, in one line</th><th>slots</th></tr></thead>
<tbody>
<tr><td class="ps">SIH26156</td><td>NTRO</td><td>every device writes logs differently — parsers take weeks to write and quietly lose data</td><td class="ps">323</td></tr>
<tr><td class="ps">SIH26076</td><td>IMD · Mausam</td><td>the weather app shows data but never tells eight kinds of users what to <em>do</em></td><td class="sl">178</td></tr>
<tr><td class="ps">SIH26087</td><td>NCCT</td><td>2.27 lakh people trained a year, but nobody can prove what they learned or match them to a job</td><td class="ps">402</td></tr>
<tr><td class="ps">SIH26138</td><td>Egreen Quanta</td><td>ships must cut fuel, cost and emissions together under IMO rules — too many variables by hand</td><td class="ps">375</td></tr>
</tbody></table>
<p style="color:#66788d;font-size:8.4pt">every project runs the same seven beats: understand → core → intelligence → screens → package → test → rehearse. the demo moment is built first; everything else serves it.</p>
""")

# ══════════ PS1 ══════════
A("""<h1 class="sec"><span class="n">01</span> &nbsp;SIH26156 — LOGSMITH</h1>
<div class="meta-line"><b>National Technical Research Organisation</b> · cybersecurity · 323 slots left</div>

<h2>the problem</h2>
<p>A firewall, a server and a CCTV camera all write logs in completely different formats. Analysing them means writing a separate parser per device — days of work each. Worse, parsers quietly drop or rename fields, and nobody finds out until an incident review goes wrong.</p>

<h2>the fix</h2>
<p>A pipeline that converts any log into one open standard (<code>OCSF</code>) and seals a copy of the original log inside every output record.</p>""")
A(panel("key", "THE ONE IDEA THAT WINS",
         "<strong>We can prove nothing was lost.</strong> One button rebuilds the original log from our own output and compares checksums. A match means the conversion was lossless.",
         "Anyone can <em>claim</em> lossless. We <em>show</em> it — live, in front of a judge."))
A("<h2>how it flows</h2>")
A(pipe([node("RAW LOGS IN", "syslog · CEF<br>JSON · LEEF"),
        node("DECODE", "charset · codecs"),
        node("NORMALISE", "OCSF mapping<br>signed + versioned"),
        node("LOSSLESS ENVELOPE", "raw bytes + SHA-256")]))
A(vdown())
A(pipe([node("AUTO-SETUP", "300 samples →<br>proposal + score", "cool"),
        node("CHANGE RADAR", "renamed field?<br>flag + quarantine", "cool"),
        node("HUMAN APPROVES", "mapping v1.0.0<br>locked", ""),
        node("VERIFY", "rebuild raw →<br>hash match ✓", "hot")]))
A(vdown("standard stream out → kafka · otlp · siem · data-lake parquet"))
A(panel("warn", "RIVALS",
         "Fixed regex rules solve parsing, not <em>proof</em>, not auto-setup, not drift. An LLM per log line is impossible in NTRO's required air gap — and unsafe for sensitive logs."))
A("<h2>roadmap — 7 weeks</h2>")
A(weeks([("1", "setup", "formats +<br>OCSF pin"), ("2", "pipeline", "one path<br>end to end"),
         ("3", "mappings", "auto-setup<br>engine"), ("4", "radar", "change<br>detection"),
         ("5", "ui", "3 screens<br>only"), ("6", "package", "offline +<br>speed test"),
         ("7", "demo", "video +<br>slides")]))
A(road([("1", "read log formats, lock OCSF version, collect samples", "5 formats parse correctly"),
        ("2", "core pipeline: read → convert → standard → store", "one end-to-end path works"),
        ("3", "mapping registry + auto-setup engine", "new device onboarded in < 10 min"),
        ("4", "change radar + dashboard", "a renamed field is caught automatically"),
        ("5", "three screens only: setup, radar, event inspector", "full journey clickable"),
        ("6", "container packaging, offline test, speed measurement", "zero internet, speed measured"),
        ("7", "demo script, 2-min video, 5 slides, judge prep", "submission ready")]))
A(panel("warn", "▊ DEMO MOMENT",
         "Paste an unfamiliar log line → the system proposes a mapping → press <code>VERIFY</code> → watch the original log rebuild from the output, checksums match → rename one field → watch the radar catch it live.",
         "NTRO's format caps: 2-page architecture doc, 2-minute video, 5 slides. Build to those."))

# ══════════ PS2 ══════════
A("""<h1 class="sec"><span class="n">02</span> &nbsp;SIH26076 — MAUSAM</h1>
<div class="meta-line"><b>India Meteorological Department · Mausam app</b> · smart automation · 178 slots left — most crowded</div>

<h2>the problem</h2>
<p>The official statement lists eight users — a patient, a runner, a surfer, a traveller, a parent, a farmer, a commuter, an event planner. That persona list is the <em>entire</em> official text: no background, no scope, no dataset. Building something serious from almost nothing is the real difficulty.</p>
<p style="color:#66788d">The constraint that decides the design: the app already ships lightning alerts and farmer crop advice. Proposing those as “innovation” means proposing what already exists.</p>

<h2>the fix</h2>
<p>Not another weather app — a layer on IMD's own official APIs that gives each user a short list of <strong>actions</strong>, not charts.</p>""")
A(panel("key", "THE ONE IDEA THAT WINS",
         "<strong>Every number can explain itself.</strong> Tap any value → the exact IMD source, station, issue time, and age.",
         "No weather app in India does this. For a government app, trust <em>is</em> the product."))
A("<h2>how it flows</h2>")
A(pipe([node("IMD APIs", "28 endpoints<br>forecast · warnings<br>marine · sun times"),
        node("CACHE + AGE", "every value<br>stamped"),
        node("RULES ENGINE", "data → action<br>+ the reason"),
        node("ACTION CARDS", "8 personas<br>< 15 KB bundle"),
        node("PWA", "offline · languages<br>screen-reader ok")]))
A(pipe([node("PROVENANCE", "tap any number →<br>source · station · age", "hot"),
        node("NO SOURCE? NO CARD", "“data unavailable”<br>+ why — never a fake number", "bad"),
        node("124-YEAR HISTORY", "“4× drier than<br>the normal”", "cool")]))
A(panel("warn", "RIVALS",
         "Persona tabs of weather tiles — tiles were never the problem. A generic chatbot will confidently invent an AQI number; ours refuses to, and says why. Non-IMD data enters only through labelled source adapters — that restraint is the differentiator."))
A("<h2>roadmap — 7 weeks</h2>")
A(weeks([("1", "imd key", "access +<br>28 endpoints"), ("2", "data", "fetch + age<br>every value"),
         ("3", "rules", "data → action<br>+ why"), ("4", "app", "“explain this<br>number”"),
         ("5", "personas", "languages +<br>contrast"), ("6", "history", "124-yr<br>comparison"),
         ("7", "demo", "script +<br>slides")]))
A(road([("1", "apply for IMD API access; map all 28 endpoints; list persona needs", "access works, or fallback confirmed"),
        ("2", "data layer: fetch, cache, track the age of every value", "all personas flow with timestamps"),
        ("3", "rules engine that turns data into actions", "every action traceable to source"),
        ("4", "core screen + the “explain this number” feature", "working and offline-capable"),
        ("5", "add 8 personas, regional languages, accessibility", "all 8 personas working"),
        ("6", "compare live data against 124 years of IMD rainfall history", "“normal vs today” visible"),
        ("7", "demo script, slides, judge prep", "full demo rehearsed")]))
A(panel("warn", "▊ DEMO MOMENT",
         "Throttle the browser to slow 2G → the app still loads instantly from cache → a fog warning appears with a real action → tap the temperature → the screen shows the IMD station, issue time and age of that number.",
         "Day-one task: register at <code>api.imd.gov.in</code> and stand up a static-IP host — the key is IP-bound and every call needs an hourly JWT. The critical path is administrative, not technical."))

# ══════════ PS3 ══════════
A("""<h1 class="sec"><span class="n">03</span> &nbsp;SIH26087 — SAHAKAR SETU</h1>
<div class="meta-line"><b>National Council for Cooperative Training · Ministry of Cooperation</b> · 402 slots left — least crowded</div>

<h2>the problem</h2>
<p>NCCT runs 20 institutes and trained 2.27 lakh people in a single year. Its systems are manual and disconnected: trainees finish courses but cannot prove what they can do, and employers cannot trust a certificate they have never checked. Training happens; outcomes stay invisible.</p>
<p style="color:#66788d">The trap: the statement lists eleven features. Building eleven shallow tabs is what most teams will do.</p>

<h2>the fix</h2>
<p>Treat the eleven features as plumbing. Own the one gap that matters: <strong>between finishing a course and getting a job.</strong> Named for NCCT's own motto — <em>“Sahakar se Samriddhi”, prosperity through cooperation.</em></p>""")
A("<h2>how it flows — and the loop that makes it different</h2>")
A(pipe([node("ENROL", ""), node("LEARN", "offline modules"), node("ASSESS", "quiz + practical"),
        node("SKILL GRAPH", "proof, not claims"), node("MATCH", "explained score"), node("HIRED?", "", "hot")]))
A(vdown("gap planner: “missing X, Y” → ICM Nagpur, 3 weeks → back to enrol"))
A(pipe([node("EMPLOYER SAYS", "hired / rejected + why", "cool"),
        node("REWEIGHT", "which skills actually<br>predict the outcome", "hot"),
        node("GRAPH IMPROVES", "next match<br>is better", "")]))
A(panel("key", "ALSO IN THE BUILD",
         "Certificate → digital fingerprint → public verify page (one click, no phone call). Attendance → QR + staff confirmation; face recognition optional, consented, on-device, deletable. Offline modules, quizzes, QR; institute shared computers, so no trainee needs a phone."))
A(panel("warn", "RIVALS",
         "Job portals match <em>keywords</em>; we match <em>proven ability</em> with evidence behind every score. A career chatbot gives generic advice; ours answers only from the trainee's own graph and the real course catalogue. A static portal structurally cannot learn from hiring outcomes."))
A("<h2>roadmap — 8 weeks, the biggest of the four</h2>")
A(weeks([("1", "skill", "3 syllabi<br>→ graph"), ("2", "profile", "login +<br>profiles"),
         ("3", "course", "offline<br>player"), ("4", "scoring", "evidence →<br>skill + range"),
         ("5", "employer", "post a<br>job"), ("6", "gap", "missing →<br>course"),
         ("7", "cert", "verify page<br>+ QR"), ("8", "loop", "outcome<br>reweight")]))
A(road([("1", "get 3 real course syllabi, map skills, define the skill graph", "graph covers 3 flagship courses"),
        ("2", "trainee + institute profiles, registration, login", "trainee logs in, sees profile"),
        ("3", "course player + quizzes, works offline", "a module runs with no internet"),
        ("4", "scoring: evidence → skill level with confidence range", "every quiz produces a scored skill"),
        ("5", "employer side: post a job, see matches with reasons", "job → explainable matches"),
        ("6", "gap planner: missing skill → exact course + institute", "full gap-closure path shown"),
        ("7", "certificates + public verification; QR attendance", "certificate verifiable by anyone"),
        ("8", "outcome capture + reweighting, demo script, slides", "full loop demoable")]))
A(panel("warn", "▊ DEMO MOMENT",
         "Open a trainee profile → see the gap to a target job → tap it → the exact 3-week course appears → complete a 5-question quiz live → watch the skill score fill in with a confidence range and a certificate fingerprint → employer sees the explained match → employer rejects with a reason → watch the admin dashboard reweight itself live.",
         "The whole loop in ~60 seconds — the strongest demo of the four."))

# ══════════ PS4 ══════════
A("""<h1 class="sec"><span class="n">04</span> &nbsp;SIH26138 — SEAWARD</h1>
<div class="meta-line"><b>Egreen Quanta</b> · 375 slots left</div>""")
A(panel("warn", "READ THIS FIRST",
         "This is a <strong>shipping</strong> problem, not road vehicles. Ship type, size, cruising speed, marine fuels — LNG, methanol, hydrogen, ammonia — plus shore power at berth. A truck dashboard with EV chargers misses the statement completely."))
A("""<h2>the problem</h2>
<p>Choose ships, sizes, speeds and fuels while cutting fuel cost, emissions and carbon intensity — without missing cargo deadlines. Too many combinations for hand calculation.</p>
<p>A real regulation drives it all: the <strong>IMO Carbon Intensity Indicator</strong> grades every ship A–E. A fuel-efficient but badly rated ship is still a compliance failure.</p>""")
A(panel("key", "THE ONE IDEA THAT WINS",
         "A timeline slider showing your “optimal” fleet becoming <strong>illegal by 2030</strong>. Drag it: today's A/B fleet slides into D/E — then the system re-optimises into the cheapest compliant fleet, with the cost attached.",
         "“Your optimal 2026 fleet is non-compliant by 2030. Here is the compliant one, and here is what it costs.”"))
A("<h2>how it flows</h2>")
A(pipe([node("SIMULATOR", "physics ground<br>truth, published"),
        node("FUEL MODEL", "physics backbone<br>+ AI residual"),
        node("CII ENGINE", "M ÷ W<br>grades A → E"),
        node("OPTIMISER", "fleet mix<br>speed · fuel"),
        node("SCENARIOS", "fuel switch<br>shore power")]))
A(vdown("benchmark — no free lunch: exact solver vs genetic vs swarm. must match the exact answer, else no quantum claim."))
A("<h2>the four parts, in one line each</h2>")
A(pipe([node("PHYSICS FIRST", "small, explainable,<br>correct on unseen ships", ""),
        node("CII-NATIVE", "optimise the rating,<br>not just the fuel", ""),
        node("HONEST QUANTUM", "classical code,<br>benchmarked", "cool"),
        node("REGULATORY CLIFF", "2024 → 2035<br>re-optimise on cost", "hot")]))
A(panel("warn", "DATA HONESTY — SAY THIS OUT LOUD",
         "Real ship-level fuel data is anonymised by IMO and is not public. So we build a documented physics simulator as our testbed — equations published — and treat real data as a bonus. Saying this plainly beats claiming data we do not have."))
A("<h2>roadmap — 8 weeks</h2>")
A(weeks([("1", "physics", "power · drag<br>· resistance"), ("2", "sim+cii", "voyage sim<br>grades A–E"),
         ("3", "fit", "per-ship<br>params"), ("4", "ai resid", "residual beats<br>physics-only"),
         ("5", "optimise", "exact + meta<br>compare"), ("6", "fuels", "shore power<br>speed limits"),
         ("7", "ui", "map · charts<br>cliff slider"), ("8", "demo", "benchmarks<br>+ script")]))
A(road([("1", "ship physics: power, drag, resistance — written down", "equations documented"),
        ("2", "voyage simulator (fleet, routes, weather) + CII formula", "runs a voyage, grades A–E"),
        ("3", "fit per-ship parameters; calibrate", "predictions match the simulator"),
        ("4", "AI residual layer; prove it beats physics-only", "measured improvement table"),
        ("5", "optimiser + exact integer-programming baseline", "both solve the same test fleet"),
        ("6", "alternative fuels, shore power, schedule limits", "scenario comparison works"),
        ("7", "frontend: map, charts, regulatory-cliff slider", "demo path clickable"),
        ("8", "benchmarks, demo script, slides", "full demo rehearsed")]))
A(panel("warn", "▊ DEMO MOMENT",
         "Load a fleet → run the optimisation → charts appear → drag the timeline to 2030 → watch ratings collapse from A/B into D/E → press re-optimise → watch a compliant mix appear with fuel switch, slower speeds and shore power, alongside cost per tonne of CO₂ saved."))

# ══════════ close ══════════
A("""<h1 class="sec"><span class="n">05</span> &nbsp;pick one — and three rules</h1>
<h2>which project suits your team</h2>""")
A(pipe([node("STRONG AT PARSING", "security · back-end", ""),
        node("01 · LOGSMITH", "deepest tech<br>clearest proof", "")]))
A(pipe([node("STRONG AT FRONT-END", "design · mobile · APIs", ""),
        node("02 · MAUSAM", "most crowded<br>needs the sharpest idea", "hot")]))
A(pipe([node("STRONG AT FULL-STACK", "databases · content", ""),
        node("03 · SAHAKAR SETU", "least crowded<br>most room to differ", "")]))
A(pipe([node("STRONG AT MATHS", "python · simulation", ""),
        node("04 · SEAWARD", "hardest build<br>best if it lands", "cool")]))
A("""<h2>team of six</h2>
<table class="ov"><tbody>
<tr><td class="ps">front-end</td><td>the app shell, offline mode, languages, demo polish</td></tr>
<tr><td class="ps">back-end ×2</td><td>APIs, background jobs, integrations, the data layer</td></tr>
<tr><td class="ps">data / domain</td><td>pipelines — log formats, weather, or shipping data</td></tr>
<tr><td class="ps">AI / optimisation</td><td>models, validation, benchmarks</td></tr>
<tr><td class="ps">DevOps + research</td><td>packaging, offline test, slides, video, judge prep</td></tr>
</tbody></table>
<h2>three rules that decide all four</h2>""")
A(panel("key", "1 · BUILD THE DEMO MOMENT FIRST",
         "Decide what the audience will gasp at, then build only what it needs. Every other screen is optional."))
A(panel("key", "2 · MEASURE, DON'T CLAIM",
         "Every number on a slide comes from your own test run. If you cannot measure it, write “to be measured in pilot” instead of a percentage."))
A(panel("key", "3 · SAY “WE DON'T KNOW” ONCE, WITH A PLAN",
         "In a hackathon that one sentence buys more trust than any feature."))
A('<p style="color:#3d4c5e;font-size:8pt;margin-top:14px">— end —</p></body></html>')


def main():
    (WORK / "tui2.html").write_text("\n".join(P), encoding="utf-8")
    for src, out in (("tui2.html", "tui2.pdf"),):
        subprocess.run(["chromium", "--headless", "--no-sandbox", "--disable-gpu",
                        f"--print-to-pdf={WORK/out}", "--no-pdf-header-footer",
                        "file://" + str(WORK / src)], check=True, capture_output=True, timeout=180)
    final = ROOT / "SIH2026-Four-Solutions-TUI.pdf"
    subprocess.run(["cp", str(WORK / "tui2.pdf"), str(final)], check=True)
    print(subprocess.run(["pdfinfo", str(final)], capture_output=True, text=True, check=True).stdout)


if __name__ == "__main__":
    main()