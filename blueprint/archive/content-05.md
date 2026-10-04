
## 7. Cross-PS Technical Strategy

### 7.1 The shared platform spine (if one team prepares multiple PS)

All four solutions share a spine: React+Vite+Tailwind PWA shell with a common design system; FastAPI service template with auth/RBAC/audit logging; Postgres + Redis + object storage; Docker Compose → single OCI image; a shared **evidence/provenance library** (content hashes, source ledgers, replay endpoints) that serves ULPF envelopes, Mausam provenance, SAHAKAR attestations, and SEAWARD benchmark seeds. Build the spine once in Phase 1; each PS becomes a different engine on the same chassis. Realistic reuse: ~60–70% of infrastructure code, ~0% of domain engines (they must stay genuinely different).

### 7.2 Neutral comparison

| PS | Solution | Core technology | Main innovation | Demo WOW moment | Main risk | MVP complexity |
|---|---|---|---|---|---|---|
| SIH26156 | LOGSMITH | Drain mining + OCSF mapping + PSI drift | Provable losslessness (reconstruct + hash) | VERIFY rebuilds raw bytes live; drift injection caught | Induction quality on adversarial formats | Medium — pipeline + 3 views |
| SIH26076 | Mausam | Rules engine over 28 IMD APIs + offline home screen | Provenance toggle + replayable advisories | Every number reveals source/age live; 2G load | Static-IP key host + crowded field (322/500) | Medium — fusion service + offline screen |
| SIH26087 | SAHAKAR SETU | Competency graph + constrained matching | Evidence skills + outcome learning loop | Live assessment → graph fill → employer match → re-weight | Syllabus-mapping effort; biometric sensitivity | High — ERP+LMS+graph+employer |
| SIH26138 | SEAWARD | Physics fuel model + QI optimiser + CII engine | CII-native optimisation + regulatory-cliff deck | 2030 slider breaks the fleet; re-optimise fixes it | No real data; quantum scepticism | High — physics + optimiser + UI |

No ranking is offered: pick by team strength (parsers/security → PS1; frontend/PWA + APIs → PS2; full-stack + Hindi content → PS3; Python/math + optimisation → PS4) and by slot pressure (PS3 is the emptiest room; PS2 the fullest).

### 7.3 Team of six — one structure, four instantiations

| Role | Owns | PS1 | PS2 | PS4 note |
|---|---|---|---|---|
| Frontend / PWA | Shell, views, offline, i18n, demo UX | Radar + inspector | PWA + toggle | Deck + maps |
| Backend ×1 | APIs, jobs, integrations | Registry + sinks | Fusion + cache | Optimiser service |
| Data / domain | Pipelines, evaluation, simulator | Codecs + corpus | IMD adapters + climatology | Simulator + physics |
| AI / optimisation | Models, validation, benchmarks | Induction + drift | Ranking + narration | Residuals + QI + MILP |
| DevOps / integration | Containers, CI, SBOM, egress tests | Air-gap proof | PWA deploy + poller | Repro harness |
| Research / presentation | Sources, PPT, video, judge Q&A | OCSF pinning | IMD liaison + key | IMO/MPA liaison |

PS3 (largest scope) borrows the second backend headcount into ERP/LMS; PS1/PS2 run lean on five.

### 7.4 Seven-phase roadmap (all four)

**P1 — Data + foundation.** Pin sources (OCSF JSON, IMD key + schemas, NCCT syllabi ×3, simulator equations). Verification-first: every A-item in Section 2.5 gets an owner and a date. Output: source ledger + sample corpora.
**P2 — Core backend.** The engine's honest core (parse→envelope; fusion→advisory; ERP→evidence; simulator→fuel). Output: API with replay/determinism.
**P3 — Intelligence.** Induction/drift; ranking/narration; IRT+matcher; residuals/QI+MILP. Output: measured validation tables (these become PPT slides).
**P4 — Frontend.** Only the screens in each blueprint's demo path. Output: clickable demo journey.
**P5 — Integration.** Sinks, caches, sync, packaging, SBOM, egress tests. Output: one-command demo environment.
**P6 — Testing.** Regression vectors, replay checks, offline/2G passes, video-script rehearsal. Output: green checklist + 2-min video.
**P7 — Demo polish.** Seeded scenarios, WOW rehearsal, 15-question drill per PS, slide freeze. Output: submission.

**Build-vs-mock discipline:** anything the WOW moment touches must be real; anything downstream of the demo (multi-node scale, full syllabus coverage, production auth, MTM-2027 modelling) is explicitly labelled future. Judges punish fake depth more than admitted scope.

### 7.5 Failure analysis (top risk per PS, with mitigation)

| PS | Biggest technical risk | Biggest data risk | Biggest adoption risk | Biggest demo risk | Mitigation posture |
|---|---|---|---|---|---|
| PS1 | Induction fails on adversarial formats | No NTRO samples available | SOC workflow inertia | Throughput challenged | Approval gates + honest EPS numbers + public-data proof |
| PS2 | Stale-cache wrong advice | Key delays; non-IMD gaps | IMD prefers in-house | "Just a UI" verdict | Replay endpoint + engine-first PPT + A2 fallback |
| PS3 | Graph cold start | Syllabus mapping scale | Institute process change | Scope overwhelm | 3-programme seed + ruthless MVP + kiosk hardware story |
| PS4 | Optimiser underperforms MILP at scale | No ship-level data, ever | Pilot data access | "Quantum" dismissed | MILP crossover shown + simulator-first + plain language |

### 7.6 Final recommendations

