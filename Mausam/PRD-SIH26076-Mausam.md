# PRD — SIH26076: Personalised Homepage for the 'Mausam' Application

| Field | Value |
|---|---|
| Problem statement | **SIH26076** — "Development of personalized homepage for 'Mausam' mobile application" |
| Organisation | Ministry of Earth Sciences (MoES) / **India Meteorological Department (IMD)** |
| Category / Theme | Software / Smart Automation |
| Idea-submission deadline | **5 October 2026** |
| Finale | Nov–Dec 2026 (36-hour build at nodal centre) |
| Document status | **v1.2 — amended 04 Oct 2026** (v1.1 adds Activity Planner & Routine Alerts; v1.2 adds grounded AI Chatbot Assistant Q29–Q31, FR-21–FR-27). v1.0/v1.1 decisions remain in force. |
| Companion docs | `../blueprint/content-02.md` (blueprint detail), `../blueprint/build_final.py` (PS brief), `../docs/adr/0001-firebase-auth.md`, `../docs/adr/0002-labelled-adapters.md`, `../docs/adr/0003-routine-alert-transport.md` |

---

## 1. Summary

**One line:** *The Mausam home screen that tells you what to do — and proves where every number came from.*

We do **not** build a new weather app. We rebuild the **home screen of IMD's own Mausam app** as a persona-adaptive **decision layer**: it turns IMD's official data into *actions* rather than charts, and it makes every number traceable to an IMD source, station, issue time, and age. Where IMD publishes nothing (pollen), it says so instead of inventing a number; where an official Indian source exists outside IMD (CPCB AQI), it shows that value **explicitly labelled**.

**v1.1 addition — Activity Planner & Routine Alerts:** the home also answers *when* to do things. A deterministic **window engine** scores the day in blocks ("best time to play volleyball — 17:00–19:00"), and **routine alerts** push the same logic to the user on schedule ("leave by 06:40 — rain reaches your route at 07:00"). Every window and alert obeys the same provenance and gap rules as the cards.

## 2. Problem & context

- The official statement is **only** a list of eight personas (health, fitness, beach/surf, travel, family, agriculture, commuter, events) and the cards each needs. There is no background, dataset, scope, or API list.
- The real difficulty is that the personas want data **IMD does not produce** — AQI, pollen, traffic, tides, soil moisture, UV. So personalisation is a **data-fusion and honesty problem**, not a layout problem.
- Two features the app already has — **Damini** (lightning) and **Meghdoot** (agromet advisory) — mean "add lightning alerts / farmer advice" is proposing what exists.
- This is the **most crowded** of the four PS (322/500 submitted, 178 open). Public rival repos already ship persona tabs, offline caches, and even per-card source lines — so those are table stakes, not a moat.

**Field reality (verified):** most rival "Mausam" apps surface a **global model (e.g., Open-Meteo)** under IMD branding, and the IMD keyed API is avoided. The opening is **IMD-native lineage + auditability**.

## 3. Goals & non-goals

**Goals**
1. Replace IMD's home with a persona-adaptive surface that outputs **actions, not charts**.
2. Make **every number traceable** (source · station · issue time · age) — the *provenance toggle*.
3. Make every advisory **deterministic and replayable** (same inputs → same card; hand-verifiable).
4. Be **offline-first** on 2G, **multilingual**, and **accessible** by construction.
5. **Never fabricate a number.** Show an honest gap card where data does not exist.
6. Turn the same data into **timed decisions** *(v1.1)* — best windows for activities and schedule-aware routine alerts.

**Non-goals**
- Not a new standalone weather app; not a forecast generator (IMD forecasts; we consume).
- Not a SIEM-style analytics suite.
- **The chatbot is a grounded help layer only — it never generates weather facts, forecasts, or advisories.**
- No black-box risk scores; no cloud LLM inventing facts.
- Not full feature parity with every Mausam section (radar, satellite, aviation) — those stay in the existing app.

## 4. Target users (personas)

**Three built deep; five ship as competent labelled cards.** Deep personas are chosen for IMD-data richness; **Agriculture** is the product the rival field visually ignores. *(v1.1: activities and routine alerts live **inside** personas as presets — Fitness → volleyball/run/walk; Commuter → office routine.)*

| Persona | IMD-native inputs | Gap handled how |
|---|---|---|
| **Agriculture** (deep) | Agromet advisory (API 28) · rainfall vs normal (5, 8, 16, 17) · basin QPF (10) · ground frost (code 14) · AWS obs (9) | soil moisture → labelled gap |
| **Commuter** (deep) | NHAI highway nowcast (21) · highway 5-day (22) · district/station nowcast (4, 7) · fog (code 15) · lightning probability | traffic → labelled adapter; office routines drive routine alerts (Q26, v1.1) |
| **Health** (deep) | heat wave / hot day / warm night / cold wave / cold day (codes 9–13) · humidity · AWS temp + "feels like" | **AQI → CPCB (labelled)** · **UV → CAMS (labelled)** · **pollen → gap card** (the honesty showcase, v1.1) |
| **Fitness** (v1.1: activity windows) | sun/moon (15) · heat alerts · wind · best-window engine (FR-18) | UV → CAMS adapter (labelled) · AQI → CPCB adapter (labelled) |
| Beach & surf | sea-area/coastal/port/fishermen bulletins (11–13, 23) · cyclone (18–20) | tides/water temp → labelled/gap |
| Traveller | saved places · destination district warnings · packing rules | flight status → out of scope |
| Parents | school-commute window · rain/nowcast alerts · severe warnings | none |
| Events | extended forecast · rain-distribution bands · comfort index (formula shown) | none |

