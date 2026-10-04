# FILEMAP.md — where everything lives

Companion to `APP.md` (architecture) and `ROADMAP.md` (sequencing).
Status: **03 Oct 2026** (amended: planner/alerts files, ADRs 0002–0003).
This file is the **single source of truth for layout**.

Rule from `APP.md` §12: **every file has a named responsibility.** A new file that
is not listed here (or not added here in the same change) is an orphan and should
not be committed.

---

## 1. Principles

1. **One concern per file.** A module does one thing and its name says so.
2. **Screens vs components.** A *screen* owns a route/state and composes
   components; a *component* renders one unit and holds no routing.
3. **Framework-free core.** `core/` and `engine/` must run in Node (no DOM) so they
   are unit-testable without a browser.
4. **No bundler.** ES modules loaded by the browser; the same modules imported by
   Node for tests. No build step in the repo.
5. **Assets are data, never generated at import time.** Fixtures are committed
   captures, not code.
6. **Secrets are files we never commit.** Only `.env.example` is tracked.

---

## 2. Target repository layout

```
Mausam/
├── README.md                     # overview + run instructions
├── APP.md                        # architecture / ecosystem / flows
├── DESIGN.md                     # design contract (tokens, grammar, flows)
├── ROADMAP.md                    # sequencing + done-when
├── FILEMAP.md                    # this file
├── PRD-SIH26076-Mausam.md        # signed-off requirements
├── AGENTS.md                     # directory-scoped agent notes
│
├── app/                          # the PWA client (no build step)
│   ├── index.html                # shell: mounts #app, pins the theme, loads scripts
│   ├── manifest.webmanifest      # install metadata
│   ├── sw.js                     # service worker (cache-first + background refresh; push handlers, ticket 18)
│   ├── app.js                    # bootstrap: state, routes, the api views talk to, offline
│   ├── core.js                   # esc/store/theme/$ + format helpers (Node-testable)
│   ├── icons.js                  # inline SVG registry (no icon font, no CDN)
│   ├── i18n.js                   # EN/HI chrome strings (ticket 12)
│   ├── personal.js               # on-device places/routines/feedback (tickets 15/19)
│   │
│   ├── views/                    # one screen owner per file, no routing
│   │   ├── onboarding.js         # splash · get started · language · login · location · persona (ticket 14)
│   │   ├── home.js               # map hero + decision stack + persona chips + gaps (tickets 03–06)
│   │   ├── provenance.js         # provenance sheet + replay + citation (ticket 04)
│   │   ├── settings.js           # settings · places · map tab · inbox (tickets 15/19)
│   │   ├── planner.js            # windows + routines + week strip (tickets 16/19)
│   │   └── chat.js               # Mausam AI sheet + home FAB + provenance ask (ticket 21, PRD v1.2)
│   │
│   ├── engine/                   # deterministic rules → view model (Node-testable)
│   │   ├── deriveCard.js         # rule chain: facts → severity → action + detail line
│   │   ├── windows.js            # gates + versioned comfort score → window view model (ticket 17)
│   │   └── chat.js               # grounded matcher: bundle quotes only, never generates (ticket 21)
│   │
│   ├── fixtures/                 # committed real IMD captures
│   │   ├── imd-synop-delhi-2026-10-02.json
│   │   └── imd-synop-delhi-2026-10-02.capture.json
│   │
│   ├── styles/
│   │   ├── tokens.css            # DESIGN §4 tokens only (light + OLED dark)
│   │   └── components.css        # screen/component styles, tokens-only values
│   │
│   ├── identity/                 # Firebase client wrapper (planned, ADR-0001, ticket 14)
│   └── data/                     # provider chain + bundle fetch (planned, ticket 13)
│
├── backend/                      # FastAPI service (proposed, ticket 13+)
│   ├── main.py                   # app factory, routes: /bundle, /replay
│   ├── config.py                 # env loading (never secrets in code)
│   ├── gateway/
│   │   ├── imd_keyed.py          # keyed API client + hourly JWT refresh
│   │   ├── imd_wfs.py            # public GeoServer WFS fallback
│   │   └── cap.py                # CAP/RSS warning floor
│   ├── fusion/
│   │   ├── normalize.py          # 28 endpoints → common taxonomy
│   │   └── staleness.py          # per-value age/issue time
│   ├── engine/
│   │   ├── rules.py              # deterministic rule chain
│   │   ├── windows.py            # window engine: gates + score, replayable (ticket 17)
│   │   ├── rank.py               # severity → persona weight → recency
│   │   └── replay.py             # byte-identical reproduction + log
│   ├── adapters/                 # labelled non-IMD sources (ADR-0002)
│   │   ├── cpcb.py               # AQI: data.gov.in (+ XKDR labelled mirror), or gap
│   │   └── cams.py               # UV: Copernicus CAMS (labelled), or gap
│   ├── alerts/                   # routine alerts (ADR-0003)
│   │   ├── scheduler.py          # digest · departure · IMD orange/red override
│   │   ├── ledger.py             # append-only notification ledger + replay
│   │   └── push.py               # Web Push (VAPID) sender + subscriptions
│   ├── identity/
│   │   ├── auth.py               # verify Firebase ID token on user-scoped routes
│   │   └── firebase.py           # firebase-admin client (service account, backend only)
│   └── store/
│       ├── cache.py              # in-process TTL cache
│       └── replay_log.py         # append-only log
│
├── firebase/                     # identity/DB config as code (ADR-0001)
│   ├── firebase.json             # project + emulator config
│   ├── firestore.rules           # per-user Security Rules for every path
│   └── firestore.indexes.json    # composite indexes (places, feedback)
│
├── tests/                        # Node + pytest; mirrors module layout
│   ├── engine.test.js            # replay byte-identity, rule boundaries
│   ├── windows.test.js           # window gates/weights + determinism (ticket 17)
│   ├── chat.test.js              # grounded replies: quotes ctx, never invents (ticket 21)
│   ├── onboarding.test.js        # ≤3 steps, skippable, defaults
│   └── test_backend.py           # gateway/fusion/engine
│
├── docs/
│   ├── UI-DIRECTION.md           # UI decision record
│   ├── evidence/                 # rendered screenshots per ticket
│   ├── ui-references/            # credited rival screenshots
│   └── deck/                     # idea-submission deck (ticket 07)
│       ├── build.py              # fills the official template + converts to PDF (stdlib + soffice)
│       ├── diagram.png           # architecture/flow diagram source
│       ├── honesty-twoup.png     # honesty two-up composite source
│       ├── SIH26076-idea-6slides.pptx  # filled template (editable source)
│       └── SIH26076-idea-6slides.pdf   # the submission file
│
└── .env.example                  # env var names only (tracked)
```

