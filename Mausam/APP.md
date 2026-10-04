# APP.md — ecosystem, architecture, and build contract

Companion to `PRD-SIH26076-Mausam.md` (requirements), `DESIGN.md` (design contract),
`ROADMAP.md` (sequencing), and `FILEMAP.md` (where every file lives).
Status: **v2 — 03 Oct 2026.** Supersedes the draft tech table in v1. Items marked
_proposed_ still need team sign-off; items marked **decided** are locked.

This document is the single source of truth for **how the product is built and how
data flows end to end**. If a claim here disagrees with `PRD`/`DESIGN`, the more
specific doc wins for its subject and this file is the one to fix — see §12.

---

## 1. What we are building

The **home screen of IMD's Mausam app**, rebuilt as a persona-adaptive **decision
layer**: it turns IMD data into *actions* and proves where every number came from.
It is a **prototype and a model** — a complete, coherent product surface that a
judge can use end to end (onboard → sign in → act → verify → adjust), not a
collection of disconnected cards.

"Finished prototype" is defined precisely in §11. The end-to-end journey is §8.

---

## 2. The ecosystem

Four planes. The app never touches a secret; the backend never touches the UI;
identity is a managed service, not hand-rolled crypto.

```
┌──────────────────────────── Clients (PWA) ─────────────────────────────┐
│  onboarding · auth · home (map + sheet) · provenance · places · settings │
└───────┬───────────────────────┬───────────────────────┬─────────────────┘
        │ Firebase JS (CDN)     │ GET /bundle (signed)  │ PUT saves
        │ web config + ID token │ + ID token            │ + feedback
┌───────▼───────────────┐ ┌─────▼───────────────────────▼─────────────────┐
│ Identity & data plane │ │ Application plane (FastAPI, single container) │
│ Firebase              │ │  gateway/   IMD keyed API (static-IP host,    │
│  auth (link + OAuth)  │ │             key + hourly JWT); WFS · CAP floor│
│  Firestore + Rules    │ │  fusion/    normalise 28 endpoints + staleness│
│  profiles·places·     │ │  engine/    rules → actions + facts · replay  │
│  feedback             │ │  adapters/  CPCB (AQI) … each value labelled  │
│                       │ │  store/     TTL cache · append-only replay log│
└───────────────────────┘ └─────┬─────────────────────────────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
  IMD keyed API (28 endpoints)                   Non-IMD (labelled)
  IMD GeoServer WFS · CAP/RSS floor              CPCB AQI · others
  IMD Pune 124-yr gridded climatology            → never unlabelled
```

**Rules that hold the ecosystem together**

1. **Secrets never ship.** The IMD key and the Firebase **service-account key** live
   only on the backend, in env/secret storage. The app carries only the **Firebase
   web config** (its `apiKey` is public by design, and access is enforced by Firestore
   Security Rules).
2. **The client never computes an advisory.** The backend returns the finished,
   ranked, provenance-carrying bundle so IMD could re-rank cards without an app
   release (PRD §10).
3. **Identity degrades offline.** Auth state is cached; the home renders from the
   personal bundle with no network. Sign-in is required only to **sync** saved
   places and feedback across devices — never to read the weather (PRD §11).
4. **Every value carries its `source`.** No source → gap card (§7).

---

## 3. Architecture

### 3.1 Client — offline-first PWA **(decided)**

Vanilla HTML/CSS/JS PWA, no bundler (PRD Q9, amended 02 Oct). Modules are ES
modules loaded natively; the service worker cache is network-first with a cache
fallback so a deploy is never served stale and a cold offline start still renders.

Why not a native build for the model: one codebase, offline by construction, and
it runs full-viewport on a real phone. *Ponytail: no framework until the diff
demands one.* A framework is revisited only if a ticket proves the vanilla surface
cannot carry the interaction (tracked in `ROADMAP.md` §5).

### 3.2 Backend — FastAPI **(proposed)**

Python 3.13, FastAPI + Pydantic v2 + httpx. One container. It holds the IMD key,
refreshes the hourly JWT, normalises endpoints, runs the advisory engine, and
exposes `replay`. It also verifies the Firebase ID token on any user-scoped route.

