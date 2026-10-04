# SIH 2026 — Solution Blueprint

**Four problem statements. One engineering-grade plan. Zero invented facts.**

This document is a build-ready blueprint for four SIH 2026 problem statements: every claim about the problem is sourced from the official statement text or an authoritative external source, and everything uncertain is marked **ASSUMPTION** with an explicit verification step. The four problem statements were taken from a verified local scrape of the official SIH portal (`sih.gov.in/sih2026PS`, scraped 2026-10-02) and cross-checked against the organisations' own sites, public APIs, and standards bodies.

---

## 1. Executive Overview

### 1.1 The four missions

| # | PS | Organisation | Title | Slot pressure |
|---|----|--------------|-------|:---:|
| 1 | **SIH26156** | National Technical Research Organisation (NTRO) | Universal Log Pre-processing Framework (ULPF) | 177/500 submitted |
| 2 | **SIH26076** | India Meteorological Department (IMD, MoES) | Personalized homepage for the 'Mausam' mobile application | 322/500 submitted |
| 3 | **SIH26087** | National Council for Cooperative Training (NCCT, Ministry of Cooperation) | AI & LMS-enabled cooperative capacity building, ERP & employment ecosystem | 98/500 submitted |
| 4 | **SIH26138** | Egreen Quanta | Quantum-inspired fuel prediction & green fleet optimisation | 125/500 submitted |

Deadline (per official scrape, all four): **5 October 2026**. An independent third-party archive shows "30 September 2026" for SIH26076 — **ASSUMPTION**: treat 30 September as the safe date and re-verify on the official portal before submission.

### 1.2 The single most important correction in this document

SIH26138 is a **maritime shipping** problem — vessel types, capacities, cruising speeds, alternative marine fuels (LNG, methanol, hydrogen, ammonia), and shore power — not a road-fleet / EV / driver-behaviour problem. Any team that builds a truck-dashboard with EV charging stations has misread the statement. The Green Fleet blueprint in this document is built entirely around IMO regulation and naval architecture.

### 1.3 How this document is organised

1. A **verified research dossier** per PS (Section 2) — official facts, then a labelled assumption register.
2. One **deep solution blueprint** per PS (Sections 3–6), each with: product identity, problem analysis, what rival teams will build and how this differs, the out-of-the-box mechanism, full architecture (frontend/backend/AI/data/infra), MVP vs demo vs production scope, screens, a timed demo script with a WOW moment, a submission-format PPT plan, quantified KPI discipline, 15 judge questions with answers, and a risk/mitigation table.
3. A **cross-PS technical strategy** (Section 7): shared platform spine, team of six, 7-phase roadmap, build-vs-mock discipline, and a neutral comparison.

### 1.4 Reading legend

- **VERIFIED** — confirmed from the official PS text, an official organisation site, a live API reference, or a standards body.
- **ASSUMPTION** — plausible but unconfirmed; every one carries a stated verification step.
- **JUDGE NOTE** — a point phrased for direct reuse in the PPT or the demo narration.

---

## 2. Verified Research Dossier

### 2.1 SIH26156 — ULPF (NTRO)

| Field | Value |
|---|---|
| Category / Theme | Software / Blockchain & Cybersecurity |
| Submission pressure | 177 of 500 (323 open) |
| Scope (verbatim) | A framework that converts **any perimeter network device-generated** log or event — regardless of source, format, vendor, or technology — into a standardized, **lossless**, analytics-ready representation for next-generation SIEM and cybersecurity platforms |
| Hard requirements (a–k) | Preserve raw without loss · parse source attributes · normalize to common taxonomy · traceability raw↔normalized · plug-and-play onboarding · unified visibility · SIEM/data-lake integration · AI/ML-ready output · reduced parser effort · **air-gapped deployment** · container packaging |
| Contact listed | "Check nciipc.gov.in, helpdesk1@nciipc.gov.in" — i.e. the National Critical Information Infrastructure Protection Centre is the reference point |
| Deliverables (**VERIFIED**, explicitly templated) | Source code link · README with setup · **architecture document, max 2 pages** · **demo video, max 2 minutes** · **technical presentation, max 5 slides** |

