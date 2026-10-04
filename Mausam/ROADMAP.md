# ROADMAP.md — from skeleton to finished model

Companion to `APP.md` (architecture), `DESIGN.md` (design contract), `PRD-SIH26076-Mausam.md`
(requirements), and `FILEMAP.md` (layout). Status: **03 Oct 2026** (amended:
activity planner & routine alerts — tickets 16–20, ADR-0002/0003).
This file is the **single source of truth for sequencing** — what ships when, and
what "done" means for each phase.

---

## 1. Where we are

| | State |
|---|---|
| **Landed** | Tickets 01–12, 14 (partial), 15 (local slice), 16, 17 (slice), 19 (local slice), 21 (Stitch UI direction) — offline mock on real IMD captures: engine + replay, personas + deep rules for held fields, provenance, gaps, sheet shell, cache-first SW, EN/HI chrome, places/routines/inbox on-device, planner presets + custom activities, 6-slide deck draft. Evidence in `docs/evidence/`. Tests: `node app/selftest.js` + `node --test tests/` (32 pass). |
| **In flight** | None. |
| **Critical path** | Static-IP host for the IMD keyed API (ticket 13) — administrative, not technical. Host-gated remainder: keyed-endpoint depth (08–10), live staleness (11), HI warning copy (12), Firebase sync (14–15), push (18), CPCB/CAMS live (20). |
| **New this cycle** | Local finale slices for 08–12, 15, 17, 19 (TDD, 32 tests green, headless smoke clean) + the planner UX pass (custom activities, tappable routine days, smart leave time); the Stitch UI direction (ticket 21: all screens, light + OLED dark, client split into `views/`, browser-verified); host-gated 13/18/20 marked `ready-for-human`. |

---

## 2. Build state by surface

Tracks the "finished prototype" definition in `APP.md` §11. `built` = visible and
verified; `partial` = some states live; `planned` = specified, not built.

| Surface | State | Ticket |
|---|---|---|
| UI — Stitch design suite (splash, onboarding, home, provenance, settings, map/places, light + OLED dark) | built (all screens; sign-in/GPS gaps stated honestly) | 21 |
| Home — hero action card | built | 01 |
| Home — provenance sheet (tap) | built (tap sheet + global toggle + raw JSON + replay) | 04 |
| Home — decision stack + sheet snaps | built (peek/half/full, opens half; auto-raise unobserved) | 06 |
| Home — persona chip / re-rank | built | 03 |
| Gap card (honesty state) | built (pollen + AQI outage; UV labelled adapter in planner) | 05 |
| Severe-warning re-rank | partial (storm rule live, unobserved in fixtures) | 06, 08 |
| Deep persona — Commuter | partial (storm + traffic-gap live; nowcast/NHAI need keyed endpoints) | 08 |
| Deep persona — Agriculture | partial (frost + soil-gap live; agromet/QPF need keyed endpoints) | 09 |
| Deep persona — Health | partial (cold + AQI/UV/pollen gaps live; codes 9–13 need keyed endpoints) | 10 |
| Offline / 2G freshness | built (cache-first SW v5 + pill + ages; expired-source labelling needs 13) | 11 |
| i18n (EN + HI) + a11y pass | partial (EN/HI chrome toggle + focus/high-contrast; warning HI copy needs review) | 12 |
| **Onboarding (language · location · persona)** | built (skippable; HI note honest) | **14** |
| **Auth / accounts (Firebase)** | partial (rules + config committed; sign-in needs project) | **14** |
| **Settings · saved places · feedback** | partial (on-device CRUD + ledger; sync/deletion need the Firebase project) | **15** |
| Live IMD keyed API | planned (host-gated) | 13 |
| Map + Places tabs | partial (schematic map panel on Home; Places local-only CRUD) | 06 |
| **Planner screen (static slice)** | built (best window + alternates + avoid + rest day; presets + custom activities, tappable days, smart leave time) | **16** |
| **Activity windows + routines** | partial (presets + custom activities + versioned weights + replay; per-day forecasts need 13) | **17** |
| **Routine alerts (scheduler · ledger · Web Push)** | planned | **18** |
| **Activities & routines UI** | partial (CRUD, week strip, stack card, inbox; push prompt needs 18) | **19** |
| **Labelled adapters (CPCB · CAMS)** | planned | **20** |

If a row is `partial`, do not describe it as complete in the deck or the README.

---

## 3. Phases and milestones

Dates are anchors against the SIH calendar (idea submission **5 Oct 2026**; finale
**Nov–Dec 2026**). "Done when" is the acceptance gate, not a vibe.

### Phase 0 — Foundation *(done)*
Repo hygiene, design tokens, real IMD fixture + capture provenance, offline shell.

### Phase 1 — Mock for idea submission *(by 5 Oct 2026)*
Deliverable: the official 6-slide deck + an offline, clickable mock on **real
captured IMD payloads**.

| Milestone | Tickets | Done when |
|---|---|---|
| Decision engine | 02 | A card and its `replay` are byte-identical from logged inputs |
| Personas | 03 | One tap re-ranks deterministically; same tap → same order |
| Provenance reveal | 04 | Tap + global toggle both expose source·station·issue·age·raw·replay |
| Honesty | 05 | A missing metric renders a real gap card in place |
| Home shell | 06 | Map + bottom sheet at 3 snap points; severe warning auto-raises |
| Deck | 07 | 3 screenshots (Home/Provenance/Honesty two-up) + 1 diagram captured |
| **Onboarding + auth** | **14** | First run ≤3 skippable steps; optional sign-in syncs a place |
| **Planner (static)** | **16** | Volleyball best-window renders from real captures; deterministic; no push |