## 5. Product principles

1. **IMD-native.** Every value is an IMD product, or explicitly labelled non-IMD.
2. **Provenance is a feature, not a footer.** Source, station, issue time, age on demand.
3. **Honest gaps.** No source → gap card, never a fabricated number.
4. **Auditable.** Advisories re-derivable by hand; a `replay` endpoint reproduces them.
5. **Offline-first.** Cache the personal bundle; degrade to "last known, age shown".
6. **Accessible & multilingual.** Not stretch goals.
7. **Timed, not just ranked** *(v1.1)* — windows and alerts are first-class outputs; determinism, provenance, and gap rules apply to them unchanged.

## 6. Key user stories

- As a **commuter**, I open the app and the top card tells me to leave earlier because of fog, with the warning code and station behind it.
- As a **farmer**, I see this week's agromet advisory as concrete actions and how this season compares to the 30-year normal for my grid cell.
- As a **health-conscious user**, I see a heat-wave action and a *pollen gap card* that explains IMD doesn't publish it.
- As a **volleyball player** *(v1.1)*, I open the planner and see today's best window — and why the alternatives lose: heat index, humidity, wind, AQI, UV, each with its source.
- As an **office worker** leaving at 07:00 *(v1.1)*, I get an alert at 06:30: rain reaches my corridor at 07:00 — leave by 06:40 — with the warning code and station behind it.
- As a **skeptic/judge**, I tap any number and see exactly where it came from and how old it is — and I can replay the advisory.
- As a **user on 2G**, the home loads from cache instantly and every value shows its age.

## 7. Functional requirements

**Persona & home**
- **FR-1** Onboarding lets a user select one or more personas; the home reorders accordingly; a chip row switches persona.
- **FR-2** Home presents a **decision stack**: a hero "do this now" action, then a ranked list of action cards.
- **FR-3** Per-persona reordering is deterministic and demoable.

**Action cards**
- **FR-4** Every card uses one fixed anatomy: **imperative action headline** + **triggering facts** (e.g. warning code, station value) + **source/age chip** + optional CTA.
- **FR-5** Cards are generated by the advisory engine; every card carries its triggering inputs.

**Provenance**
- **FR-6** Tapping any number opens an inline **provenance sheet**: endpoint, station ID, issue time, age.
- **FR-7** A global **provenance toggle** in the app bar reveals source chips on every number at once.

**Honesty**
- **FR-8** A missing metric renders an **inline gap card** ("not published by IMD — here's why"), in place of the value.

**Advisory engine**
- **FR-9** Rules consume only documented IMD endpoints and emit actions + triggering facts.
- **FR-10** A `replay` endpoint reproduces any advisory byte-identically from logged inputs.

**Offline & freshness**
- **FR-11** Each value shows an **age badge**; a global "last updated / offline" strip is shown.
- **FR-12** The personal bundle (~15 KB JSON) is cached and loads on 2G from cache.
- **FR-13** Missing/expired sources degrade to "last known, age shown" — never silent emptiness.

**Language & accessibility**
- **FR-14** Warning text is template-first, human-reviewed (never raw MT for alerts).
- **FR-15** Screen-reader pass, keyboard map, high-contrast severe-weather states.

**Accounts & sync** *(amended 03 Oct 2026 — see Q20 and `../docs/adr/0001-firebase-auth.md`)*
- **FR-16** Onboarding and the home are fully usable **signed-out** (guest-first); an account only enables cross-device **sync of saved places** and **opt-in feedback**, and the user can **delete their account and rows**. No behavioural tracking is introduced.

**Activity planner & routine alerts** *(added v1.1 — Q21–Q28)*
- **FR-17** Activities are **presets inside personas**; routines (activity · days · departure/return · optional places) are **explicitly user-entered**, stored on-device, and never behaviourally inferred. Guest-first.
- **FR-18** A deterministic **window engine**: hard gates (IMD nowcast categories; heat-wave/heat-index bands) then a **versioned weighted comfort score** over the best available resolution; windows are daylight-constrained (sun/moon). The formula, weights, and any **excluded (gap) metrics** are shown with the value.
- **FR-19** **Routine alerts**: evening "tomorrow plan" digest (default 21:00), departure alert (default T−30 min), and an immediate override for **IMD orange/red warnings only**. Quiet hours and a daily cap are enforced; permission is requested at first routine creation; the in-app inbox always carries every alert; every alert is appended to a **notification ledger** and replayable (extends FR-10).