### 3.3 Identity & data plane — Firebase **(decided — ADR-0001)**

Firebase Authentication provides sign-in (passwordless email link + OAuth), Cloud
Firestore stores account data, and Firestore **Security Rules** enforce per-user
ownership. It works from a vanilla-JS CDN client **and** a Python backend. Full
rationale and rejected alternatives: `../docs/adr/0001-firebase-auth.md`.

| Concern | Decision |
|---|---|
| Sign-in methods | Email **passwordless link** (primary, no password) · Google **OAuth** (secondary) |
| Guest mode | **Default.** Onboarding works with no account; home is fully usable signed-out |
| What needs an account | Syncing **saved places** and **feedback** across devices (PRD §11) |
| Session | Firebase **ID token** (JWT, refreshed hourly) + refresh token; persisted client-side; offline-safe |
| Authorisation | **Firestore Security Rules** on every collection — the store enforces ownership, not the client |
| Backend verification | FastAPI verifies the Firebase ID token with `firebase-admin` (`verify_id_token`) before any user-scoped read/write |
| Billing | Free (Spark) tier for the prototype; documented upgrade path for a pilot |

### 3.4 Storage & caching

| Layer | Choice | Purpose |
|---|---|---|
| Server cache | **In-process TTL cache** keyed by issue time | Avoid re-fetching IMD endpoints |
| Durable store | **Cloud Firestore** | profiles · saved places · feedback |
| Client cache | **Service worker** + last signed bundle | Offline home + freshness badges |
| Replay log | **Append-only** (backend) | Byte-identical advisory reproduction |

A relational store or Redis is only introduced if a real pilot needs them —
*ponytail: skip until proven.*

### 3.5 Maps & live updates

- **Maps:** Leaflet + OSM tiles + IMD WFS district-warning overlay, labelled with
  its own source (no token cost).
- **Live updates:** WebSocket for the demo re-rank animation; **Web Push (VAPID)**
  with a backend scheduler + notification ledger as the production transport for
  routine alerts (ADR-0003); FCM remains the future native-shell option.

---

## 4. Account, onboarding & settings model

The first run is three steps, every step skippable (DESIGN §6.1). Step 3 is where
identity enters — and it can be deferred.

```
Launch
  → Language        English / हिंदी            (default: device language)
  → Where are you?  GPS · search · popular     (one tap, never a form)
  → Who are you?    the PS's eight personas    (pick 1+, first is primary)
  → Home            (guest session, everything works)

Later, from Settings, only when you want sync:
  → Sign in         passwordless email link, or Google OAuth
  → Profile         display name, home place, personas (editable)
  → Saved places    synced to your account (RLS-scoped)
  → Feedback        "was this action useful?" — account-scoped, deletable
```

**Data model (Firestore; Security Rules on every path):**

| Collection path | Rule | Contents |
|---|---|---|
| `users/{uid}` | read/write only by that `uid` | display name, primary persona, language, home place |
| `users/{uid}/places/{placeId}` | read/write only by that `uid` | label, lat/lon, optional district |
| `feedback/{feedbackId}` (carries `uid`) | owner writes; owner (and admin) reads | advisory id, verdict, optional note |

**Privacy guardrails (PRD §11):** personalisation stays on-device; there is **no
behavioural tracking**; only explicit saves and feedback are stored; a user can
delete their account and rows. Guest data never leaves the device.

**Offline behaviour of identity:** the signed-in state and saved places are cached;
a signed-in user with no network still opens the home and sees their places, and
any queued save syncs when connectivity returns. We never block the home on auth.

---

## 5. Data & provider chain

**Chain (first hit wins), every value recording its `source`:**

1. **IMD keyed API** (`api.imd.gov.in`, 28 endpoints) — authoritative. Gated: key
   bound to a **static public IP**, **API key + user JWT expiring hourly**, 2 DEV +
   2 PROD keys, usage stats shared with IMD.
2. **IMD GeoServer WFS** (public) — used until the host/key is live, so values stay
   genuinely IMD.
3. **CAP/RSS warning feed** — the always-available warning floor.
4. **Labelled adapters** — CPCB AQI (`data.gov.in`; XKDR labelled mirror),
   Copernicus CAMS UV; policy + bans in ADR-0002.
