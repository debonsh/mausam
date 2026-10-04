
## 4. PS2 — SIH26076 — MAUSAM: the Personalised Decision Homepage

**One-line pitch:** The Mausam homepage, rebuilt as a provenance-first decision layer — it keeps IMD's own name and retains IMD's own data, tells eight different lives what to *do*, and lets a judge ask any number where it came from and when.

**Naming note.** The official statement asks for a *personalised homepage for the 'Mausam' mobile application*. The product therefore keeps the name **Mausam**; it is not a side app and carries no separate codename. Presenting it as the app's adaptive home screen answers the statement directly and removes any "you built a different app" objection.

### 4.1 Problem, and why the obvious answer fails

The official statement is eight personas, each needing a different slice of weather intelligence. The trap is reading "personalized homepage" as "eight dashboards of tiles." Four facts make tiles insufficient:

1. The personas need data IMD does not publish (AQI, pollen, traffic, tides, soil moisture, UV) — so personalization is a **data-fusion and honesty problem**, not a layout problem.
2. Damini (lightning) and Meghdoot (crop guidance) already ship inside Mausam — "add lightning alerts and farmer advice" is proposing what exists.
3. This is the most crowded of the four statements (322/500 submitted, 178 open).
4. **The field has already split into two shallow camps**, and both are beatable: tiles-over-a-foreign-model (most rivals silently surface a global model such as Open-Meteo under IMD branding), and generic LLM chat. Neither is IMD-authentic; neither is auditable.

### 4.2 What other teams will probably build (observed in public SIH26076 repos)

- Persona tabs of weather tiles whose real data source is a global model, not IMD — an IMD judge can spot a non-IMD number.
- A generic LLM chatbot ("Ask Mausam anything") that hallucinates AQI with full confidence.
- A competent offline-first clone with "data unavailable" gap cards. **This is now table stakes, not a differentiator** — at least two public repos already ship offline caches and honest gap cards.

### 4.3 How Mausam is different

The product is not a dashboard. It is a **decision layer** with two mechanisms and one positioning:

1. **The Provenance Toggle (the hook).** One control reveals, on every number on screen: source endpoint, station ID, issue time, and staleness. This is the visceral, demoable moment — and against a field that rebrands foreign models, it is also the integrity claim.
2. **The Replayable Advisory Engine (the depth).** A transparent rule chain consumes only documented IMD endpoints and emits *actions* with their triggering facts ("Avoid outdoor exertion 12:00–16:00 — heat-wave warning (code 9) + station max 44.6 °C"). Every advisory is deterministic: **same inputs → same card**, and a judge can hand-re-derive any card. A `replay` endpoint reproduces each advisory from logged inputs. A narration model may *rephrase* but can never *invent* a number — numbers are bound to the data payload by construction.
3. **IMD-native lineage (the positioning).** Every value is either an IMD product or explicitly labelled non-IMD. No silent substitution of a global model.