**Labelled adapters** *(added v1.1 — ADR-0002)*
- **FR-20** Non-IMD values come only from **labelled adapters**: IMD first; then official-Indian sources (CPCB AQI via `data.gov.in`; XKDR mirror labelled when CPCB is unreachable); then a labelled public-institution source where India has none (**Copernicus CAMS** for UV). Safety-critical triggers are **IMD-only**; no source → gap card. No unlabelled model data, ever; `app.cpcbccr.com` is never used.

## 8. UX / UI specification

### 8.1 Information architecture (research-driven)

The **real Mausam home is map-centric with a bottom sheet** (latest stores release note: auto-opening bottom sheet by current location). To stay faithful to the app *and* deliver personalisation, the home is:

> **Map context (top) + persona-adaptive decision stack (bottom sheet).**

Swiping the sheet up reveals the ranked action stack; the map carries warning overlays. This preserves IMD's paradigm and reframes "personalisation" as the sheet reordering per persona. *(Decision Q2/D1 — see §14.)*

### 8.2 Screens (mock scope)

1. **Onboarding** — language · location · persona, three skippable steps (ticket 14).
2. **Home** — map + decision-stack bottom sheet (per persona).
3. **Provenance sheet** — tap a number → source/station/issue/age.
4. **Gap card** — inline honesty state (pollen; adapter outages).
5. **Persona chip row** — switch persona; deterministic re-rank.
6. *(optional)* **Auth** — passwordless email link / OAuth, reached from Settings; guest-first (ticket 14).
7. *(optional)* **Settings** — profile · saved places · feedback (ticket 15).
8. **Activities & routines** *(added v1.1)* — planner windows, routine setup, week strip, notification inbox (tickets 16/17/19).

### 8.3 Action card anatomy (fixed component)

```
┌───────────────────────────────────────────────┐
│  Leave 20 minutes early                       │  ← imperative action
│  Fog warning (code 15) · visibility 400 m     │  ← triggering facts
│  IMD district warning · 05:30 IST · 2 h old   │  ← source + age chip
└───────────────────────────────────────────────┘
```

The window card uses the same anatomy with a window headline (A.8).

### 8.4 Visual identity

- **No official IMD/Mausam brand guide exists**; "IMD Deep Blue `#003366`" is a team invention, not guidance. Use a **hybrid**: a documented government/authority blue palette with a modern layout, and **do not claim official brand compliance**.
- Reference MeitY's **UX4G** national design system (which hosts a Mausam case study) as the design authority.
- Design tokens in the mock are labelled as *our* system.

### 8.5 States

`Ready` (value + provenance) · `Stale` (value + age emphasised) · `Unavailable` (gap card, no number) · `Offline` (cache + global strip).

## 9. Data & API requirements

- **IMD keyed API** (`api.imd.gov.in`, 28 endpoints). **Operating constraints (verified):** key is **bound to a static public IP**; every call needs **API key + a user-bound JWT that expires hourly**; 2 DEV + 2 PROD keys max; usage stats shared with IMD on request. → key cannot ship in the app; a **static-IP backend** must hold it and refresh the JWT. **This is the critical path.**
- **Fallback while the host is absent:** IMD public **GeoServer WFS** so all displayed values remain genuinely IMD.
- **Warning floor:** public **CAP/RSS** warning feed.
- **Climatology:** IMD Pune 124-year gridded rainfall (Pai et al. 2014) for "normal vs now".
- **Non-IMD adapters (labelled — policy v2, ADR-0002):** CPCB national AQI (`data.gov.in`, GODL; **provisional** flag; **XKDR** mirror only as a labelled fallback) · **Copernicus CAMS** UV (hourly forecast; labelled; India publishes no UV API). SAFAR is not integrated (no API/licence; degraded). `app.cpcbccr.com` is never used or labelled CPCB. Unavailable → gap card. Attribution strings are tracked per source.
- **Known documentation gaps to design around:** the API reference's index lists MausamGram (#27) and Highway Nowcast (#21) but their field sections are dead anchors — treat hourly/NHAI data as upside, with documented fallbacks (Q27).

## 10. Architecture (summary)

`IMD keyed gateway (static-IP host, key + hourly JWT, cache, attribution ledger)` → `Fusion service (normalise 28 endpoints, staleness; labelled adapters — CPCB · CAMS)` → `Advisory engine (rules → actions + facts, replayable)` + `Window engine (activities → deterministic windows, replayable)` → `Personal bundle (~15 KB signed JSON)` → `Offline home screen (map + bottom sheet, i18n, a11y, provenance toggle, planner)`; alongside: `Routine-alert scheduler + notification ledger → Web Push (VAPID) → in-app inbox`.

## 11. Non-functional requirements