Repo-level (outside `Mausam/`):

```
docs/adr/                         # cross-cutting decisions
  0001-firebase-auth.md
  0002-labelled-adapters.md
  0003-routine-alert-transport.md
.scratch/mausam-homepage/         # tickets (local-markdown tracker)
  spec.md
  issues/NN-*.md
```

---

## 3. Current → target mapping

The client split landed with ticket 21 (the Stitch UI direction). Earlier rows are
kept for traceability; the note below records what actually moved.

| Was | Now | Notes |
|---|---|---|
| `app/app.js` (all logic) | `app/app.js` (bootstrap + api) + `app/views/*` + `app/core.js` + `app/icons.js` | one screen owner per view file; engine exports unchanged |
| `app/styles.css` (single file) | `app/styles/tokens.css` + `app/styles/components.css` | values replaced by the Stitch palette (light + OLED dark) |
| inline provenance wiring in `app.js` | `app/views/provenance.js` | behaviour unchanged (replay + raw JSON + citation) |
| planner + inbox markup in `app.js` | `app/views/planner.js` + the inbox route in `app/views/settings.js` | same engine, restyled |
| `app/fixtures/*` | unchanged (`app/fixtures/*`) | planned `app/data/` move deferred to ticket 13 |
| `app/selftest.js` (CommonJS) | unchanged | `tests/` already cover the engine; selftest stays as the smoke script |

**Migration rule:** move one concern per commit; keep the app green (`node --test`
+ manual offline reload) after each move.

> 03 Oct 2026 (ticket 21): client split done — `views/onboarding|home|provenance|settings|planner.js`,
> `core.js`, `icons.js`; `app.js` is bootstrap + api only (soft 200-line cap met). Engine split
> was done earlier (`engine/deriveCard.js`, `engine/windows.js`).

---

## 4. Naming and size conventions

- **Files:** `kebab-case` for assets/docs, `camelCase` for JS modules whose default
  export is a function (`deriveCard.js`), `PascalCase` never in filenames.
- **Modules:** one default export; named exports for pure helpers.
- **CSS:** token names from `DESIGN.md` §4 only; component classes are
  `block__element--modifier` (already the house style).
- **Tests:** mirror the module path (`app/engine/deriveCard.js` → `tests/engine.test.js`).
- **Soft size cap:** ~200 lines per JS module; beyond that, split by concern.
- **No barrel files by default;** import the module you need.

---

## 5. Documentation ownership

Every fact has exactly one home. Violations are fixed in the same change.

| Fact | Lives in | Must not be restated in |
|---|---|---|
| Requirements (FR-*) | `PRD-SIH26076-Mausam.md` | README (link instead) |
| Architecture / tech choices | `APP.md` | DESIGN (link instead) |
| Design tokens, card grammar, flows | `DESIGN.md` | APP (link instead) |
| Sequencing / done-when | `ROADMAP.md` | APP (link instead) |
| File layout / responsibilities | `FILEMAP.md` | any other doc |
| Auth rationale | `docs/adr/0001-firebase-auth.md` | APP (summarise + link) |
| Non-IMD data policy | `docs/adr/0002-labelled-adapters.md` | APP (§5 summarises + links) |
| Routine-alert transport | `docs/adr/0003-routine-alert-transport.md` | APP (§3.5 summarises + links) |
| Ticket state | `.scratch/**` issues | README status table (summarise) |

---

## 6. Definition of "clean and organised" (the lint we hold ourselves to)

- [ ] No file exists that is not in §2 (or added here first).
- [ ] No doc restates a fact owned by another doc (§5).
- [ ] No secret value in the repo; `.env.example` lists names only.
- [ ] `core/` and `engine/` import nothing DOM-specific.
- [ ] Every ticket in `.scratch/**` has a `Status:` line and a matching row in
      `ROADMAP.md` §2.
- [ ] `node --test` passes and the app reloads offline after every change.