Non-IMD needs (AQI via CPCB, tides/marine beyond IMD's bulletins, traffic) enter only through a **labelled source-adapter interface**; where no public source exists (pollen is the honest example), the card shows the gap instead of a fabricated number. That restraint is itself a differentiator a judge remembers — and it is strongest on the Health persona, where three of the headline inputs are not IMD's to give.

> **JUDGE NOTE (PS2):** "Every number on this screen can tell you where it came from, when it was issued, and how old it is — and every advisory can be re-derived by hand. No weather app in India does that, including the current one."

### 4.4 The eight personas — three deep, five light

Eight personas is too many to build well. **Three are built to depth; five ship as competent labelled cards.** The three are chosen because they are the richest in genuine IMD product — and because Agriculture is the product the rival field visibly ignores.

| Persona | IMD-native products (of the 28 endpoints) | Not in IMD → honesty card |
|---|---|---|
| **Agriculture (deep)** | Agromet advisory (28, weekly text → action cards) · rainfall vs normal (5, 8, 16, 17) · river-basin QPF (10) · ground-frost warning (code 14) · AWS/ARG observations (9) | **soil moisture** → labelled gap |
| **Commuter (deep)** | **NHAI highway nowcast (21) + highway 5-day warning (22)** — the most under-used IMD product · district/station nowcast (4, 7) · fog (code 15) · lightning probability (nowcast Cat 6/11/19) | traffic → labelled adapter |
| **Health (deep)** | heat wave / hot day / warm night / cold wave / cold day (codes 9–13) · humidity · AWS temperature + "feels like" (9) | **AQI (CPCB adapter), UV (not IMD), pollen (no source)** — three gap cards, shown proudly |
| Fitness | sunrise/sunset (15) · heat alerts · wind · "best running window" from hourly risk | none — fully IMD-derivable |
| Beach & surf | sea-area + coastal + port + fishermen bulletins (11, 12, 13, 23) · cyclone track/wind/cone (18, 19, 20) | tides/water-temp → labelled or gap |
| Traveller | saved places + destination district warnings + packing rules from forecast deltas | flight status → out of scope, stated |
| Parents & families | school-commute window + rain/nowcast alerts + severe warnings | none |
| Event planners | extended forecast + rain-distribution bands + comfort index *with its formula* | none |

**Persona caveat (be honest in the PPT):** of the three deep personas, **Health is the least IMD-servable** — three of its headline inputs are not IMD's. That is why Health is retained: it is the three-gap showcase that proves the honesty thesis on one screen. Neither Agriculture nor Commuter may be described as "easy"; they are *IMD-rich*, which is different.

### 4.5 AI/ML components — with the "why AI?" answered

| Component | Method | Why ML / why not |
|---|---|---|
| Advisory Engine | Deterministic rule engine over typed IMD facts (the core intelligence) | Rules, because advisories must be auditable and reproducible — a judge can re-derive any card by hand |
| Narration layer | Small LM, retrieval-grounded, numbers bound to payload | Only for phrasing + translation; falls back to template strings offline |
| Personal ranking | Lightweight on-device scoring (which cards first for this user at this hour) | No server profile needed — personalization without a user database |
| Comfort/heat-risk index | Published heat-index + warning-code fusion, formula displayed | Transparent by design; "metric to measure during pilot" for calibration |
| Climatology delta | Gridded 0.25° normals vs current, per grid cell | Statistics, public data, citable |

Explicitly **not** used: forecast generation (IMD does that; we consume it), black-box risk scores, cloud LLMs for facts.

### 4.6 System architecture

**IMD access reality (VERIFIED, from the official IMD API Portal User Guide).** The portal at `api.imd.gov.in` exposes 28 documented endpoints, but access is gated: a registered account issues an **API key bound to the caller's static public IP**, and every request needs **both** the `X-API-KEY` header **and** a user-bound `Authorization: Bearer <JWT>` that expires hourly (`expires_in: 3600`). The portal allows **2 DEV + 2 PROD keys**, and states that API usage statistics must be shared with IMD on request. **Consequence:** the key cannot ship inside the app; a small backend on a **static-IP** host must hold it and refresh the JWT. This — not the model — is the project's critical path, and it must start on day one. Until the host exists, the clickable mock draws on IMD's public GeoServer WFS layers so that every displayed value is still genuinely IMD.

<div class="arch">
<div class="abox">IMD keyed API gateway<br><span>static-IP host · key + hourly JWT · cache · attribution ledger</span></div>
<div class="aarrow">→</div>
<div class="abox">Fusion service<br><span>normalize 28 endpoints · staleness tracking</span></div>
<div class="aarrow">→</div>
<div class="abox">Advisory engine<br><span>rules → actions + triggering facts · replayable</span></div>
<div class="aarrow">→</div>
<div class="abox">Personal bundle<br><span>per-persona ~15 KB JSON · signed</span></div>
<div class="aarrow">→</div>
<div class="abox">Offline home screen<br><span>persona-adaptive · i18n · a11y · provenance toggle</span></div>
</div>

**Frontend:** the Mausam home screen as a lightweight offline-first web app (React + Vite + Tailwind PWA, or a Compose/Dioxus shell) — Leaflet for warning/radar overlays, Workbox service worker, `prefers-reduced-motion` and forced-colors support, language packs for Hindi + 3 more (**ASSUMPTION**: translation quality via human review, never raw MT for warning text). **Backend:** FastAPI fusion/advisory service on a static-IP host; Redis for endpoint caches keyed by issue time; Postgres for saved places + feedback (no behavioural tracking beyond explicit saves); a poller that refreshes the JWT and respects rate etiquette (backoff, conditional fetch). **Data:** IMD keyed APIs; a public **CAP/RSS warning feed** as the always-available floor; gridded climatology shipped as static tiles; labelled CPCB/other adapters. **Infra:** single container + static-hostable PWA; auth only for saved places; a `replay` endpoint so any advisory is reproducible from logged inputs.

### 4.7 The 5 October deliverable — official 6-slide deck + clickable mock

The idea-submission deadline is **5 October 2026** (extended), and the format is fixed: IMD's mandated template, **a maximum of six slides including the title**, submitted as PDF, points/diagrams rather than paragraphs. So the earlier ten-slide plan is replaced. In the three days before the deadline, ship (a) the six-slide deck and (b) an **offline, clickable mock whose numbers are real captured IMD payloads** — never invented values, or the mock contradicts the one claim being sold. The mock runs from cached/snapshot IMD data and demonstrates the persona-adaptive home screen, the provenance toggle, and one gap card.

| Slide | Content |
|---|---|
| 1 · Title | Team, **SIH26076**, exact title, MoES / India Meteorological Department, Category: Software, Theme: Smart Automation |
| 2 · Problem | Eight lives, one app; IMD publishes data, not decisions; current apps show tiles and substitute a global model; scale = 1.4B users |
| 3 · Proposed solution | The persona-adaptive Mausam home screen as a decision layer; one diagram; **the provenance toggle is the hook**; replayable advisories is the depth |
| 4 · Technical approach & feasibility | 28 IMD endpoints; key + hourly JWT on a static-IP host; deterministic rules engine + `replay`; labelled adapters; offline PWA; honest 36-hour build plan |
| 5 · Impact | Agriculture, Commuter, Health built deep; honest gap cards instead of fake numbers; national scalability; qualitative Low/Medium/High — **no invented statistics** |
| 6 · Research & references | IMD API reference + Portal User Guide; CAP/SACHET; CPCB via data.gov.in; gridded climatology (Pai et al. 2014); public SIH26076 solutions reviewed, and how we differ |

### 4.8 Demo script + WOW

0:00–0:20 problem (one app, eight lives, zero decisions); 0:20–0:40 why tiles + chatbot fail (show a hallucinated AQI answer, then the gap card); 0:40–1:00 the decision layer + provenance principle; 1:00–3:30 live: pick "commuter," 2G-throttle the browser, the home screen loads from cache; a fog morning card appears with an action; **WOW: hit the Provenance Toggle — every number expands to endpoint + station + issue time + age, live**; 3:30–4:00 the advisory engine + climatology delta ("4× drier than the 30-year normal for this grid cell"); 4:00–4:30 impact (comprehension, response time, accessibility — as pilot metrics); 4:30–5:00 deployment (IMD-side host, key management, language expansion).

### 4.9 KPIs, risks, judge Q&A (highlights)

KPIs: card comprehension (can a user state the action?); time-to-decision; cache-load time at 2G; **advisory reproducibility (target 100% replay)**; translation coverage; per-endpoint staleness SLA (measured); warning-action latency from the CAP feed. No invented percentages.

Top risks: (1) **IMD key/host delay — the account exists but the static-IP host is not yet provisioned, so the keyed API cannot be called today**; mitigation: stand up the host immediately and, until then, run the mock on IMD's public WFS layers so no displayed value is non-IMD; (2) non-IMD sources missing → labelled gap cards, never fake data; (3) "just a UI" perception → the replayable advisory engine *is* the backend story; (4) language quality → template-first, human-reviewed warning strings; (5) most-crowded PS → provenance + auditability + IMD-native lineage is a defensible moat no tile-app can copy in a week.

Judge Q&A highlights: *Where does AQI come from?* — CPCB adapter, labelled, or absent with explanation. *Why not just use OpenWeatherMap/Open-Meteo?* — Because IMD is the authoritative Indian source and this is an IMD app; mixing sources without lineage is exactly the trust failure we fix. *What if IMD is down?* — Cached bundles + CAP feed + explicit staleness badges; the app degrades to "last known, age shown." *Why rules, not ML, for advisories?* — Auditability: any advisory must be hand-re-derivable in front of a judge. *Is this really a "homepage"?* — It is the app's home screen; the persona is chosen once and the home re-orders. *(12 more in the appendix.)*