Key standard (**VERIFIED**, from ocsf.io and the OCSF GitHub schema repo): the **Open Cybersecurity Schema Framework (OCSF)** is the vendor-agnostic, JSON-defined core schema for security events — categories, event classes, objects, attribute dictionary, versioned (schema 1.8.x, server 4.5.x at time of writing). Notable: the old `Security Finding [2001]` class is **deprecated** (since v1.1.0) in favour of specific classes (`Detection Finding [2004]`, `Incident Finding [2005]`, etc.). Any solution that ships 2001 events is demonstrably out of date — a small, checkable detail that signals competence.

Prototype data strategy (sensitivity-safe): use **publicly documented log formats only** — Linux audit/syslog samples, web-access logs, documented CEF/LEEF layouts, and public research collections such as the LogHub/LogPai datasets. No operational, classified, or government data is required at any point, and the demo is designed so none is ever needed.

> **JUDGE NOTE (PS1):** "We never ask for your logs. We prove the framework on public data, and we prove losslessness mathematically — by reconstructing the original bytes from the normalized event and hashing them."

### 2.2 SIH26076 — Mausam personalised homepage (IMD)

| Field | Value |
|---|---|
| Category / Theme | Software / Smart Automation |
| Submission pressure | 322 of 500 (178 open) — the most competitive of the four |
| Official statement, in full | Eight user personas with the cards each needs (health, fitness, beach, travel, family, agriculture, commuter, events) — quoted verbatim in Section 4. That persona list **is** the entire official description. There is no published background, scope, dataset, or API list beyond it. |

External verification (**VERIFIED**):

- **Mausam is real and official**: package `com.imd.masuam`, developed jointly by ICRISAT's Digital Agriculture & Youth team and IITM under the MoES Monsoon Mission; surfaces observed weather, forecasts, radar, and warnings from `mausam.imd.gov.in`.
- **Damini (lightning) and Meghdoot (farmer crop guidance) features already exist inside Mausam.** Any team that proposes "lightning alerts" or "farmer advice" as its innovation is proposing something that already ships. This is the single most important differentiation constraint on PS2.
- **IMD runs an official, documented API portal** at `api.imd.gov.in` — 28 endpoints covering city forecasts (7-day, with lat/lon), current weather, district/station nowcasts (including lightning-probability and thunderstorm-severity categories), district/subdivision warnings (heat wave, fog, ground frost among 17 codes), AWS/ARG station observations, district/state rainfall vs normals, river-basin QPF, marine/port/sea-area/coastal bulletins, cyclone track + wind + cone of uncertainty, sunrise/sunset by lat/lon, highway nowcasts, radar, and agromet advisories.
- **The APIs are key-gated** (a call without a key returns HTTP 401, "API key missing"). Accounts are self-registered with CAPTCHA + email confirmation; government organisations must use official mail; organisational terms go through IMD's nodal officer (Dr. Sankar Nath, Sc-E). **Verified operating constraint (IMD API Portal User Guide):** a key is bound to the caller's static public IP, every call needs a user-bound JWT that expires hourly (`expires_in: 3600`), and the portal allows only 2 DEV + 2 PROD keys — so the key must live on a static-IP backend, never inside the app, and usage statistics must be shared with IMD on request. No published rate limits; data licence is arranged per-organisation, not self-serve. A **CAP RSS warning feed is public domain.**
- **IMD Pune publishes 124 years (1901–2024) of daily gridded rainfall at 0.25° resolution** (135×129 grid), citable as Pai et al. 2014 — a legitimate, public climatology baseline for any "normal vs now" comparison the blueprint proposes.

The structural gap every team must face: the personas demand data **IMD does not produce** — AQI, pollen count, traffic, tides, soil moisture, packing advice. A serious solution therefore cannot be "more tiles." It must be a **decision and provenance layer** that derives advisories from what IMD actually publishes, marks every non-IMD input with its source, and degrades gracefully when a source is absent. That honest constraint is the core of the Section 4 design.

### 2.3 SIH26087 — Cooperative training, ERP & employment (NCCT)