1. **Register for the IMD API key on day one** (PS2's critical path is administrative, not technical).
2. **Write the two data-request emails in week one** (MPA/Egreen non-sensitive data; NCCT syllabus + SPOC clarification on A1 hardware).
3. **Freeze the WOW moment per PS before writing any other UI** — every other screen serves the 60 seconds that win.
4. **Measure, don't claim**: every PPT number comes from your own validation tables (Sections 3.9/4.8/5.8/6.8).
5. **Respect the explicit deliverable caps** (PS1: 2-page architecture, 2-minute video, 5 slides) — teams lose marks ignoring format, not lacking features.
6. **Say "we don't know" once per presentation**, with the verification step attached. It is the highest-credibility sentence in a hackathon.

---

## Appendix A — Judge Q&A bank (15 per PS, condensed answers)

**PS1 — LOGSMITH.** 1. Why not Logstash? — Parses, but proves nothing, induces nothing, watches no drift. 2. Encrypted payloads? — Opaque envelope + hash; parse declared spans only. 3. Binary/proprietary formats? — Codec plugins; honest 0% coverage rather than guessing. 4. Why no LLM? — Air gap, determinism, per-event cost; small local proposer, human-gated. 5. Throughput? — Measured single-node EPS on stated hardware + partition curve; no billions/day claims. 6. Which OCSF version? — Pinned/vendored; never deprecated 2001. 7. Schema upgrades? — Migration notes + dual-version replay. 8. False drift storms? — PSI thresholds tuned on validation; quarantine is reversible. 9. Multi-line/stack-trace logs? — Framing stage with session stitching before segmentation. 10. Clock skew? — Provenance records receipt vs event time separately. 11. PII in logs? — Redaction codec lane with audit. 12. Why Kafka? — Backpressure + replay; file mode works without it. 13. Mapping conflicts? — Signed versions; only one active per source; rollback one click. 14. Cost to deploy? — Single container + commodity hardware; pilot metric for scale costs. 15. Copy risk? — Moat is the validation methodology + registry corpus, not the idea.

**PS2 — Mausam.** 1. AQI source? — CPCB adapter or labelled absence. 2. Why not OpenWeatherMap? — IMD is authoritative for India; lineage is the product. 3. IMD down? — Cached bundles + CAP floor + staleness badges. 4. Rules over ML? — Auditability; hand-re-derivable. 5. Hallucination guard? — Numbers bound to payload; LM rephrases only. 6. Languages? — Template-first, reviewed warnings; MT never for alerts. 7. Battery/data cost? — 15 KB bundles, poll-on-change. 8. Accessibility proof? — Screen-reader pass + keyboard map + contrast states in demo. 9. Personal data? — On-device ranking; saved places only, deletable. 10. Packing advice basis? — Forecast deltas + rules shown, e.g. rain PoP thresholds. 11. Meghdoot overlap? — We surface, not duplicate; agri card links advisory provenance. 12. Alert fatigue? — Severity-gated push tiers, user-set. 13. Coastal/marine accuracy? — Verbatim bulletins + cyclone cone; no interpolation claims. 14. Why would IMD adopt? — Adapter, not replacement; attribution + caching reduce their load. 15. Copy risk? — Provenance ledger + offline engine depth.

**PS3 — SAHAKAR SETU.** 1. Employer trust? — Public verify page + evidence + signatures. 2. Fake attendance? — QR nonces + confirmation + anomaly flags. 3. Biometrics concern? — QR-first; face optional, on-device, consented, deletable. 4. Vs SWAYAM/job portals? — We close assessment→hiring→outcome; they don't. 5. No-smartphone trainees? — Kiosk devices + printed QR + SMS. 6. Syllabus scale? — 3-programme seed + mapping method. 7. Cold-start matching? — Expert weights first; learning labelled future. 8. Gaming assessments? — Item banks + time-on-task + practicals; confidence reflects evidence. 9. Employer adoption? — Structured requirements cheaper than resume triage; pilot metric. 10. Language? — Indic-first content tiers. 11. Certificate fraud? — Hash chains; verification needs no phone call. 12. Rural connectivity? — Offline PWA + explicit sync conflicts. 13. Who governs data? — NCCT institutional ownership; role-based institute scoping. 14. Cost? — Commodity phones + existing infrastructure; pilot metric. 15. Copy risk? — Outcome loop + institute graph corpus.

**PS4 — SEAWARD.** 1. What's quantum? — Classical code; named mechanisms; no hardware claims. 2. Why not MILP only? — Exact at small scale (we use it); metaheuristic where MILP times out, crossover shown. 3. Training data? — No public ship-level data exists; documented simulator is the ground truth, equations shown. 4. Why CII over fuel? — Regulation prices the rating; fuel-optimal D-rated fleets fail commercially. 5. Physics accuracy? — Residual analysis by speed bin on screen; bias reported. 6. Alternative fuels? — Explicit lifecycle factors + cost; sensitivity bands. 7. Shore power? — Berth-level variable per enhanced-granularity structure. 8. Weather routing? — Added-resistance terms + scenario weather; not a routing solver claim. 9. 2027–2030 factors? — Configurable; review-dated; sensitivity shown. 10. Schedule reliability? — Buffer constraints + Pareto trade-off, not assumed. 11. Egreen's own twin? — We complement: CII-native optimisation + honest benchmarking is the layer twins lack. 12. MPA pilot path? — Data ask + SEEMP-shaped reporting + MTM readiness. 13. Black-box comparison? — Ablation on screen: backbone vs +residuals vs pure ML. 14. Compute cost? — CPU-only; wall-clock vs size curve published. 15. Copy risk? — CII engine correctness + benchmark harness + simulator corpus.

---

*Document built from the verified SIH 2026 scrape (202 open statements, scraped 2026-10-02) plus authoritative external sources cited inline. Every uncertain item is marked ASSUMPTION with a verification step. Good luck — build the WOW first.*