> **Re-scope note:** ticket 14 is pulled into the mock because onboarding is the
> first thing a judge sees, and a mock without a front door does not read as a
> finished product. It stays skippable, so it never blocks the demo.

> **v1.1 note:** ticket 16 is the planner pull-forward — independent of 02–07 by
> design. **Tripwire:** if tickets 02–07 aren't green by 4 Oct evening, it drops to
> a deck design and ships at the finale instead (PRD Q23).

### Phase 2 — Finale build *(Nov–Dec 2026)*
Deliverable: the working pipeline against keyed IMD APIs, three deep personas,
provenance + replay, offline PWA, EN/HI, a11y.

| Milestone | Tickets | Done when |
|---|---|---|
| Deep personas | 08, 09, 10 | Commuter / Agriculture / Health each fill the card grammar with IMD-native inputs |
| Offline + 2G | 11 | Cold start with no network renders from cache; ages visible |
| i18n + a11y | 12 | EN + HI with human-reviewed warnings; keyboard + AA pass clean |
| Live IMD | 13 | Authenticated calls to the keyed API from the static-IP host |
| Settings + sync | 15 | Saved places + feedback sync across a reload, RLS-scoped |
| Activity windows | 17 | Same inputs → same windows; formula + excluded metrics shown; replay byte-identical |
| Routine alerts | 18 | Push arrives with the app closed; quiet hours + caps enforced; ledger replayable |
| Activities UI | 19 | Routine CRUD, week strip, inbox — guest-first |
| Labelled adapters | 20 | CPCB/CAMS normalised with provenance; gap on outage; keys backend-only |

### Phase 3 — Productisation *(post-finale, optional)*
Only if the pilot proceeds: Firestore/Redis scale, FCM warning pushes,
admin/scenario console, data-deletion flows, Firebase project region + paid
tier sizing, and the app-shell decision (native wrapper vs PWA-only).

---

## 4. Workstreams

Five parallel tracks. Anyone picking up work should know which track it belongs to.

| Track | Owns | Key files |
|---|---|---|
| **Client** | Screens, tokens, service worker, a11y | `app/*` (see `FILEMAP.md`) |
| **Engine** | Rules, ranking, replay, determinism, windows | `backend/engine/*` |
| **Data** | IMD gateway, WFS/CAP, adapters, staleness | `backend/gateway/*`, `backend/adapters/*` |
| **Identity** | Firebase auth, profiles, places, feedback, security rules | `backend/identity/*`, `app/identity/*` |
| **Docs** | This file, `APP.md`, `DESIGN.md`, `PRD`, tickets | `Mausam/*.md`, `.scratch/**` |

---

## 5. Risk register

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | Static-IP host not provisioned | High | High (critical path) | Provision it now; run the mock on public IMD WFS meanwhile | Infra |
| R2 | Vanilla JS cannot carry the sheet interaction | Low | Medium | Prototype the sheet early (ticket 06); revisit a framework only if it fails | Client |
| R3 | "Just a UI" perception | Medium | High | The replayable engine *is* the backend story; show `replay` live | Engine |
| R4 | Firebase project region latency vs backend location | Medium | Low | Co-locate the Firestore location with the host (ADR-0001 follow-up) | Identity |
| R5 | Language quality | Medium | Medium | Template-first, human-reviewed warnings; never raw MT for alerts | Docs |
| R6 | Brand overclaim | Low | Medium | Never claim official IMD brand; cite UX4G | Docs |
| R7 | Auth scope creep into reading the weather | Medium | Medium | Guest-first invariant (APP §4); auth only ever gates sync | Identity |
| R8 | `api.data.gov.in` unreachable from the production network | Medium | Medium | Validate from the static-IP host on day one; XKDR labelled mirror fallback (ADR-0002, ticket 20) | Data |
| R9 | MausamGram #27 / NHAI #21 field docs are dead anchors (undocumented endpoints) | High | Medium | Design documented fallbacks (WFS, district/station nowcast); treat hourly/highway as upside (PRD Q27) | Data |
| R10 | Notification fatigue + iOS PWA push quirks | Medium | Medium | Quiet hours + daily cap; Android Chrome demo; iOS install note (ADR-0003, ticket 18) | Client |
| R11 | Adapter quality/licence drift (SAFAR precedent) | Medium | Low | Labelled adapters only; provisional flags; gap on outage; attribution ledger (ADR-0002) | Data |

---

## 6. Ways of working

1. **Tracer bullets.** Each ticket is a thin vertical slice, not a layer.
2. **Frontier discipline.** Work the first open, unblocked ticket
   (`../docs/agents/issue-tracker.md`).
3. **Docs move with code.** A change that makes a doc false updates that doc in the
   same change (`APP.md` §12).
4. **Honest status.** `partial` is written as `partial`. Judges punish fake depth
   more than admitted scope.
5. **Determinism is a test, not a promise.** Replay byte-identity is asserted.

---

## 7. Immediate next actions

1. **Deck ownership:** the team builds the final PPT — the repo PDF is a draft reference only (ticket 07).
2. **Kick off R1** — register on `api.imd.gov.in` and stand up the static-IP host (ticket 13). This unblocks keyed depth for 08–10, live staleness for 11, 1-h grain for 17, and day-one CPCB validation (ticket 20).
3. **Firebase project** — sign-in, cross-device sync and account deletion for 14–15 (ADR-0001 follow-up).
4. **VAPID pair + Android-Chrome demo device** — routine-alert push for 18 (ADR-0003).
5. **HI warning review** — a human signs the Hindi advisory copy for 12; until then warnings stay in English.