| Field | Value |
|---|---|
| Category / Theme | Listed as **Hardware** in the portal, but the statement itself says "Proposed Mode: **Software + Hardware**" — plan for both, and clarify the hardware (QR/attendance capture device) early in the PPT |
| Submission pressure | 98 of 500 (402 open) — the least crowded of the four |
| Organisation | NCCT, an autonomous society under the Ministry of Cooperation; network of **20 institutes**: VAMNICOM Pune (national), 5 RICMs (Chandigarh, Bengaluru, Kalyani, Gandhinagar, Patna), 14 ICMs, plus ~109 junior training centres academically supported |
| Scale evidence (**VERIFIED**, NCCT annual report 2023-24) | 3,759 programmes, **227,177 participants trained** in one year; VAMNICOM alone exceeded its 10,000-participant target by 185%. The "existing system" is a vast, working, human institution — the proposal must augment it, not replace it. Motto: **"Sahakar se Samriddhi"** (prosperity through cooperation) |
| Required feature set (verbatim from PS) | Online registration/nomination · participant/institution/trainee profiles · multilingual e-learning · digital attendance (face/QR) · timetable/hostel/logistics · LMS + assessments + certification · certification repository + verification · career counselling chatbot · employer dashboard · mobile-friendly + offline learning · central database for outreach/monitoring |

The strategic reading: the PS lists **eleven features**. Every rival team will build eleven shallow tabs. The winning move is to pick the pipeline the features imply — nomination → training → assessment → **verified skill** → match → hire → outcome feedback — and make the *arrow between assessment and match* the product. Everything else becomes competent-but-ordinary plumbing around one genuinely intelligent core.

### 2.4 SIH26138 — Quantum-inspired green fleet optimisation (Egreen Quanta)

| Field | Value |
|---|---|
| Category / Theme | Software / Clean & Green Technology |
| Submission pressure | 125 of 500 (375 open) |
| Organisation (**VERIFIED**) | Egreen Quanta is a real quantum-technology startup (founder-director Dr. Kumar Gautam). In July 2026 it signed a **Strategic Quantum Technology for Port Innovation Agreement with the Mormugao Port Authority** — quantum vessel scheduling, cargo-handling optimisation, AI analytics — with MPA providing **non-sensitive operational data and pilot support** under the Sagarmala / PM Gati Shakti / Green Shipping missions. The company publicly frames future ports as observation→prediction→optimisation→simulation→action loops around **digital twins** |
| The five objectives (paraphrased from PS) | Quantum-inspired fuel-consumption prediction across vessel types/conditions · quantum metaheuristic fleet-mix/speed optimisation · minimise fuel, cost, lifecycle GHG · satisfy cargo demand, reliability, emission rules · **benchmark against conventional methods** on accuracy, convergence, quality, scalability |

Regulatory ground truth (**VERIFIED**, IMO):

- **CII (Carbon Intensity Indicator)** is mandatory since 1 Jan 2023 for ships ≥5,000 GT: attained CII = CO₂ mass ÷ transport work, rated **A–E**, with corrective-action plans required for E (1 year) or D (3 consecutive years). The 40%-by-2030-vs-2008 trajectory is the binding context; the CII review and the 2027–2030 reduction factors were due for adoption by 1 Jan 2026 — **ASSUMPTION**: treat factor values as configurable inputs, not constants.
- Ship-level **IMO DCS data is anonymised and aggregate; individual ships are not identifiable.** There is no public ship-level training dataset. Any team claiming "we trained on real fleet data" without a data agreement should be assumed to be bluffing. The honest, winning answer is a **physics-calibrated simulator** documented as such.
- **MEPC.385(81) enhanced granularity** (fuel per consumer type, in-port vs underway split, shore power supplied, laden distance) applies from 2026 reporting — the exact variables a serious model needs, which makes a physics-plus-residual architecture uniquely well-timed.
<div class="callout warn"><strong>Critical anti-hallucination boundary (PS4)</strong><br>No real quantum computer is used or needed. "Quantum-inspired" means classical metaheuristics that borrow quantum concepts (superposition-inspired population states, rotation-gate updates), and the blueprint benchmarks them against an exact MILP baseline on small instances — because a team that cannot beat a MILP on 6 ships has no business claiming quantum advantage.</div>

### 2.5 Assumption register (all four)

