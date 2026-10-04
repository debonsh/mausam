
## 5. PS3 — SIH26087 — SAHAKAR SETU: the Verified Skill-to-Job Ecosystem

**One-line pitch:** Not a job portal — an evidence pipeline that turns NCCT training into *provable* skills, matches on proof instead of keywords, and learns from every hiring outcome. *Sahakar se Samriddhi, made measurable.*

### 5.1 Problem, and why the obvious answer fails

NCCT runs one of the largest cooperative training networks in the world — 20 institutes, 227,177 people trained in a single year — and its systems are "largely manual or fragmented." The PS lists eleven features, and the failure mode is obvious: eleven shallow tabs (registration form, video page, QR attendance, job list) that digitise paperwork without changing a single outcome. A trainee still can't answer "what am I missing for the job I want, and exactly what do I do about it," and an employer still can't trust a certificate they've never seen. The product must make **the arrow between assessment and hiring** intelligent; everything else is plumbing.

### 5.2 What other teams will probably build

- An ERP clone (registration, timetable, hostel) + embedded YouTube-style videos + a job board with keyword search + a ChatGPT-wrapper "career chatbot" that gives generic advice.
- Face-recognition attendance as the headline innovation — a biometric system on rural youth with no consent, retention, or failure story. A judge *will* ask about this; most teams will have no answer.

### 5.3 How SAHAKAR SETU is different

One core — the **Competency Graph with Cryptographic Attestation** — plus honest engineering around it:

1. **Skills as evidence, not claims.** Every skill node (mapped to real NCCT programme syllabi) carries: proficiency estimate, confidence interval, and the *evidence artifacts* behind it — item-level assessment responses, module completion with time-on-task, practical submissions, verified attendance. A skill without evidence renders as "unverified" by design. Resumes are inputs; evidence is truth.
2. **Matching as constrained optimisation, not keyword cosine.** For a job posting, the matcher maximises expected fit subject to demonstrated-proficiency thresholds, prerequisite chains from the graph, region/language, and employer must-haves — and every score is *explainable*: the exact missing nodes, each linked to the specific NCCT module (down to institute and duration) that closes it. "What should I do to become job-ready?" gets a concrete answer: *this 3-week module at ICM Nagpur, then re-assess node X.*
3. **The outcome feedback loop.** Employers record hire/no-hire with reasons and (optionally) early performance; the system re-weights skill-importance per role family. The graph learns which credentials actually predict outcomes — the one thing a static portal structurally cannot do. Shown live in the admin view.
4. **Tamper-evident credentials.** Each attestation is a hash-chained record (skill, level, evidence refs, issuer, timestamp) verifiable by any employer without calling NCCT — a public verify page. No blockchain theatre required; hash chains + institutional signatures are sufficient and honestly described.
5. **Offline-first rural reality.** PWA with offline modules, assessments, and QR capture; sync with explicit conflict resolution; Indic-language content; text/light media tiers. Face attendance is **QR-first with coordinator confirmation**; face matching (on-device embedding, explicit consent, deletable, retention policy shown) is an *optional* lane — and the PPT leads with the privacy answer, not the technology.

> **JUDGE NOTE (PS3):** "Every other team matches resumes to job posts. We match *proven abilities* to job requirements — and we can show you the proof behind every single score."

### 5.4 Module map (the eleven features, competently covered, one core deep)

ERP lane: registration/nomination workflows, profiles, timetable/hostel/logistics, central outreach database. Learning lane: multilingual modules, assessments, certification repository + public verification. Employment lane: employer dashboard, postings with structured requirements, explainable matches, outcome capture. Counselling: a **grounded** guidance assistant that answers only from the trainee's own graph + NCCT catalogue ("your gap to Dairy Supervisor is nodes X, Y; the next Y-batch is…") — never generic career advice. Attendance: QR + coordinator confirm as default; face as consented option with on-device processing.

### 5.5 AI/ML components — with the "why AI?" answered

| Component | Method | Why ML / why not |
|---|---|---|
| Proficiency estimation | Item-response-style scoring over assessment evidence (per-skill ability + confidence) | Principled uncertainty: the confidence interval is the product, not the point score |
| Matcher | Constrained optimisation over the competency graph (OR-tools/CP-SAT style) | Optimisation, because requirements are constraints, not vibes; fully explainable by construction |
| Gap planner | Shortest-path over prerequisite edges to target role | Graph algorithms, exact and auditable |
| Outcome re-weighting | Bayesian/logistic update of skill weights per role family from hire outcomes | The learning loop; labelled "pilot metric" until outcome volume exists |
| Guidance assistant | Retrieval-grounded generation over trainee graph + catalogue only | Small, constrained, cited; falls back to templates offline |