- **Offline/2G:** cache-first; first contentful render from cache; age visible.
- **Accessibility:** WCAG-minded contrast, keyboard nav, screen-reader labels; verify in demo.
- **i18n:** template-first strings; human-reviewed warnings; English + Hindi in the mock.
- **Privacy:** personalisation on-device; no behavioural tracking; saved places only, deletable. *(v1.1: routine delivery config — schedule + place — is backend-registered for delivery only, deleted on opt-out; ADR-0003.)*
- **Determinism:** advisory output reproducible; fixed inputs → fixed cards; windows and alerts inherit the same rule.
- **Security:** secrets in env/secret store; never in the app; attribution honoured.

## 12. Success metrics (measure, never invent)

Card comprehension (can a user state the action?) · time-to-decision · cache-load time at 2G · **advisory reproducibility (target 100% replay)** · translation coverage · per-endpoint staleness SLA (measured) · warning→action latency · **routine-alert delivery latency** · **alert→action time** *(v1.1)*. Anything unmeasurable is written "to be measured in pilot".

## 13. Release scope

**By 5 Oct 2026 (idea submission):** the official **6-slide SIH template deck** (title included) **+ an offline, clickable mock** whose numbers are **real captured IMD payloads** (never invented). The mock also carries a **static planner screen** from real captures (ticket 16; no push), and the deck's third visual block becomes the **honesty two-up** (mixed state + planner).
**Finale (Nov–Dec):** the working pipeline against keyed IMD APIs, three deep personas, provenance + replay, offline PWA, i18n/a11y — plus the **activity planner and routine alerts** (window engine · scheduler · ledger · Web Push) and the labelled adapter clients.

## 14. Decision log (Q1–Q9, D1–D3, Q20–Q28) & open questions

| # | Decision | Value | Status |
|---|---|---|---|
| Q1 | One-line spine | "The Mausam home screen that tells you what to do — and proves where every number came from." | Accepted |
| Q2 | Home IA | Decision stack — **refined to map + decision-stack bottom sheet** (D1) | Accepted |
| Q3 | Persona model | Onboarding selection (multi) + chip row; deterministic reordering | Accepted |
| Q4 | Provenance interaction | Both: tap-a-number sheet **and** global toggle | Accepted |
| Q5 | Card anatomy | Fixed: action + facts + source/age chip | Accepted |
| Q6 | Gap handling | Inline gap card in place of the value | Accepted |
| Q7 | Freshness UI | Per-value age badge + global offline/last-updated strip | Accepted |
| Q8 | Visual identity | **Amended 02 Oct:** Apple-leaning product surface — calm neutral chrome, one lead element, restrained accent, system font stack, light + dark, motion only to explain state. No official-brand claim; cite UX4G | Accepted |
| Q9 | Mock platform | Web PWA; keep the app shell, personalise Home. **Superseded 02 Oct:** no decorative phone bezel — a responsive full-viewport mobile app, so it runs natively when opened on a phone | Accepted (amended) |
| D1 | Map vs stack on home | Map + bottom-sheet decision stack (matches the real app) | Accepted |
| D2 | Which three personas ship deep | Agriculture / Commuter / Health | Accepted |
| D3 | Languages in the mock | English + Hindi | Accepted |
| Q20 | **Accounts & identity** *(amended 03 Oct 2026)* | **Firebase** for auth + account data (passwordless email link + OAuth, Firestore + Security Rules); **guest-first** — the home never requires sign-in; an account only syncs saved places and feedback | Accepted (see `../docs/adr/0001-firebase-auth.md`) |
| Q21 | **Feature family** *(v1.1)* | Activity Planner (pull) + Routine Alerts (push), one deterministic window engine | Accepted |
| Q22 | **Activity model** *(v1.1, amended 03 Oct 2026)* | Activities are presets inside personas (Fitness → volleyball/run/walk; Commuter → office routine); **custom activities ship in the mock**: any name + the weighted metrics that matter, pinned at the config version, on-device only | Accepted |
| Q23 | **5-Oct planner scope** *(v1.1)* | Static planner screen in the mock from real captures (ticket 16) + deck shot; **tripwire:** if tickets 02–07 aren't green by 4 Oct evening → planner drops to deck-only | Accepted |
| Q24 | **Non-IMD adapter policy v2** *(v1.1)* | IMD first; labelled official Indian adapters (CPCB AQI via `data.gov.in`; XKDR labelled mirror); **CAMS UV** (no Indian UV API); safety triggers IMD-only; no unlabelled models; `app.cpcbccr.com` banned; SAFAR excluded | Accepted (see `../docs/adr/0002-labelled-adapters.md`) |
| Q25 | **Routines & privacy** *(v1.1)* | Explicit manual entry; stored on-device; never behaviourally inferred; Q20 account scope unchanged (delivery config only, ADR-0003) | Accepted |
| Q26 | **Alert semantics** *(v1.1)* | Evening plan (21:00) + departure (T−30 default) + IMD orange/red override; quiet hours 21:30–06:30; cap 3/day; permission at first routine creation; inbox always; append-only ledger + replay | Accepted (see `../docs/adr/0003-routine-alert-transport.md`) |
| Q27 | **Window granularity** *(v1.1)* | Resolution-adaptive; demo at 3-h blocks with the grain stated; 1-h only if MausamGram #27 is accessible | Accepted |
| Q28 | **Score model** *(v1.1)* | Hard gates + versioned weighted comfort score, daylight-constrained (sun/moon); formula shown in provenance | Accepted |