| # | Assumption | Verify by |
|---|------------|-----------|
| A1 | SIH26087 hardware expectation is satisfied by a QR/attendance capture flow on commodity phones, not custom electronics | Ask the SPOC / read the "Delivery Table" template if one is published |
| A2 | IMD API keys are obtainable by a student team within weeks, and a static public IP can be provisioned (self-registration, not gov email) | Register on api.imd.gov.in **and** provision a static-IP host on day one — the key is IP-bound and every call needs an hourly JWT; if blocked, run the mock on IMD's public GeoServer WFS + cached CAP RSS + gridded climatology |
| A3 | No operational access to MPA/Egreen data exists for the hackathon window | Write to the PS contact early; design the simulator-first architecture so the answer works either way |
| A4 | OCSF 1.8.x attribute/class surface used in code | Pin the vendored `dictionary.json` + `categories.json` in the repo at build time |
| A5 | Judging constraints: 5-slide PPT and 2-minute video for ULPF are explicit; the SIH **idea submission** is a separate artifact — the mandated SIH template, **max 6 slides including the title**, in PDF | Use the official SIH2026 idea template for the 5 Oct submission; keep the PS-specific caps (e.g. ULPF's 5 slides) for the finale deck |

---

## 3. PS1 — SIH26156 — LOGSMITH: the Lossless Log Fabric

**One-line pitch:** A vendor-agnostic log pipeline that converts any perimeter-device log into OCSF events, and *proves* — byte for byte — that nothing was lost.

### 3.1 Problem, and why the obvious answer fails

SOC teams don't suffer from a shortage of parsers. They suffer from three specific, expensive pains: (1) every new device needs a hand-written parser (~days of regex work) before a single alert can fire; (2) parser outputs silently drop or mangle fields, and nobody notices until an incident review; (3) schemas drift — a vendor firmware update renames a field and downstream detections quietly go blind. Generic answers ("a universal parser with regex + Grok patterns") address none of these verifiably.

### 3.2 What other teams will probably build

- A Grok/regex pipeline (Logstash-style) that maps Syslog + CEF + a few JSON formats to a flat schema.
- "AI log parsing" that calls a cloud LLM per log line — undemonstrable in an air gap, unscalable, and a privacy non-starter for NTRO.
- A dashboard with pretty charts over parsed logs, where "lossless" is asserted in a bullet point.

### 3.3 How LOGSMITH is different

Three mechanisms, each directly aimed at a pain above — and each *demonstrably* working in the demo:

1. **The Losslessness Contract.** Every normalized event is wrapped in an envelope containing the original bytes (or a pointer + length), a SHA-256 of the raw event, the mapping version, and a field-level provenance map (which output attribute came from which input span). A standalone `verify` tool **reconstructs the original bytes from the normalized record and compares hashes**. Lossless stops being a claim and becomes a passing test. **This is the product's USP in one sentence.**
2. **Zero-shot source onboarding.** Drop 200–500 sample lines from an unseen device. The induction engine — Drain-style template mining, type clustering, and a *local, CPU-only* field-name→OCSF-attribute proposer constrained to the schema's type system — emits a versioned mapping plus a held-out validation report: per-field precision/recall, coverage %, and a confidence score. A human approves with one click (human-in-the-loop by design).
3. **The Drift & Coverage Radar.** Every mapping continuously reports parse coverage and per-field value-distribution statistics (Population Stability Index vs the validated baseline). When a firmware change renames `src` to `src_ip`, the radar flags the drift event, quarantines affected events under the old mapping version, and routes them for re-induction — detections never silently go blind.

Supporting mechanisms: OCSF-native output with pinned schema version (never the deprecated 2001 class); offline GeoIP/asset enrichment from bundled databases; CEF/LEEF/JSON/XML/key-value/syslog codec library; air-gap packaging as a single OCI image with SBOM and a live "zero external calls" proof; mapping registry with signed versions and regression test vectors.

> **JUDGE NOTE (PS1):** "Every other parser says 'lossless.' We are the only team that can *prove* it, live, in front of you, by rebuilding the original log from our output."

### 3.4 Core features (mapped to requirements a–k)

| Requirement | LOGSMITH answer |
|---|---|
| (a) preserve raw | Raw bytes + SHA-256 in every envelope; optional external blob store for scale |
| (b) parse attributes | Drain-template mining + codec library + regex assist for the long tail |
| (c) normalize taxonomy | Versioned OCSF mappings; `metadata.product` always set; schema version pinned |
| (d) traceability | Field-span provenance map + mapping version + content hash per event |
| (e) plug-and-play onboarding | Sample-drop induction flow with validation report and one-click approval |
| (f) unified visibility | Coverage/drift radar per source; unified OCSF event stream for all sinks |
| (g) SIEM / lake integration | Kafka + HTTP/OTLP + OpenSearch + Parquet-on-S3 sinks; OCSF JSON is the contract |
| (h) AI/ML-ready | Typed, schema-stable stream + documented residual/anomaly example (Isolation Forest on OCSF features) |
| (i) reduced parser effort | Measured: mapping induction in minutes with a reported score, vs hand-written rules |
| (j) air-gapped | Single container, offline assets, SBOM, zero-egress test in CI |
| (k) container | OCI image; compose file for SIEM-side services |

### 3.5 AI/ML components — with the "why AI?" answered

| Component | Model / method | Input → output | Metric | Why ML is necessary; fallback |
|---|---|---|---|---|
| Template mining | Drain-style fixed-depth parse tree (deterministic algorithm, not a model) | Raw lines → log templates + parameter slots | Templates discovered; tokens stabilised | No fallback needed — offline and deterministic |
| Field→OCSF proposer | Small local embedding model + cosine over OCSF attribute descriptions + type compatibility rules, CPU-only | Unseen field name + sample values → ranked OCSF attribute candidates | Top-3 accuracy on held-out known mappings | Fallback: pure rule/lexical matching; output is always a *proposal* a human approves |
| Type clustering | Shape-feature vectors + HDBSCAN-style clustering | Raw values → inferred semantic types (ip, port, ts, user, path…) | Cluster purity on labelled sample | Fallback: regex type library |
| Drift detection | PSI / chi-square on per-field distributions (statistics, not ML) | Live stream vs baseline → drift events | Detection latency; false-drift rate | Deterministic, no fallback needed |
| Demo anomaly layer | Isolation Forest on normalized OCSF numeric/categorical features | OCSF stream → scored anomalies for the "AI-ready output" proof | Precision@k on injected anomalies | Clearly labelled as demonstration of *output usability*, not a production detector |

No cloud LLM anywhere in the pipeline. Say this on slide 1 of the architecture.

### 3.6 System architecture

<div class="arch">
<div class="abox">Collectors<br><span>file · syslog UDP/TCP · Kafka · container logs</span></div>
<div class="aarrow">→</div>
<div class="abox">Framing + Decode<br><span>charset detect · CEF/LEEF/JSON/XML/KV codecs</span></div>
<div class="aarrow">→</div>
<div class="abox">Segmentation<br><span>Drain-tree templates · parameter slots</span></div>
<div class="aarrow">→</div>
<div class="abox">Extraction<br><span>typed fields + shape clustering</span></div>
<div class="aarrow">→</div>
<div class="abox">OCSF Mapper<br><span>versioned YAML · approval gate</span></div>
<div class="aarrow">→</div>
<div class="abox">Lossless Envelope<br><span>raw + SHA-256 + provenance</span></div>
<div class="aarrow">→</div>
<div class="abox">Sinks<br><span>Kafka · OTLP/HTTP · OpenSearch · Parquet</span></div>
</div>

Side-plane (control): **Mapping Registry** (signed, versioned mappings + regression vectors), **Coverage/Drift Radar** service, **Verify tool** (reconstruction + hash check), **Induction UI**. State in PostgreSQL; stream backpressure via Kafka; exactly-once semantics through idempotent `event_uid` derived from the content hash.

**Frontend:** React + Vite + Tailwind — three views only: Onboarding (drop samples → proposed mapping → validation report → approve), Radar (per-source coverage, drift timeline, quarantined events), Event Inspector (raw bytes, envelope, OCSF JSON, provenance spans, verify button). Restraint here is a feature: fewer screens, deeper proof.

**Backend:** FastAPI (control plane + induction jobs), Go or Rust optional for the hot parse path (**ASSUMPTION**: keep the hot path in Python with multiprocessing first; port only if the 100k logs/sec claim needs defending — benchmark honestly and report the number you actually measured). Workers: Celery/RQ or plain asyncio queues. Storage: Postgres (mappings, baselines, provenance index) + filesystem/S3 Parquet for raw blobs at scale.

**Data pipeline:** sample ingest → charset/line detection → codec decode → template mining → field typing → mapping proposal → held-out validation → human approval → versioned publish → live stream with coverage + PSI drift → quarantine + re-induction loop.

**Security architecture:** no log content ever leaves the box; content hashes only for dedup; RBAC on registry approvals; signed mapping artifacts; audit log of every mapping change (who approved what, when); SBOM + pinned base images; CI egress test proving zero external calls; secrets via env/file mounts, never in mappings.

**Scalability story:** stateless parse workers behind Kafka partitions; envelope design keeps reconstruction local (no cross-event joins); Parquet partitioning by source×hour; drift statistics are sketch-based (count-min / t-digest style aggregates) so memory is bounded. Target honestly: report measured single-node EPS and the partition-scaling curve.

### 3.7 Product name, user journey, screens

**LOGSMITH — the Lossless Log Fabric.** The analyst journey: (1) a new firewall arrives → drop 300 sample lines; (2) the induction report shows 97.4% coverage, 3 flagged fields, top-3 OCSF proposals each; (3) approve → mapping v1.0.0 signed and live; (4) radar shows coverage holding at 99%+; (5) firmware Tuesday renames a field → drift event fires, affected events quarantined *with raw preserved*; (6) re-induction produces v1.1.0, regression vectors pass, detections resume. The demo compresses this into 4 minutes with a pre-seeded unseen device.

### 3.8 Implementation roadmap (7 phases) + team split + build-vs-mock

| Phase | Output | Owner |
|---|---|---|
| P1 data + foundation | Codec library (syslog/CEF/LEEF/JSON/KV), OCSF vendor pin, sample corpus, envelope spec | Data + backend |
| P2 core backend | Collectors → segmentation → mapper → sinks; registry + Postgres | Backend ×2 |
| P3 induction + radar | Template miner, proposer, validation harness, PSI drift service | AI/ML + backend |
| P4 frontend | Three views; verify/inspector UX | Frontend |
| P5 integration | Kafka→OpenSearch→notebook round trip; container build; SBOM | DevOps/integration |
| P6 testing | Regression vectors per mapping; 2-min video script rehearsal; egress test | All |
| P7 demo polish | Seeded unseen device; drift-injection script; 5-slide deck | Research/presentation + all |

**Must actually work:** ingest → normalize → envelope → verify → radar. **May be mocked:** SIEM-side correlation rules, multi-node clustering numbers (report single-node + projection, labelled as such).

### 3.9 Demo script (3–5 min) + WOW + PPT

0:00–0:20 problem (analysts write parsers, parsers lie silently); 0:20–0:40 why regex-logstash fails (drift blindness, lossy drops); 0:40–1:00 LOGSMITH + the contract; 1:00–3:30 live: onboard an unseen device → show validation scores → **WOW: hit VERIFY and watch the original log bytes rebuilt from the normalized event with matching hash — then inject a firmware field-rename and watch the radar catch it live**; 3:30–4:00 local-CPU induction + air-gap proof (network panel: zero calls); 4:00–4:30 impact (parser effort minutes not days; quarantine instead of blindness); 4:30–5:00 path to production (signed mappings, regression CI, Kafka scale-out).

**PPT (5 slides, hard limit — VERIFIED requirement):** 1. The parser problem + drift blindness. 2. LOGSMITH: contract + induction + radar (one diagram). 3. Live proof (verify + coverage numbers from your own runs). 4. Architecture + air-gap packaging. 5. Deployment path (what's real, what's next, what we need from NTRO — e.g., format samples under NDA-free terms).

### 3.10 KPIs, risks, judge Q&A (abridged here; full set in appendix table)

KPIs (measured, never invented): induction coverage % + per-field precision/recall on held-out samples; time-to-onboard (minutes); single-node events/sec; verify pass rate (must be 100%); drift detection latency; quarantine correctness. **"Metric to measure during pilot"** for anything requiring NTRO's real traffic.

Top risks: (1) induction scores poorly on truly adversarial proprietary formats → mitigation: regex-assist lane + human approval gate, scores reported honestly; (2) throughput claims questioned → mitigation: publish measured EPS on stated hardware, never claim billions/day without a cluster you don't have; (3) OCSF version drift → mitigation: pinned, vendored schema + migration notes; (4) air-gap dependency leakage (Python wheels, GeoIP updates) → mitigation: vendored wheels, bundled DB, CI egress test; (5) scope temptation (building a SIEM) → mitigation: hard boundary — LOGSMITH ends at the normalized stream.

Judge Q&A highlights: *Why not Logstash?* — Logstash parses; it doesn't prove losslessness, induce mappings, or watch drift. *How do you handle encrypted/compressed payloads?* — Envelope carries them opaquely with hashes; parsing applies only to declared plaintext spans. *What if the vendor format is binary/proprietary?* — Codec plugin interface + induction over decoded samples; if it can't be decoded, the system says so with a coverage score of 0 rather than guessing. *Why no LLM?* — Air gap, determinism, cost per event; the proposer is a small local model and every output is human-gated. *(12 more in the appendix.)*