### 5.6 System architecture

<div class="arch">
<div class="abox">PWA client<br><span>offline modules · QR · Indic i18n</span></div>
<div class="aarrow">→</div>
<div class="abox">API + ERP<br><span>registration · scheduling · logistics</span></div>
<div class="aarrow">→</div>
<div class="abox">LMS + Assessment<br><span>items · evidence store · IRT scoring</span></div>
<div class="aarrow">→</div>
<div class="abox">Competency Graph<br><span>skills · prereqs · attestations</span></div>
<div class="aarrow">→</div>
<div class="abox">Matcher + Planner<br><span>constrained match · gap paths</span></div>
<div class="aarrow">→</div>
<div class="abox">Employer + Admin<br><span>dashboard · outcomes · re-weighting</span></div>
</div>

**Frontend:** React PWA (+ a light USSD/SMS-adjacent notification story via standard gateways — **ASSUMPTION**: gateway access; the core never depends on it). **Backend:** FastAPI or Node; Postgres (operational) + graph represented as relational adjacency (no exotic store needed at this scale); object storage for evidence artifacts; background workers for scoring/sync. **Hardware lane (A1):** commodity Android phones as QR/attendance terminals in a kiosk mode + printed QR cards for trainees — presented as the hardware answer unless the SPOC says otherwise. **Security/privacy:** consent-first biometrics policy, on-device embeddings only, retention + deletion flows, DPDP-act-aligned data minimisation story, role-based access across 20 institutes, audit logs on attestations.

### 5.7 Demo script + WOW + PPT

0:00–0:20 problem (2.27 lakh trained, outcomes invisible); 0:20–0:40 why portals fail (keyword match demo: same resume, wildly different scores elsewhere); 0:40–1:00 SAHAKAR SETU + evidence principle; 1:00–3:30 live: trainee profile with gaps → click gap → exact NCCT module → **WOW: complete a 5-question live assessment; watch the graph node fill with confidence interval + attestation hash; the same trainee surfaces in the employer dashboard with an explainable score; employer rejects with a reason; the admin panel visibly re-weights the graph** — the full closed loop in ~60 seconds; 3:30–4:00 graph + attestation architecture; 4:00–4:30 impact (pilot metrics: match-to-interview, gap-closure, outcome prediction); 4:30–5:00 rollout across 20 institutes, offline-first.

**PPT (≤10):** 1. Scale of NCCT + invisible outcomes. 2. Why portals fail. 3. Evidence pipeline (one diagram). 4. Competency graph + attestation. 5. Explainable matching. 6. Outcome loop. 7. Offline + language + attendance honesty. 8. Architecture. 9. Pilot metrics + rollout. 10. Demo + ask.

### 5.8 KPIs, risks, judge Q&A (highlights)

KPIs: assessment→skill calibration (predicted vs observed task success), match→interview and interview→offer rates, median gap-closure time, employer return rate, offline-sync success, verification-page usage by employers. All "pilot metrics" until measured.

Top risks: (1) biometric backlash → mitigation: QR-first, consent-led, on-device, deletable — lead with this; (2) syllabus mapping effort across institutes → mitigation: seed with 2–3 flagship programmes, show the mapping *method*, not full coverage; (3) cold-start outcomes → mitigation: weights start expert-set, learning labelled as future; (4) offline-sync conflicts → mitigation: explicit, demoed conflict UI; (5) "too big to build" → mitigation: ruthless MVP boundary (Section 7 roadmap phases P1–P4 only).

Judge Q&A highlights: *Why would employers trust your certificates?* — Public verification page + evidence links + institutional signatures; trust is checkable, not claimed. *What stops fake attendance?* — QR nonces + coordinator confirmation + anomaly flags (same device, impossible travel); face only as consented option. *How is this different from SWAYAM/NAPS portals?* — Those deliver learning; we close the loop to *verified hiring outcomes*. *What about trainees without smartphones?* — Kiosk-mode institute devices + printed QR identity + SMS notifications; the trainee never needs a personal smartphone. *(12 more in the appendix.)*