## 15. Risks & mitigations

1. **IMD key/host delay** (account exists, static-IP host not yet provisioned) → stand up the host immediately; run the mock on IMD WFS meanwhile. *(critical path)*
2. **"Just a UI" perception** → the replayable advisory engine is the backend story.
3. **Most-crowded PS** → IMD-native lineage + full provenance + auditability is the moat.
4. **Brand overclaim** → never claim official IMD brand; cite UX4G.
5. **Language quality** → template-first, human-reviewed warnings.
6. **Undocumented IMD endpoints** *(v1.1)* — MausamGram (#27) and Highway Nowcast (#21) are index entries with dead field anchors → treat hourly/highway data as upside; design documented fallbacks (WFS, district/station nowcast) and state the grain (Q27).
7. **`api.data.gov.in` reachability unverified from the production host** *(v1.1)* → validate on day one (ticket 20); XKDR labelled mirror as fallback (ADR-0002).
8. **Notification fatigue + iOS PWA push caveats** *(v1.1)* → quiet hours + daily cap; demo on Android Chrome; iOS requires install (ADR-0003).
9. **Adapter licence/quality drift** *(v1.1)* — SAFAR degraded and unlicensable; CPCB values provisional → labelled adapters only, provisional flags, attribution ledger; gap card on outage (ADR-0002).

## 16. References

- IMD API Reference — https://api.imd.gov.in/public/api_reference.html
- IMD API Portal User Guide (key + JWT + static-IP) — https://api.imd.gov.in/public/IMD_API_Portal_User_Guide.pdf
- SIH 2026 (idea submission deadline 5 Oct; official 6-slide template) — https://www.sih.gov.in/
- Mausam app (Play) — https://play.google.com/store/apps/details?id=com.imd.masuam
- PIB — Mausam/Meghdoot/Damini, languages — https://pib.gov.in/PressReleasePage.aspx?PRID=2202382
- MeitY UX4G design system — https://www.ux4g.gov.in/
- Climatology — Pai et al. 2014 (IMD Pune gridded rainfall)
- Competitor repos reviewed — optimusprime123x/SIH2026-Mausam, Sovereign-Immortal/mausam, xarjunpatil/SIH26076-…, aditi-agarwal-sketch/sih26076-mausam
- CPCB real-time AQI dataset — https://www.data.gov.in/resource/real-time-air-quality-index-various-locations
- XKDR India Air Quality Database — https://airquality.xkdr.org/
- Copernicus CAMS (UV forecasts) — https://ads.atmosphere.copernicus.eu
- SAFAR (sibling MoES product; not integrated) — https://safar.tropmet.res.in/

---


## 17. Amendment v1.2 — AI Chatbot Assistant *(04 Oct 2026, proposed)*

**Scope:** A grounded, retrieval-only conversational layer that helps users navigate the home screen, explain cards, set up routines, and answer "what does this mean?" questions. **Never generates weather facts.** Falls back to template strings offline.

### 17.1 New Decisions (Q29–Q31)

| # | Decision | Value | Status |
|---|---|---|---|
| Q29 | **AI Chatbot Assistant** | A grounded, retrieval-only conversational layer that helps users navigate the home screen, explain cards, set up routines, and answer "what does this mean?" questions. Never generates weather facts. Falls back to template strings offline. | Proposed |
| Q30 | **Chatbot Data Boundary** | The bot only reads from the personal bundle (already-fetched IMD payloads, derived cards, saved routines). No live API calls. No external knowledge. | Proposed |
| Q31 | **Chatbot Persona** | Calm, concise, task-oriented. No chit-chat, no personality simulation. Responses are short, action-linked, and cite the card they reference. | Proposed |

### 17.2 New Functional Requirements

**Conversational Assistant**

- **FR-21** A text/voice chatbot is accessible from the home screen (floating action button) and from any card's provenance sheet. It answers navigation questions ("how do I switch persona?"), card explanations ("what does 'visibility 400 m' mean?"), routine setup help ("add a run at 7am"), and provenance follow-ups ("which station was that?").
- **FR-22** The bot **never generates weather values, forecasts, or advisories**. Every factual response is a direct quote or structured read from the personal bundle (cards, window scores, routine alerts, gap cards). If the bundle has no answer, the bot says "I don't have that data" and points to the gap card.
- **FR-23** The bot runs **offline-first**. It uses a small on-device model (or deterministic template matcher in the mock) that consumes the personal bundle JSON and emits templated responses. No network call for chat. Online mode may use a retrieval-grounded LM for phrasing only; numbers are never generated by the LM.
- **FR-24** Routine creation via chat: user says "remind me for my run at 7am" → bot confirms the activity, time, days, and place → creates the routine entry in local storage → schedules the departure alert (T−30 default). The bot shows the created routine card immediately.
- **FR-25** Provenance integration: from any card, "Ask about this" opens the bot pre-seeded with that card's context. The bot can read the provenance sheet fields aloud or in text.
- **FR-26** Accessibility: voice input/output supported where browser APIs allow; all bot responses meet WCAG AA contrast; keyboard-accessible chat pane; screen-reader labels on all messages.
- **FR-27** Privacy: chat history stored locally only (IndexedDB), cleared on app data clear. No chat logs sent to any server. If online phrasing LM is used, only the user's question text is sent (no bundle data, no location, no identity).

### 17.3 Architecture Impact

```
Personal Bundle (~15 KB JSON) → Chatbot Context Engine (on-device)
                                     ↓
                         Template Matcher / Small LM (phrasing only)
                                     ↓
                         Response: template + bundle quote + action link
```

- No new backend endpoint required for the mock. Finale may add a `/chat` endpoint that proxies to a retrieval-grounded LM with strict schema: input = user text + bundle context; output = templated response with `card_ref` pointers. The LM never sees raw IMD payloads.
- The chatbot is a **view** on the existing engine, not a new data path.

### 17.4 Updated Risk Register Additions

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| R12 | Chatbot hallucinates a weather value | Medium | Critical (judge demo fails trust) | Hard rule: LM output validated against bundle schema; any numeric claim without `card_ref` → blocked and replaced with template "I don't have that data" | Engine |
| R13 | Chatbot scope creep (users treat it as forecast source) | High | High | UI: bot never shows a number without a source chip; every response links to the originating card; empty state says "This app shows IMD data only" | Client |
| R14 | Offline chatbot quality too low for demo | Medium | Medium | Mock uses deterministic template matcher (no LM) with 50+ pre-written patterns covering onboarding, card help, routine setup, provenance questions. Tested headless. | Client |
| R15 | Voice input not supported on judge device | Medium | Low | Text input always available as primary; voice is progressive enhancement. Demo script uses text. | Client |

### 17.5 Demo Script Addition

| Time | Beat |
|---|---|
| 0:00–0:20 | Problem (unchanged) |
| 0:20–0:40 | Why tiles + chatbot fail (unchanged, but now contrast: *other* chatbots hallucinate; ours is grounded) |
| 0:40–1:00 | Decision layer + provenance (unchanged) |
| 1:00–2:30 | Live: Commuter persona, 2G throttle, fog card, provenance toggle (unchanged) |
| 2:30–3:00 | **NEW: Chatbot** — tap fog card → "Ask about this" → bot explains "visibility 400 m means dense fog, drive slowly" with source chip; user says "remind me tomorrow" → bot creates routine, shows card |
| 3:00–3:30 | Advisory engine + climatology (unchanged) |
| 3:30–4:00 | Impact metrics (unchanged) |
| 4:00–4:30 | Deployment + chatbot privacy (local-only, no chat logs leave device) |
| 4:30–5:00 | Q&A buffer |

### 17.6 What Does NOT Change

- Card generation, provenance, replay, gap cards, window engine, routine alerts, labelled adapters, offline PWA, i18n, a11y, guest-first auth — all v1.1 scope intact.
- The chatbot is a **help layer**, not a decision layer. The home screen remains the primary interface.

### 17.7 Sign-off Required

Before merging this amendment into the submission deck:

- [ ] Product lead: scope is real, not aspirational
- [ ] Engine lead: template matcher + 50 patterns feasible in mock timeline
- [ ] Client lead: chat pane fits bottom-sheet IA without breaking snap points
- [ ] Privacy lead: local-only storage + no-bundle-to-LM rule accepted

If any box is unchecked, the amendment stays proposed and the submission uses v1.1 scope.


## Appendix A — Deep UI specification

### A.1 Competitive UI landscape (what already exists — do not rebuild it as our "novelty")

| Rival | UI approach | Provenance / gaps |
|---|---|---|
| optimusprime123x/SIH2026-Mausam | Compose, Material 3 Expressive + Liquid Glass; floating pill toolbar; card→detail sheet | **Per-card source line**; `CardValue = Ready \| Pending \| Unavailable` ("Pending never carries a number") |
| Sovereign-Immortal/mausam | Rust/Dioxus; **5-tab bottom nav**; bento metric cards, ring charts | None visible; invented "Atmospheric System" tokens (`#003366`/`#2DBCFE`) |
| xarjunpatil/SIH26076 | Dark glassmorphism web dashboard, Chart.js | None |
| Shreyansh303/team_mausam_sih_2026 | Flutter; server-driven ranked home | "Estimated" chip; freshness chip |

**Implication:** persona reordering, offline cache, and a source line are **table stakes**. Our UI must visibly exceed them: **station + issue time + age per value**, and a **replay** proof.

### A.2 Home shell & bottom-sheet interaction

The real Mausam home is map-centric with an auto-opening bottom sheet. We keep that shell.

- **Snap points:** peek (~32% — hero action only), half (~62% — hero + next 2 cards), full (~92% — whole ranked stack).
- **Gesture:** drag handle; velocity-based snap; respects `prefers-reduced-motion` (snap without spring).
- **Pinned in the sheet header:** persona **chip row** (switch persona → stack re-ranks) and the global **provenance toggle**.
- **Map layer:** Leaflet with IMD WFS district-warning overlay; colour follows IMD's 4-colour warning convention.
- **Empty/degraded:** if offline, the map shows the last cached tiles flagged "offline"; the sheet still renders from cache.

### A.3 Action cards — concrete contents per deep persona

Every card obeys the §8.3 anatomy (action → facts → source/age chip).

**Commuter**
| Card | Headline | Triggering facts | Source |
|---|---|---|---|
| Hero | Leave 20 minutes early | Fog warning (code 15) · visibility 400 m | District warning (6) |
| 2 | Carry a raincoat today | Heavy rain > 15 mm/hr likely | District nowcast Cat12 (4) |
| 3 | Check your highway stretch | Highway nowcast advisory | NHAI highway nowcast (21) |
| 4 | Lightning likely 15:00–17:00 | CG lightning probability > 60% | Station nowcast Cat19 (7) |
| Gap | — | Traffic data not published by IMD | labelled adapter / gap |

**Agriculture**
| Card | Headline | Triggering facts | Source |
|---|---|---|---|
| Hero | Delay sowing by 3 days | Agromet advisory, week of … | Agromet advisory (28) |
| 2 | Protect seedlings tonight | Ground frost | Warning code 14 (6) |
| 3 | Rainfall 42% below normal | Week actual vs normal | District/state rainfall (5, 8) |
| 4 | Heavy rain in your river basin (~48 h) | Basin QPF | River-basin QPF (10) |
| Gap | — | Soil moisture not published by IMD for your block | gap card |

**Health**
| Card | Headline | Triggering facts | Source |
|---|---|---|---|
| Hero | Avoid outdoor exertion 12:00–16:00 | Heat wave (code 9) · station max 44.6 °C | Warning (6) + AWS (9) |
| 2 | Keep hydrated tonight | Warm night (code 11) | Warning (6) |
| 3 | Check AQI before heading out | CPCB national AQI (**provisional**) | CPCB adapter — labelled (data.gov.in) |
| 4 | UV — check the labelled forecast | Copernicus CAMS UV (model run shown) | CAMS adapter — labelled (ADR-0002) |
| Gap | — | **Pollen** not published by IMD (no Indian source) | gap card (the honesty showcase) |

**Fitness / activity windows** *(added v1.1)*
| Card | Headline | Triggering facts | Source |
|---|---|---|---|
| Hero | Play 17:00–19:00 — best window today | Comfort 82/100 · heat index 31 °C · wind 9 km/h | IMD nowcast + AWS |
| 2 | Skip 12:00–15:00 (heat) | Heat-index band amber/red | IMD heat index (AWS "Feel Like") |
| 3 | Prefer the evening window for air quality | CPCB national AQI (provisional) | CPCB adapter — labelled |
| 4 | UV shown from a labelled source | Copernicus CAMS UV · model run shown | CAMS adapter (ADR-0002) |

### A.4 Provenance sheet (the hook's payoff)

Tapping any value expands a sheet:

```
Source       IMD District Warning
Endpoint     /api/v1/districtwarning?id=573
Station      Nashik  (Obj_id 573)
Issued       05:30 IST · 02 Oct 2026
Age          2 h 14 m
Type         Official warning — code 15 (Fog)
Raw value    Day_1 = "15"  · Day1_Color = 3 (yellow)
[ Replay advisory ]
```

And for a **window score** *(added v1.1)*:

```
Score        82 / 100   (config windows-v1)
Formula      gates pass · 0.35·heat + 0.20·humidity + 0.20·wind + 0.15·AQI + 0.10·UV
Facts        heat index 31 °C · humidity 54% · wind 9 km/h        (IMD AWS/nowcast)
             AQI 96 — CPCB (labelled, provisional, 14 m old) · UV 2 — CAMS (labelled, run 05:00 UTC)
Excluded     pollen — no source (gap)
[ Replay window ]
```

- **"Replay advisory"** re-derives the card from its logged inputs — the audit proof.
- Optional **raw-payload** view for judges (show the JSON that produced the value).

### A.5 Gap-card spec

In place of the value, not beside it: a muted card, no number, reading *"IMD does not publish pollen."* plus a one-line reason and, if applicable, the labelled adapter's value with its own source chip. No spinner, no "—", no fake zero.

### A.6 The three deck screenshots (6-slide deck)

1. **Home (Commuter)** — map + sheet peek, fog hero card.
2. **Provenance expanded** — the A.4 sheet, station + issue + age visible.
3. **Honesty two-up** *(reworked v1.1)* — mixed state (IMD-native · labelled adapter · pollen gap) alongside the **planner best-window** screen (ticket 16); replaces the pollen-only gap shot.

### A.7 Design tokens (labelled as *ours*, not IMD's)

Authority-blue primary, warning amber, severe red, safe green; 8-pt spacing grid; system font stack with Noto Indic fallbacks. Documented as our system, referencing MeitY **UX4G** — **no claim of official IMD brand compliance**, because none exists.

### A.8 Activity planner & routine alerts *(added v1.1)*

**Window card** — same fixed anatomy as §8.3; the headline is a window, the facts are the score and its drivers:

```
┌───────────────────────────────────────────────┐
│  Play 17:00–19:00 — best window today         │  ← imperative window
│  Comfort 82/100 · heat index 31 °C · wind 9   │  ← triggering facts
│  IMD nowcast + AWS · CPCB · CAMS · 3-h blocks │  ← sources + grain
└───────────────────────────────────────────────┘
```

- **Granularity:** 3-hour blocks in the demo (IMD's documented finest numeric forecast cadence); 1-hour only if MausamGram #27 proves accessible. The grain is always stated on screen.
- **Score:** hard gates (rain, thunderstorm/lightning, heat extremes) → weighted comfort (heat index, humidity, wind, AQI, UV); weights versioned; formula shown in provenance (A.4).
- **Custom activities:** any name + which weighted metrics matter (builder under the activity picker); weights are the canonical per-metric values renormalised over the selection; preset names are reserved; rain/storms remain hard gates, never toggles.
- **Alerts (defaults, editable):** evening "tomorrow plan" 21:00 · departure T−30 min · IMD orange/red override (immediate, bypasses quiet hours) · quiet hours 21:30–06:30 · cap 3/day · permission at first routine creation · inbox always.
- **States:** Ready · Stale (age emphasised) · No good window today · Rest day · Adapter unavailable (metric excluded + disclosed) · Offline (last-known + age).
- **Audit:** every alert appended to the notification ledger; `replay` reproduces the window and the alert payload byte-identically.

---

## Appendix B — Traced decisions

| # | Decision | Value | Status |
|---|---|---|---|
| Q10 | Home shell | Map + bottom-sheet decision stack (matches the real app) | Accepted |
| Q11 | Provenance depth | Both: per-value station/issue/age **and** replay proof | Accepted |
| Q12 | Deck visuals | 3 screenshots (Home/Provenance/Gap) + 1 diagram | Accepted |
| Q13 | Mock languages | English + Hindi | Accepted |
| Q14 | Map in mock | Leaflet + IMD WFS warning overlay (static image fallback) | Accepted |
| Q15 | Default sheet snap | **Half** on open; auto-raise on a severe (orange/red) warning; never force full | Accepted |
| Q16 | Agromet rendering | Template-first, human-reviewed → imperative actions; raw advisory shown in provenance | Accepted |
| Q17 | Raw-payload view | Collapsible raw API JSON in the provenance sheet | Accepted |
| Q18 | Hero selection rule | Severity → persona weight → recency (deterministic, stated on the Tech slide) | Accepted |
| Q19 | Clickable-mock depth | Persona switch + provenance (tap + global toggle) + gap card + sheet snaps are live; rest static | Accepted |

## Appendix C — Implementation tickets

Broken down with the `to-tickets` skill into tracer-bullet vertical slices; published to the local-markdown tracker at `../.scratch/mausam-homepage/issues/`. All are `Status: ready-for-agent`. Work the frontier — as of v1.1: tickets 02, 05, 11, 14, and 16 are open and unblocked; 17–20 are finale-scope.

**Mock (by 5 Oct)**

| # | Ticket | Blocked by |
|---|---|---|
| 01 | Walking skeleton — real IMD payload → one frozen hero card, offline | None |
| 02 | Advisory engine v0 + replay endpoint | 01 |
| 03 | Persona model + deterministic re-rank | 02 |
| 04 | Provenance interaction (tap sheet + global toggle + raw JSON + replay) | 02 |
| 05 | Gap card (honesty state) | 01 |
| 06 | Bottom-sheet home shell (map + snaps + WFS overlay) | 01, 03 |
| 07 | Six-slide deck + mock capture | 04, 05, 06 |
| 14 | Onboarding + auth/accounts (Firebase) | 01 |
| 16 | Planner screen — static best-window slice (real captures, no push) *(v1.1)* | None (independent of 02–07) |

**Finale**

| # | Ticket | Blocked by |
|---|---|---|
| 08 | Deep persona — Commuter | 03, 06 |
| 09 | Deep persona — Agriculture | 03, 06 |
| 10 | Deep persona — Health | 03, 05, 06 |
| 11 | Offline / 2G + freshness | 01 |
| 12 | i18n (EN + Hindi) + accessibility pass | 03, 06 |
| 13 | Live IMD keyed API integration | 02 (and the static-IP host) |
| 15 | Settings · saved places · feedback | 14 |
| 17 | Activity model + window engine v1 *(v1.1)* | 02, 03 |
| 18 | Routine alerts — scheduler, ledger, Web Push *(v1.1)* | 13, 17 |
| 19 | Activities & routines UI *(v1.1)* | 15, 17 |
| 20 | Labelled adapters — CPCB AQI (+ XKDR mirror) & CAMS UV *(v1.1)* | 13 |