5. **Gap card** — when nothing applies. Never a fabricated number.

**Climatology:** IMD Pune 124-year gridded rainfall (Pai et al. 2014) for
"normal vs now".

---

## 6. The advisory engine

- Deterministic rule chain over typed IMD facts → **action card** (imperative
  action + triggering facts + source/age chip).
- **Hero selection:** severity → persona weight → recency (deterministic, PRD Q18).
- **Replay:** same logged inputs → byte-identical card; a `replay` endpoint proves it.
- **Persona re-rank:** deterministic ordering per selected persona.
- A narration model may *rephrase* — it can never *invent* numbers (§7, PRD §3).

---

## 7. Provenance & honesty model

- Every number carries: **source · endpoint · station · issue time · age**.
- **Tap** any value → provenance sheet (collapsible raw JSON + **Replay**). A
  **global toggle** chips every value at once ("the sweep") — the demo beat.
- Missing value → **inline gap card** ("IMD does not publish pollen"), in the value's
  own position, never a dash, zero, or placeholder (PRD FR-8, DESIGN §6.4).

---

## 8. The end-to-end flow (the "model")

This is the journey the finished prototype must make frictionless. Legend:
`→` transition · **(built)** / **(planned)**.

```
┌ First run ──────────────────────────────────────────────────────────────┐
│ Language → Location → Persona                     (planned, ticket 14)   │
│   └─ every step skippable; defaults exist; "Skip" lands on commuter home │
└───────────────────────────────┬─────────────────────────────────────────┘
                                ▼
┌ Home (guest or signed-in) ─────────────────────────────────────────────┐
│ Read hero (severity + action) → triggering facts → source row          │
│   ├─ tap source row → provenance sheet (station·issue·age·raw·replay)   │
│   ├─ toggle (i)  → global provenance sweep                             │
│   ├─ persona chip → deterministic re-rank                              │
│   ├─ severe warning → sheet auto-raises, urgency beats preference      │
│   └─ scroll → ranked decision stack                                    │
└───────────────────────────────┬─────────────────────────────────────────┘
                                ▼
┌ Account (optional, from Settings) ─────────────────────────────────────┐
│ Sign in (link/OAuth) → sync saved places → feedback      (planned, 14)  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                ▼
┌ Offline / 2G ──────────────────────────────────────────────────────────┐
│ cached bundle renders · "Offline, showing cached data" · ages visible   │
└─────────────────────────────────────────────────────────────────────────┘
```

Deep flows (provenance, gap, persona switch, severe re-rank, offline, language,
map/places) are specified in `DESIGN.md` §6; their build state is in `ROADMAP.md` §2.

---

## 9. Tech stack

| Layer | Choice | Status | Why / what we skip |
|---|---|---|---|
| Home screen | **PWA** — vanilla HTML/CSS/JS + service worker; ES modules | decided | One codebase, offline by construction, runs on a real phone |
| Backend | **FastAPI** (Python 3.13) + Pydantic v2 + httpx | proposed | Validated by prior art; easy rule engine; one language for the data layer |
| Identity / DB | **Firebase** — Auth (passwordless + OAuth) + Firestore + Security Rules | decided (ADR-0001) | Managed auth, real store, per-user security; CDN client + `firebase-admin` |
| Storage | In-process TTL cache + Cloud Firestore | proposed | Zero infra for the demo |
| Live updates | WebSocket (demo) → Web Push VAPID (routine alerts; ADR-0003) | proposed | Re-rank animation is a strong demo beat; alerts fire with the app closed |
| Maps | **Leaflet** + OSM tiles + IMD WFS overlay | proposed | No token cost |
| Packaging | single OCI image + static PWA | proposed | Matches the "one container" story |

---

## 10. Repository map & build plan

- **Where every file goes:** `FILEMAP.md`.
- **What ships when:** `ROADMAP.md`.
- **Tickets:** `../.scratch/mausam-homepage/issues/` (local-markdown tracker).

**Ticket index**

- **Mock (by 5 Oct):** 01 skeleton · 02 engine+replay · 03 persona · 04 provenance ·
  05 gap · 06 sheet shell · 07 deck · 16 planner (static slice).
