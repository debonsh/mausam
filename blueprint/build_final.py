#!/usr/bin/env python3
"""SIH 2026 — per-PS brief: official description, our build, how to build it,
flowchart, PPT slide plan, tips + out-of-the-box ideas. Nothing else."""
import pathlib
import subprocess

from build_tui import node, pipe, vdown, panel  # noqa: F401

ROOT = pathlib.Path(__file__).parent
WORK = ROOT / "build_tmp"
WORK.mkdir(exist_ok=True)

THEME = r"""
@page { size: A4; margin: 0; }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { background: #ffffff; color: #1c1f24; font-family: "DejaVu Sans Mono", "Noto Sans Mono", monospace; font-size: 8.7pt; line-height: 1.5; margin: 0; padding: 10mm 13mm 17mm 13mm; }
.pgfoot { position: fixed; bottom: 6mm; left: 13mm; right: 13mm; font-size: 7pt; color: #b6bcc3; }
.pgfoot .l { float: left; }
h1.sec { font-size: 12.5pt; page-break-before: always;} color: #111318; font-weight: bold; border-bottom: 1px solid #e3e6e9; padding: 12px 0 6px 0; margin: 14px 0 7px 0; }
h1.sec .n { background: #111318; color: #ffffff; padding: 1px 8px; border-radius: 3px; font-size: 11pt; }
h2 { font-size: 9.2pt; color: #6a737d; text-transform: uppercase; letter-spacing: 1.2px; margin: 7px 0 3px 0; font-weight: bold; }
p { margin: 5px 0; }
strong { color: #000000; }
em { color: #5c6672; font-style: normal; }
code { background: #f1f2f4; color: #1c1f24; border: 1px solid #e3e6e9; padding: 0 4px; border-radius: 3px; font-size: 8.6pt; }
ul { margin: 5px 0 8px 0; padding-left: 0; list-style: none; }
ul li { margin-bottom: 4px; padding-left: 14px; position: relative; }
ul li:before { content: "–"; position: absolute; left: 0; color: #c3c8ce; }
.meta-line { color: #6a737d; font-size: 8.4pt; margin: 2px 0 4px 0; }
.meta-line b { color: #1c1f24; font-weight: bold; }
.pipe { display: table; width: 100%; margin: 10px 0 4px 0; }
.prow { display: table-row; }
.node { display: table-cell; border: 1px solid #d4d8dc; border-radius: 6px; background: #ffffff; padding: 4px 6px; text-align: center; vertical-align: middle; }
.node .t { display: block; color: #111318; font-size: 8.2pt; font-weight: bold; }
.node .s { display: block; color: #6a737d; font-size: 7.1pt; margin-top: 2px; line-height: 1.4; }
.node.hot { background: #fff6d9; border-color: #e0cd8b; }
.node.cool { background: #e9f0fa; border-color: #bccfe6; }
.node.bad { background: #f9e7e4; border-color: #e0b5af; }
.parr { display: table-cell; vertical-align: middle; text-align: center; color: #9aa2ab; font-size: 12pt; padding: 0 4px; width: 22px; }
.vcon { text-align: center; color: #b6bcc3; font-size: 9pt; margin: 0; }
.vcon b { color: #5c6672; font-weight: normal; }
.panel { background: #f7f8f9; border: 1px solid #e3e6e9; border-radius: 6px; padding: 6px 10px; margin: 7px 0; }
.panel.key { border-left: 3px solid #111318; }
.panel.warn { border-left: 3px solid #c9a227; }
.panel .ph { font-size: 8.6pt; font-weight: bold; letter-spacing: .6px; color: #111318; }
.panel .pn { color: #6a737d; font-size: 8.2pt; margin-top: 4px; }
.official { border-left: 3px solid #dfe3e7; background: #f7f8f9; border-radius: 0 6px 6px 0; padding: 7px 11px; margin: 7px 0; font-size: 7.8pt; color: #3d454e; }
.official b { color: #111318; }
.official .src { color: #9aa2ab; font-size: 7.6pt; }
.official ul { margin: 4px 0 6px 0; }
.official li { margin-bottom: 2px; }
table.slides { border-collapse: collapse; width: 100%; margin: 4px 0 5px 0; font-size: 7.6pt; }
table.slides td { border: none; border-top: 1px solid #e9ebed; padding: 2px 6px 2px 0; vertical-align: top; }
table.slides tr:last-child td { border-bottom: 1px solid #e9ebed; }
td.sn { color: #111318; width: 30px; font-weight: bold; white-space: nowrap; }
td.st { color: #111318; width: 32%; }
td.sd { color: #5c6672; }
.tips li { margin-bottom: 2px; }
.tips li b { color: #111318; }
.cover { min-height: calc(100vh - 27mm); display: flex; flex-direction: column; justify-content: center; }
.cover .prompt { color: #8a94a0; font-size: 10pt; margin-bottom: 14px; }
.cover h1 { font-size: 31pt; line-height: 1.22; color: #111318; margin: 0; font-weight: bold; }
.cover h1 .g { color: #c9a227; }
.cover .rule { width: 72px; height: 3px; background: #111318; margin: 20px 0; }
.cover .sub { color: #5c6672; font-size: 10pt; line-height: 1.9; }
.cover .grid { display: table; margin-top: 22px; font-size: 8.4pt; }
.cover .grow { display: table-row; }
.cover .gc { display: table-cell; padding: 3px 18px 3px 0; color: #8a94a0; }
.cover .gc b { color: #1c1f24; font-weight: bold; }
.cover .foot { margin-top: 26px; color: #b6bcc3; font-size: 8pt; }
"""