- **Finale:** 08 Commuter · 09 Agriculture · 10 Health · 11 offline/2G ·
  12 i18n+a11y · 13 live IMD keyed API · 17 window engine · 18 routine alerts
  (scheduler · ledger · Web Push) · 19 activities UI · 20 labelled adapters.
- **Accounts & productisation:** 14 onboarding + auth/accounts (Firebase) ·
  15 settings · saved places · feedback.

**Landed:** 01 done — `app/` vanilla PWA rendering real IMD SYNOP values, fixture +
provenance in `app/fixtures/`, evidence in `docs/evidence/`.

Use the superpowers `executing-plans` / `subagent-driven-development` process; keep
the **ponytail** reflex for all code.

---

## 11. Definition of "finished prototype"

The model is **done** when a reviewer can, without help, do all of the following:

1. **Onboard** in ≤3 skippable steps and land on a working home.
2. **Read an action** and state what to do, from the hero alone.
3. **Prove a number** — tap it, see source · station · issue time · age · raw JSON,
   and **replay** the advisory to a byte-identical card.
4. **See honesty** — a real gap card where IMD publishes nothing.
5. **Switch persona** and watch the stack re-rank deterministically.
6. **Go offline** and still open the home, with ages visible and an Offline pill.
7. **Sign in** (optional) and sync a saved place across a reload.
8. **Use it one-handed, keyboard-only, and in Hindi**, with no AA failures.

Anything not meeting all eight is described as **partial** in `ROADMAP.md`, never
claimed as complete (DESIGN §8.5, PRD §12).

---

## 12. Engineering conventions (kept deliberately boring)

1. **Single source of truth per fact.** Architecture → here; design → `DESIGN.md`;
   sequencing → `ROADMAP.md`; layout → `FILEMAP.md`; requirements → `PRD`. Cross-doc
   contradictions are bugs, fixed in the same change.
2. **No orphan files.** Every file has a named responsibility in `FILEMAP.md`.
3. **No secrets in the repo.** Env templates only (`.env.example`); real values in
   the host's secret store.
4. **Deterministic by construction.** Every advisory is reconstructible from a
   logged input; tests assert byte identity.
5. **Honest states.** Unbuilt surfaces are labelled in docs and in the UI; we never
   ship a placeholder as a value.
6. **Least code that works.** Native and existing patterns first; no dependency that
   does not pay for itself.

---

## 13. Prior art & what we borrow (verify licences; attribute)

| Repo | License | What we borrow |
|---|---|---|
| `Shreyansh303/team_mausam_sih_2026` | MIT | Provider chain with per-value `source`; 33-card catalog; scoring formula; admin demo console + scenario overlays + demo clock; "Why am I seeing this?" sheet; EN/HI per-key fallback; offline tests replaying captured payloads via `respx` |
| `optimusprime123x/SIH2026-Mausam` | verify | `CardValue = Ready \| Pending \| Unavailable` ("Pending never carries a number"); per-card source line |
| `Sovereign-Immortal/mausam` | MIT | Dioxus/Compose offline cache patterns |
| `xarjunpatil/SIH26076-…` | verify | FastAPI + web demo structure |

**Our differentiation (not borrowed):** IMD-native lineage (rivals default to
Open-Meteo), provenance depth (station + issue time + age + raw JSON), gap cards
instead of "Estimated", and the **replayable advisory** proof.

---

## 14. Open questions (need team input)

1. **Backend host** — who provisions the static-IP host, and when? *(critical path,
   ticket 13)*
2. **Firebase project region** — pick the Firestore location closest to the static-IP
   host to keep latency low (ADR-0001 follow-up).
3. **OAuth providers** — Google only, or Google + Apple (needed if we later publish
   to the App Store)?
4. **App shell** — confirm PWA-only for the model vs a later Flutter/native shell.
5. **Deep-persona depth** — confirm ticket-07 scope (persona switch + provenance +
   gap + sheet snaps).
6. **VAPID keys + demo device** — generate the keypair and confirm the Android-Chrome
   demo device for routine-alert push (ADR-0003, ticket 18).