def slides(rows):
    b = "".join(f'<tr><td class="sn">{n}</td><td class="st">{t}</td><td class="sd">{d}</td></tr>'
                for n, t, d in rows)
    return f'<table class="slides"><tbody>{b}</tbody></table>'


P = []
A = P.append

# ══════════ cover ══════════
A(f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{THEME}</style></head><body>
<div class="pgfoot"><span class="l">sih2026 · ps brief</span></div>
<div class="cover">
<div class="prompt">$ sih2026 --brief --per-ps</div>
<h1>What it asks.<br>What we build<span class="g">.</span><br>How we show it<span class="g">.</span></h1>
<div class="rule"></div>
<div class="sub">official description → our solution → how we build it →<br>working flowchart → PPT plan → tips. per problem.</div>
<div class="grid">
<div class="grow"><div class="gc"><b>SIH26156</b> · ULPF / NTRO</div><div class="gc"><b>SIH26076</b> · Mausam / IMD</div></div>
<div class="grow"><div class="gc"><b>SIH26087</b> · NCCT / Cooperation</div><div class="gc"><b>SIH26138</b> · Green Fleet</div></div>
</div>
<div class="foot">deadline 05 oct 2026 · october 2026</div>
</div>

<h1 class="sec"><span class="n">01</span> &nbsp;SIH26156 — ULPF · NTRO</h1>
<div class="meta-line"><b>Universal Log Pre-processing Framework</b> · Software · Blockchain &amp; Cybersecurity · 323 slots left</div>

<h2>① · what the website asks (official, condensed)</h2>
<div class="official">
<p><b>Background.</b> Enterprises generate massive log volumes — network devices, servers, OS, apps, databases, cloud, containers, endpoint tools, identity systems, IoT — in Syslog, JSON, XML, CSV, CEF, LEEF, proprietary and app-specific formats. This diversity breaks central monitoring, security ops, compliance, investigation and threat analytics. Teams hand-write parsers before SIEM, lake or ML tools can use anything.</p>
<p><b>Task.</b> Design a framework that ingests, parses, normalises and standardises logs from <b>any</b> hardware or software system — preserving originals for forensics/compliance — into one schema for analytics, correlation, visualisation, threat hunting, anomaly detection and ML. Scalable, extensible, vendor-agnostic, big-data scale (billions of events/day).</p>
<p><b>It must:</b> (a) keep raw data loss-free · (b) parse source attributes · (c) normalise to a common taxonomy · (d) trace raw↔normalised · (e) onboard new sources plug-and-play · (f) unify visibility · (g) feed SIEM + data lake · (h) be AI/ML-ready · (i) cut parser effort · <b>(j) run air-gapped</b> · (k) ship as a container.</p>
<p><b>Scope:</b> any <b>perimeter device</b> log → standardised, lossless, analytics-ready form for next-gen SIEM.</p>
<p><b>Deliverables:</b> code link · README + setup · architecture doc <b>≤ 2 pages</b> · demo video <b>≤ 2 min</b> · tech presentation <b>≤ 5 slides</b>.</p>
<div class="src">source: sih.gov.in/sih2026PS · contact via nciipc.gov.in</div>
</div>

<h2>② · what we can build — LOGSMITH</h2>
<p>A pipeline that converts any device log into the open <code>OCSF</code> standard and seals the original log inside every output — then <strong>proves nothing was lost</strong> by rebuilding the original from its own output, live. Plus: point it at 300 sample lines and it learns a new device's format by itself (with a score), and it raises an alarm when a vendor update renames a field.</p>

<h2>③ · how we build it (short)</h2>
<p>Python pipeline: format readers (syslog / CEF / LEEF / JSON) → template mining that finds each log's structure → a mapping table (versioned file) that converts fields to OCSF → every output sealed with the original bytes + checksum. A small local model only <em>suggests</em> mappings for new fields — a human approves. Control screens in React. Everything runs on CPU inside one container with no internet. Start with 5 common formats, prove it on public log samples.</p>

<h2>④ · how it works</h2>""")
A(pipe([node("RAW LOGS IN", "syslog · CEF<br>JSON · LEEF"),
        node("DECODE", "charset · codecs"),
        node("NORMALISE", "OCSF mapping<br>signed + versioned"),
        node("LOSSLESS ENVELOPE", "raw bytes + SHA-256")]))
A(vdown())
A(pipe([node("AUTO-SETUP", "300 samples →<br>proposal + score", "cool"),
        node("CHANGE RADAR", "renamed field?<br>flag + quarantine", "cool"),
        node("HUMAN APPROVES", "mapping v1.0.0<br>locked", ""),
        node("VERIFY", "rebuild raw →<br>hash match ✓", "hot")]))
A("""<h2>⑤ · PPT — 5 slides (the PS caps it here)</h2>""")
A(slides([
    ("S1", "The parser problem", "show one real mangled field, dropped by a parser"),
    ("S2", "LOGSMITH, one diagram", "the pipeline; the lossless envelope is the hero"),
    ("S3", "Live proof, our numbers", "coverage %, verify rate, onboard time - measured"),
    ("S4", "Architecture + air gap", "one container, CPU-only, zero network calls"),
    ("S5", "Deploy path + ask", "what works, what's next, the samples we need"),
]))
A("""<h2>⑥ · tips + out-of-the-box ideas</h2>
<ul class="tips">
<li><b>Verify, don't claim.</b> Rebuild-and-hash live is the whole pitch - rehearse till it cannot fail.</li>
<li><b>Rename a field mid-demo.</b> Let the radar catch it. Motion beats slides.</li>
<li><b>Never ship OCSF 2001.</b> Deprecated - current classes prove you read the standard.</li>
<li><b>Air-gap proof.</b> Network panel open, zero calls. End at the stream; never build a SIEM.</li>
</ul>""")

# ══════════ PS2 ══════════
A("""<h1 class="sec"><span class="n">02</span> &nbsp;SIH26076 — MAUSAM HOMEPAGE · IMD</h1>
<div class="meta-line"><b>Personalised homepage for the 'Mausam' mobile application</b> · Software · Smart Automation · 178 slots left — most crowded</div>

<h2>① · what the website asks (official — this persona list is the whole statement)</h2>
<div class="official">
<ul>
<li><b>Health-conscious:</b> AQI, pollen, UV, humidity — allergies, asthma, skin.</li>
<li><b>Fitness:</b> sunrise/sunset, “best running hours”, wind, heat alerts.</li>
<li><b>Beach &amp; surf:</b> sea state, tides, wave height, water temperature.</li>
<li><b>Travellers:</b> saved places, severe alerts for flights, packing hints (“carry a raincoat in London”).</li>
<li><b>Parents &amp; families:</b> school commute, rain alerts, severe warnings.</li>
<li><b>Agriculture:</b> soil moisture, rain outlook, frost alerts, planting guidance.</li>
<li><b>Commuters:</b> weather + traffic, visibility, storm/fog alerts.</li>
<li><b>Event planners:</b> extended forecast, rain probability, “comfort index”.</li>
</ul>
<div class="src">source: sih.gov.in/sih2026PS · that is the complete official text — no scope, dataset or API list beyond it</div>
</div>

<h2>② · what we can build — MAUSAM (the personalised homepage itself)</h2>
<p>The Mausam home screen, rebuilt as a decision layer: each user gets <strong>actions</strong>, not charts (“heat-wave warning + 44°C → stay indoors 12–4”). Every number tap-reveals its exact IMD source, station, issue time and age, and every advisory is deterministic enough to be re-derived by hand. Works offline on slow networks, in regional languages, and honestly says “data unavailable” where IMD publishes nothing (pollen) instead of inventing a number.</p>

<h2>③ · how we build it (short)</h2>
<p>A small Python service on a <strong>static-IP host</strong> holds the IMD API key — the key is IP-bound and every call needs a user JWT that expires hourly — and polls the 28 documented endpoints, with the public warning feed as backup. A rules engine turns fresh data into action cards with the reason attached. The home screen is an offline-first web app that caches your personal forecast on the phone, works on 2G, and reads warnings aloud for accessibility. Maps use the free Leaflet library.</p>

<h2>④ · how it works</h2>""")
A(pipe([node("IMD APIs", "28 endpoints<br>forecast · warnings"),
        node("CACHE + AGE", "every value<br>stamped"),
        node("RULES ENGINE", "data → action<br>+ the reason"),
        node("ACTION CARDS", "8 personas<br>< 15 KB bundle"),
        node("PWA", "offline · languages<br>screen-reader ok")]))
A(pipe([node("PROVENANCE", "tap any number →<br>source · station · age", "hot"),
        node("NO SOURCE? NO CARD", "“unavailable” + why<br>never a fake number", "bad"),
        node("124-YEAR HISTORY", "“4× drier than<br>the normal”", "cool")]))
A("""<h2>⑤ · PPT — the official 6-slide idea format (SIH template, title included)</h2>""")
A(slides([
    ("S1", "Title", "team · SIH26076 · exact title · MoES/IMD · Software · Smart Automation"),
    ("S2", "Problem", "eight lives, one app; IMD publishes data, not decisions"),
    ("S3", "Proposed solution", "the decision home screen; provenance toggle is the hook"),
    ("S4", "Technical approach + feasibility", "28 IMD endpoints; key + hourly JWT on a static-IP host; replayable rules"),
    ("S5", "Impact", "agri · commuter · health deep; honest gap cards; no invented stats"),
    ("S6", "Research + references", "IMD API guide, CAP/SACHET, CPCB, 124-yr climatology"),
]))
A("""<h2>⑥ · tips + out-of-the-box ideas</h2>
<ul class="tips">
<li><b>The toggle is the demo.</b> One button exposing every number's source and age.</li>
<li><b>Throttle to 2G on stage.</b> Loading from cache while rivals spin wins.</li>
<li><b>Show a gap card proudly.</b> Pollen: not published by IMD. Restraint reads as skill.</li>
<li><b>Never pitch lightning alerts as new.</b> They already ship in Mausam - IMD judges know.</li>
</ul>""")

# ══════════ PS3 ══════════
A("""<h1 class="sec"><span class="n">03</span> &nbsp;SIH26087 — COOPERATIVE ECOSYSTEM · NCCT</h1>
<div class="meta-line"><b>AI &amp; LMS-enabled capacity building, ERP &amp; employment ecosystem</b> · listed as Hardware, statement says Software + Hardware · 402 slots left — least crowded</div>

<h2>① · what the website asks (official, condensed)</h2>
<div class="official">
<p><b>Background.</b> NCCT (VAMNICOM + 5 RICMs + 14 ICMs) trains cooperative staff, PACS, SHGs, dairy co-ops, farmers, rural youth. Trained youth still can't reach jobs or visible certification. Systems are manual: no tracking, no analytics, weak job linkage.</p>
<p><b>Task.</b> One central web platform combining ERP training management + e-learning + analytics + skill development + digital literacy + employment exchange for cooperative stakeholders and rural youth.</p>
<p><b>Features demanded:</b> online registration · trainee profiles · multilingual e-learning · attendance (face/QR) · timetable/hostel/logistics · LMS + assessments + certification · certificate verification · career chatbot · employer dashboard · mobile + offline learning · central outreach database.</p>
<p><b>Tech:</b> LMS · cloud ERP · analytics · mobile apps · interactive media · face/QR. <b>Mode: Software + Hardware.</b></p>
<div class="src">source: sih.gov.in/sih2026PS · scale reference: NCCT annual report 2023-24 — 3,759 programmes, 2,27,177 trained</div>
</div>

<h2>② · what we can build — SAHAKAR SETU</h2>
<p>Skip eleven shallow tabs. Own one gap: <strong>course → proven skill → job</strong>. Skills need evidence (quizzes, practicals, attendance) — no evidence, no claim. Jobs match on proof, each gap linked to the exact NCCT course closing it. Employers log hired/rejected + why; the system learns what predicts outcomes. Certificates verify on a public page. Attendance QR-first; face optional, consented, on-device.</p>

<h2>③ · how we build it (short)</h2>
<p>Offline-first web app (no internet needed, syncs later, Indian languages) + Python back-end with trainees, courses, scores, jobs. Quizzes feed a scoring engine (skill + confidence range). Matching is rules-based and explainable. QR attendance on ordinary phones. Seed with 3 syllabi.</p>

<h2>④ · how it works</h2>""")
A(pipe([node("ENROL", ""), node("LEARN", "offline modules"), node("ASSESS", "quiz + practical"),
        node("SKILL GRAPH", "proof, not claims"), node("MATCH", "explained score"), node("HIRED?", "", "hot")]))
A(vdown("gap planner: “missing X, Y” → exact NCCT course + institute → back to enrol"))
A(pipe([node("EMPLOYER SAYS", "hired / rejected + why", "cool"),
        node("REWEIGHT", "which skills predict<br>the outcome", "hot"),
        node("GRAPH IMPROVES", "next match<br>is better", "")]))
A("""<h2>⑤ · PPT — slide by slide</h2>""")
A(slides([
    ("S1", "Scale, zero proof", "20 institutes, 2.27L trained, no verified skill"),
    ("S2", "Why portals fail", "keyword-match demo with nonsense scores"),
    ("S3", "Evidence pipeline", "the flow above, one diagram"),
    ("S4", "Graph + attestation", "skill node: evidence, confidence, fingerprint"),
    ("S5", "Explainable matching", "one match, every point accounted for"),
    ("S6", "The outcome loop", "hire/reject reasons reweight the graph live"),
    ("S7", "Offline + honesty", "QR-first, consent-led biometrics, shared devices"),
    ("S8", "Architecture", "app + API + DB, sync, public verify page"),
    ("S9", "Pilot + rollout", "match-to-interview, gap-closure, 20 institutes"),
    ("S10", "Demo + ask", "the 60-second loop; syllabus + SPOC ask"),
]))
A("""<h2>⑥ · tips + out-of-the-box ideas</h2>
<ul class="tips">
<li><b>The 60-second loop is the demo.</b> Quiz to skill to match to reject to reweight.</li>
<li><b>Lead with privacy.</b> QR-first, face optional with consent - before anyone asks.</li>
<li><b>Let a judge verify a certificate.</b> On their own phone. Checkable beats claimable.</li>
<li><b>Map 3 programmes deep.</b> Not 30 shallow. Borrow their motto: Sahakar se Samriddhi.</li>
</ul>""")

# ══════════ PS4 ══════════
A("""<h1 class="sec"><span class="n">04</span> &nbsp;SIH26138 — GREEN FLEET · EGREEN QUANTA</h1>
<div class="meta-line"><b>Quantum-inspired fuel prediction &amp; green fleet optimisation</b> · Software · Clean &amp; Green Technology · 375 slots left</div>

<h2>① · what the website asks (official, condensed)</h2>
<div class="official">
<p><b>Background.</b> Maritime and logistics face pressure to cut greenhouse gases while staying efficient and cheap. Fuel is among the largest costs and impacts. Traditional methods struggle with its high-dimensional, non-linear nature. Quantum-inspired metaheuristics (quantum search ideas, classical computers) are the proposed way forward.</p>
<p><b>Task.</b> Predict fuel use per vessel type and condition; optimise vessel mix, capacity, speed; fold in LNG, methanol, hydrogen, ammonia + shore power; minimise fuel, cost, lifecycle emissions under demand, reliability, emission rules.</p>
<p><b>Objectives:</b> quantum-inspired fuel prediction · quantum-metaheuristic fleet optimisation · minimise fuel + cost + lifecycle GHG · meet demand, reliability, regulations · <b>benchmark against conventional methods</b> (accuracy, convergence, quality, scale).</p>
<p><b>Expected:</b> a software platform — modelling, data-driven prediction, multi-objective optimisation, constraints, alternative-fuel scenarios, benchmarking with case studies.</p>
<div class="src">source: sih.gov.in/sih2026PS · context: Egreen Quanta × Mormugao Port quantum-maritime agreement, Jul 2026</div>
</div>

<h2>② · what we can build — SEAWARD</h2>
<p>Four moves: <strong>physics first</strong> (small, explainable, works on unseen ships), AI only on leftovers; <strong>CII-native optimisation</strong> (optimise the actual IMO A–E ship grade, not just fuel); <strong>honest “quantum-inspired”</strong> (classical code, checked against an exact solver on small fleets — no match, no claim); and a <strong>cliff slider</strong> showing today's best fleet illegal by 2030, re-optimised with its price.</p>

<h2>③ · how we build it (short)</h2>
<p>Python (NumPy/SciPy): ship physics (power vs speed, wind/wave/fouling), a few fitted params per ship type, gradient boosting on residuals only. A voyage simulator is the test ground — real ship data is anonymised by IMO, so the simulator <em>is</em> the honest dataset. Quantum-inspired search for mix × speed × fuel, cross-checked by exact integer programming. Front-end: map, charts, cliff slider. CPU-only, fixed seeds.</p>

<h2>④ · how it works</h2>""")
A(pipe([node("SIMULATOR", "physics ground<br>truth, published"),
        node("FUEL MODEL", "physics backbone<br>+ AI residual"),
        node("CII ENGINE", "M ÷ W<br>grades A → E"),
        node("OPTIMISER", "fleet mix<br>speed · fuel"),
        node("SCENARIOS", "fuel switch<br>shore power")]))
A(vdown("benchmark — no free lunch: exact solver vs genetic vs swarm. match the exact answer, or drop the quantum claim."))
A("""<h2>⑤ · PPT — slide by slide</h2>""")
A(slides([
    ("S1", "The maritime trilemma", "fuel cost vs emissions vs compliance"),
    ("S2", "Black boxes fail", "confidently wrong outside their training range"),
    ("S3", "Physics + residuals", "the model in one diagram; who owns what"),
    ("S4", "CII-native", "the real IMO formula; grade, not tonne"),
    ("S5", "Honest quantum", "named mechanisms, exact-solver check on screen"),
    ("S6", "The cliff deck", "2030 slider: collapse, re-optimise, capex"),
    ("S7", "Measured benchmarks", "same harness, same seeds, our table"),
    ("S8", "Architecture", "simulator as dataset, equations published"),
    ("S9", "Pilot path", "metrics, Mormugao data ask, 2027 readiness"),
    ("S10", "Demo + ask", "the slider moment; what we need next"),
]))
A("""<h2>⑥ · tips + out-of-the-box ideas</h2>
<ul class="tips">
<li><b>The slider is the demo.</b> 2030, collapse, re-optimise. One motion, whole story.</li>
<li><b>Ablation on screen.</b> Physics vs +AI vs black-box proves the architecture.</li>
<li><b>Say the data truth out loud.</b> Ship data is anonymised by design; here is our simulator.</li>
<li><b>Rs/tonne-CO2-avoided on every scenario.</b> The number ports decide on.</li>
</ul>
</body></html>""")


def main():
    (WORK / "final.html").write_text("\n".join(P), encoding="utf-8")
    subprocess.run(["chromium", "--headless", "--no-sandbox", "--disable-gpu",
                    f"--print-to-pdf={WORK / 'final.pdf'}", "--no-pdf-header-footer",
                    "file://" + str(WORK / "final.html")],
                   check=True, capture_output=True, timeout=180)
    final = ROOT / "SIH2026-Four-Solutions-TUI.pdf"
    subprocess.run(["cp", str(WORK / "final.pdf"), str(final)], check=True)
    print(subprocess.run(["pdfinfo", str(final)], capture_output=True, text=True, check=True).stdout)


if __name__ == "__main__":
    main()