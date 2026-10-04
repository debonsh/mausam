# DESIGN.md — design philosophy and UI flow

Companion to `PRD-SIH26076-Mausam.md` (requirements), `APP.md` (architecture), and `docs/UI-DIRECTION.md` (the decision record). This document is the **design contract**: the principles we design by, the token system that encodes them, and the flows the interface must support.

Status note (03 Oct 2026): §4 and §5 are **implemented** for the full stack
(tickets 02–06: ranked cards, gaps, sheet shell), in the Stitch visual direction
(ticket 21: slate light + OLED dark tokens, Plus Jakarta Sans, four-step
onboarding, Settings/Map tabs). §6.1/6.3/6.4/6.5 are built; §6.2/6.6/6.7/6.9 are
partial; §6.8 is partial (EN/HI chrome live, warning copy awaits human review).

---

## 1. The anchor: we cannot drift from PS 26076

- **Official title:** *Development of a personalized homepage for the 'Mausam' mobile application* (IMD / MoES · Software · **Smart Automation**).
- **The statement's scope is eight personas**: Health-conscious · Outdoor fitness enthusiasts · Beachgoers & surfers · Travelers · Parents & families · Agriculture & gardeners · Commuters · Event planners.
- **Three non-negotiables:** this is **Mausam's home screen** (not a new app); it visibly serves **eight** personas; it surfaces **IMD's own** intelligence.

Every screen must answer: *which persona is this for, and where did this number come from?*

---

## 2. The one idea

> **The home screen tells you what to do, and proves where every number came from.**

Everything else is subordinate to that sentence. The design has one job: make the *action* obvious, and make the *provenance* one gesture away. If a visual choice does not serve one of those two, it is decoration and it goes.

The memorable moment (the thing a judge remembers) is the **provenance reveal**: one control unmasks source, station, issue time, and age across the whole screen at once.

---

## 3. Design philosophy

The register is **product, not brand**. This is an instrument someone opens at 6 a.m. with one hand; familiarity beats surprise, and the design earns trust through consistency and speed.

Four principles, in priority order:

### 3.1 Calm
Weather is already loud; the interface must not add noise. Neutral chrome, generous whitespace, one accent doing the work. Colour is a **signal**, never a mood board. A quiet screen is what makes the one amber dot mean something.

### 3.2 One lead element
Each screen has exactly one thing that leads, and everything else supports it. On the home screen that is the **hero action**. If two elements compete, the user cannot tell what to do, and we have failed the job.

### 3.3 Honest
The interface never invents a number, never hides an age, and never dresses an estimate as an observation. A missing value becomes a **gap card**, not a placeholder. This is a design principle, not just a data rule: honesty must be *visible*.

### 3.4 Legible
Readable outdoors, on 2G, at arm's length, one-handed, in bright sun and at night. Contrast, size, and target area are floors, not polish. A beautiful screen that fails AA is not shipped.

### 3.5 How the principles resolve conflicts
- Calm vs. Honest → **Honest wins.** A warning must interrupt; a calm screen that buries a red warning is wrong.
- One lead vs. Calm → **One lead wins.** A screen with no focal point is not calm, it is fog.
- Legible vs. everything → **Legible wins.** Contrast and target size are non-negotiable.

---

## 4. The token system

Tokens are the design contract expressed in code (`app/styles/tokens.css`). Nothing is chosen by feel at the call site.

### 4.1 Colour as roles, not shades

| Role | Light | Dark | Used for |
|---|---|---|---|
| `--canvas` | `#f8fafc` | `#000000` | Page canvas |
| `--surface` | `#ffffff` | `#1c1c1e` | Cards, controls |
| `--sheet` | `#ffffff` | `#121214` | Bottom sheets, tab bar |
| `--label` | `#0f172a` | `#f2f2f7` | Primary text, headline |
| `--label-2` | `#475569` | `#a1a1a6` | Secondary (eyebrow, units) |
| `--label-3` | `#64748b` | `#8e8e93` | Tertiary (labels, timestamps) |
| `--label-4` | `#94a3b8` | `#636366` | Quaternary (captions) |
| `--line` | `#e2e8f0` | `#2c2c2e` | Hairlines |
| `--accent` | `#0b3d66` | `#4aa3ff` | Primary action, links, active tab |
| `--ok` | `#059669` | `#34c759` | No warning / live |
| `--sev-high` | `#dc2626` | `#ff453a` | Warning-level severity |

Rules:
- **Whisper commitment.** One accent, used rarely. If the accent is everywhere, no action is primary.
- **Severity is never colour alone.** Every severity carries a dot **and** a word ("Reduced visibility"). Colour-blind users read the word; screen readers read both.
- **Medium severity is authority blue**, not amber — the calm-authority direction the mocks set; red is reserved for warnings above the action level.
- **Three text levels, no more.** `label` / `label-2` / `label-3`. Numbers are tokenised so they can be audited.
- **Light and dark both ship.** Dark follows `prefers-color-scheme`; `?theme=light|dark` pins it for demos and screenshots, and `data-theme` is set before first paint so dark never flashes light.

### 4.2 Type

Plus Jakarta Sans (400 · 500 · 600 · 700) carries the UI, JetBrains Mono covers
endpoints and raw JSON, and Noto Sans Devanagari covers Hindi — with an Apple /
`system-ui` fallback stack so an offline load still renders in the platform font.
Fonts are fetched with `display=swap` and never block first paint.

| Step | Size / weight | Tracking | Use |
|---|---|---|---|
| Large title | 34 / 700 | −0.4 | Location name |
| Action | 22 / 600 | −0.3 | The imperative headline |
| Metric value | 19 / 700 | −0.4, tabular | The numbers |
| Unit | 14 / 500 | 0 | Attached to a value |
| Body | 17 / 400 | 0 | Default |
| Secondary | 15 / 400 | 0 | Loading, helper |
| Label | 13 / 600 | 0 | Eyebrow, source |
| Caption | 12 / 400 | 0 | Metric caption, timestamp |
| Tab | 10 / 400 | .1 | Bottom navigation |
| Footnote | 11 / 400 | 0 | PS attribution |

Rules: hierarchy by **size + weight together**; numbers use **tabular figures** so digits do not jump; sentences are **sentence case**; body measure stays readable; text wraps rather than truncates (`text-wrap: balance` on the action).

### 4.3 Space, radius, depth

- **Spacing scale:** 4 · 8 · 12 · 16 · 20 · 24 · 32. Every margin and padding is one of these. No arbitrary values.
- **Radii:** sheet `28`, card `16`, tile/control `12`, pill `999`. Large radii read as calm; small ones read as utilitarian.
- **Depth:** three planes. Background (canvas, never interactive), Content (cards, text), Attention (sheets, overlays, animated in from the nearest edge). A card is not placed inside another card; where a boundary is needed we use a **hairline separator**, not a nested box.
- **Elevation:** one soft shadow token. Elevation means "this is a distinct object", so there are only two levels: canvas and card.

### 4.4 Motion

Motion exists to **explain state**, never to decorate. Short and functional.

- **Durations:** `--t-fast` 160 ms (press, colour), `--t-base` 320 ms (card entrance).
- **Curve:** `cubic-bezier(.2, .8, .2, 1)` — decelerate out. No bounce, no elastic.
- **Only `transform`, `opacity`, and `grid-template-rows`** are animated; anything else causes layout.

The motion inventory (all implemented in `app/styles/components.css`):

| Element | Behaviour | Duration / delay |
|---|---|---|
| Header (title, freshness, button) | Staggered rise-in (`translateY 8px → 0`) | 300 ms; 0 / 40 / 60 ms |
| Live dot | Gentle pulse (scale + opacity) | 2.4 s, infinite |
| Hero card | 3-beat entrance: `scale .95, opacity 0` → `.015, .92` → `1, 1` | 320 ms |
| Metric columns | Staggered rise-in | 280 ms; 60 / 110 / 160 / 210 ms |
| Provenance endpoint | Slides open by animating `grid-template-rows: 0fr → 1fr` (no layout jump) | 260 ms |
| Provenance chevron | Rotates 90° to point down | 160 ms |
| Offline pill | Rise-in when it appears | 200 ms |
| Icon button, tab, source row | Press response (`scale .92` / `.94`, opacity) | 160 ms |

Rules: the whole entrance settles in **under ~500 ms** (product motion is short); a flat fade is dead, so entrances carry scale or translate; exits run faster than entrances; nothing animates longer than it takes to explain the change. **Reduced motion is honoured**: `prefers-reduced-motion` collapses every duration to ~0 and the same content is always reachable without motion.

### 4.5 Interaction and states

Every interactive element is designed in all of the states it can enter, not just rest:

| State | How it looks |
|---|---|
| Idle | Token defaults |
| Hover | Pointer only; never required to reach a function |
| Active/press | `scale(.94)` on icon buttons, `opacity .6` on the source row |
| Focused | `:focus-visible` 3px accent ring, 2px offset |
| Loading | Named ("Loading IMD data…"), never a bare spinner |
| Empty | Teaches what belongs there and what fills it |
| Error | Names what broke and the recovery path |
| Offline | Freshness line changes + an explicit "Offline" pill |

Rules: **44×44 minimum targets**; focus rings are architecture (never `outline: none` without a visible replacement); **undo beats confirm**; labels are always visible (placeholders are not labels); native controls over custom ones.

### 4.6 Copy and voice

Words are interface.
- **Sentence case** everywhere.
- **One verb per action.** "Allow extra time on the road", not "OK".
- **No exclamation points**, no marketing preamble, no filler headings.
- **No em dashes** in interface copy; use a comma, colon, or a new sentence.
- **Errors are recovery paths**: name the break, then the way forward.
- **Loading names the work**: "Loading IMD data…", not "Loading…".
- **Numbers carry their unit** and their age.

### 4.7 Accessibility is the floor

- Contrast ≥ AA for all text (measured, not assumed).
- Never colour alone; severity = dot + word.
- Full keyboard path; visible focus; 200% zoom and 320px reflow survive.
- `prefers-reduced-motion` and `prefers-reduced-transparency` respected.
- Semantic HTML first (`<button>`, `<a href>`, `<nav>`), ARIA only when native cannot express it.
- Safe-area insets via `env(safe-area-inset-*)`; iOS zoom avoided by keeping inputs ≥16px.

### 4.8 Responsive and platform

- Mobile-first, `max-width: 480px` centred; the same file runs full-viewport on a phone.
- **Thumb zone:** primary actions and navigation live in the bottom 25%; destructive actions sit higher.
- Structure changes with width; features are never amputated ("not available on mobile" is a bug).
- Logical properties (`start`/`end`) so `dir="rtl"` works when we add Urdu/other scripts.

### 4.9 Anti-patterns we refuse

Decorative device frames · coloured left-border cards · cards inside cards · glassmorphism as a style · gradient text · purple/blue-violet SaaS palettes · colour-only state · em dashes · exclamation points · animation that delays the task · hover-gated functionality · placeholder-as-label · "Loading…" · invented numbers.

---

## 5. The card grammar

Every advisory card has the same anatomy, in this order. Consistency is what makes the eighth card as readable as the first.

```
┌────────────────────────────────────────────┐
│  ● Reduced visibility                      │  eyebrow: severity dot + category
│                                            │
│  Allow extra time on the road              │  action: imperative, one sentence
│                                            │
│  ── hairline ───────────────────────────   │
│   2 km      25.8 °C      90 %              │  metrics: value (tabular) + unit + label
│   Visibility  Temp       Humidity          │
│                                            │
│  IMD SYNOP · New Delhi-Safdarjung       ›  │  source: tappable, reveals the raw endpoint
│  Issued 02 Oct, 23:38 IST                  │  sub: issue time (and age)
└────────────────────────────────────────────┘
```

Anatomy rules:
1. **Eyebrow** names the trigger, not the metric. It carries the severity dot and the word.
2. **Action** is imperative and complete without the numbers ("Allow extra time on the road").
3. **Metrics** are the *triggering facts*, ordered by relevance to the action; a metric with zero signal is omitted rather than padded.
4. **Source row** is the honesty anchor: source + station, then issue time and age, then the raw endpoint when provenance mode is on. It is a real control, not a label.
5. Nothing else. No secondary actions, no share row, no decorative glyph.

**Severity → action** is deterministic (the rule chain, ticket 02): dense fog (≤1 km) → "Avoid driving if you can"; reduced visibility (≤4 km) → "Allow extra time on the road"; rain → "Carry rain gear"; otherwise "No action needed today".

---

## 6. UI flows

Legend: `→` screen/state transition · **(built)** / **(planned)**.

### 6.1 First run and onboarding *(built, ticket 14 + 21 — live GPS, city search and live-warning Hindi are finale)*

```
Launch (splash)      brand + "IMD data ready"
  → Get started      the one-screen pitch      (Skip / Continue as guest → Home)
  → Language  1 / 4  English / हिंदी            (default: device language)
  → Sign in   2 / 4  email link · Google        (guest-first; shows the Firebase gap honestly)
  → Location  3 / 4  GPS · search · popular     (one tap, never a form)
  → Persona   4 / 4  the PS's eight personas    (pick 1+, first is primary)
  → Home             guest session, everything works
```
Rules: never more than four steps; every step skippable; a sensible default exists for each; "Skip" lands on the Persona-default commuter home, not a blank screen. The persona list uses the **statement's own words** so it is recognisable to a judge, and the persona editor is reachable again from Settings.

**The sign-in step never blocks.** It explains what sync unlocks, then steps
aside; the home is fully usable signed-out (PRD §11, `APP.md` §4, ADR-0001), and
the same screen is offered from Settings for later. Until the Firebase project
exists, both entry points state that plainly instead of faking a session.

### 6.2 The daily home — the primary flow *(built; severe re-rank unobserved — no severe fixture yet)*

```
Home
  → Read the hero: severity + action        (one lead element)
  → Read the triggering facts               (metrics row)
  → Act, or tap the source row              (provenance, §6.3)
  → Scroll for the ranked stack             (built, ticket 06)
```

The hero is chosen by **severity → persona weight → recency**. When nothing is severe, the hero is the persona's most useful card and the screen stays quiet. The bottom sheet snaps half-open showing the hero plus two cards; it **auto-raises** only on an orange/red warning, and never forces full-screen.

### 6.3 The provenance flow — the defining interaction *(built, ticket 04)*

Two entry points into one revealing state:

```
Tap a value ─┐
             ├─→ Provenance on
Tap the (i) ─┘     • every value gains a dotted underline
                   • every source row reveals its raw endpoint
                   • the (i) shows pressed state (aria-pressed)

Global toggle on  → all values chip at once ("the sweep")
Global toggle off → the screen returns to calm
```
Rules: the toggle reveals **source · station · issue time · age**, and the raw endpoint/layer underneath. It is reversible and non-destructive. This is the moment we design the whole product around; it must feel like lifting a lid, not opening a debug panel.

### 6.4 The gap-card flow — honesty made visible *(built, ticket 05)*

```
A metric IMD does not publish (pollen, UV)
  → the slot is NOT a blank, NOT a dash, NOT a zero
  → it becomes a gap card, in place:
        ● Not published by IMD
          Pollen is not an IMD product, so we do not show a number.
          [ Labelled source, if one exists ] → shows the value + its own source chip
```
Rules: the gap occupies the **same position** the value would (so the layout is stable); it states who *does* publish it if anyone; it never shows a number we cannot attribute. A missing value must never look like a zero.

### 6.5 Persona switch *(built, ticket 03)*

```
Chip row (pinned at the top of the sheet, active chip first)
  tap "Farmer"  →  the stack re-ranks deterministically
                   the hero may change
                   the chips animate; nothing else moves position
```
Rules: one tap, no menu; the content changes, the **chrome does not** (a persona switch is not a page load). Re-ranking is deterministic and replayable, so the same tap always produces the same order.

### 6.6 Severe-warning re-rank *(partial — rule live, unobserved; ticket 06)*

```
A red/orange warning is issued
  → the sheet auto-raises (only for severe)
  → the warning card animates to the top, above personal preference
  → a banner states the warning in words
  → urgency beats preference: no personalisation may bury a warning
```
Rule: severity always outranks personal relevance. The animation explains *that something changed*; it never delays reading the warning.

### 6.7 Offline and 2G *(partially built)*

```
Load with no network
  → render the last cached payload (service worker)
  → freshness line: "Offline, showing cached data"
  → explicit "Offline" pill; the live dot turns amber
  → every value keeps its age
```
Rules: a cold start with no network still renders; age is always visible; we never show a stale number as if it were live, and we never show a spinner where cached truth exists.

### 6.8 Language *(planned, ticket 12)*

English + Hindi. Language is a setting, not a separate app; copy, actions, and gap reasons translate, but **numbers and station names do not**. Warning text is human-reviewed, never raw machine translation.

### 6.9 Map and places *(built: schematic map on Home + the Map tab; the WFS overlay waits on ticket 13)*

```
Home (map behind)  ← map + bottom-sheet stack, faithful to the real app
  → pan to a district       → that district's warning highlights (IMD WFS)
  → Map tab                 → full-map view
  → Places tab              → saved places (traveller persona)
```
Rules: the map is **labelled with its own source** when it carries warning data; the sheet never fully covers the map on first paint; the map is never the only way to reach a value (accessibility).

---

## 7. State coverage matrix

Every surface must ship these, not just the happy path:

| Surface | Loading | Empty | Error | Offline | Overflow |
|---|---|---|---|---|---|
| Home | named load | gap card | recovery copy + retry | cached + pill | scroll, wrap |
| Onboarding | n/a | each step has a default | inline retry on location | cached choices | step scroll |
| Auth | "Sending code…" | signed-out teaches value | "code expired, resend" | session cached | sheet scroll |
| Settings | named load | signed-out explanation | "couldn't sync, retry" | cached places | list scroll |
| Provenance | instant | n/a | "endpoint unavailable" | cached endpoint | mono wrap |
| Map | skeleton | no overlay for this area | tiles unavailable | last tiles | zoom |
| Personas | — | "pick one to see more" | — | — | chip row scrolls |

---

## 8. Build rules (how we make it)

1. **Tokens first.** No literal colour, size, or radius at the call site; if a value is missing, add a token.
2. **Real files, real data.** No markdown mockups. Test with the real IMD capture, long station names, and missing values.
3. **Measure, do not eyeball.** Contrast is measured; states are screenshotted (`docs/evidence/`).
4. **One card at a time.** The grammar in §5 is fixed; new cards fill the same anatomy.
5. **Verify before claiming.** A state that is implemented but not visible is described as such.
6. **Least code that works.** Prefer native and existing patterns; no visual dependency that does not pay for itself.

---

## 9. Open design questions

1. **Map:** behind the sheet, or a tab? (Decides ticket 06.)
2. **Severity colour:** current amber/red, or quieter still? (Calm vs. honest.)
3. **Density:** how much of the ranked stack before scrolling?
4. **Persona switch placement:** chip row under the title, or a segmented control?
5. **Brand:** no official IMD brand guide exists; do we adopt a direction (A/B/C in `UI-DIRECTION.md`) or keep the neutral system?

---

## 10. Built for mobile (the PS says "mobile application")

The statement asks for a homepage **for the Mausam mobile application**. So the deliverable is not a website that happens to be narrow: it is the app's home screen, and it must behave like a mobile app on a real device.

### 10.1 The delivery form
The mock ships as an **installable PWA** for the demo (tickets 01–07), from which the same screen is specified for the real app. Three ways it reaches users, in order of realism:

1. **Inside the real Mausam app.** The backend returns the finished, ranked, provenance-carrying bundle (`GET /home`), so the home screen is server-driven and IMD can add or reorder a card **without an app release**. The screen itself is implemented natively (Compose/Flutter) against this document as the spec.
2. **WebView / TWA wrapper** around the same code, if a native rebuild is out of scope, so it still installs and runs standalone.
3. **Standalone installable PWA** (what we demo): added to the home screen, launched with no browser chrome.

### 10.2 What makes it feel like an app, not a page
Implemented in `index.html` / `manifest.webmanifest` / `styles/tokens.css` + `styles/components.css`:

- **Standalone display** (`display: standalone`), portrait-locked, `id` + `start_url` scoped so it launches into the home screen.
- **Install metadata**: `mobile-web-app-capable`, `apple-mobile-web-app-capable`, `apple-mobile-web-app-title`, `status-bar-style`, an `apple-touch-icon`, and an SVG icon set with a **maskable** variant so Android can shape it.
- **Status bar matches the app**: `theme-color` is white, so the OS bar blends into the surface.
- **Safe areas**: `viewport-fit=cover` plus `env(safe-area-inset-*)` on the header and tab bar, so nothing collides with a notch or a home indicator.
- **Touch, not hover**: 44×44 minimum targets; `-webkit-tap-highlight-color: transparent` with our own press states; no functionality behind hover.
- **No page-like gestures**: `overscroll-behavior-y: none` (no rubber-band pull-to-refresh on the mock), tab bar anchored to the bottom thumb zone.
- **Offline by default**: the service worker precaches the shell and the fixture, so a cold launch with no network still renders the home screen with its age visible.

### 10.3 Performance for 2G and low-end phones
- **No framework, no webfonts**: system font stack only; the whole app is three small text files plus one JSON fixture.
- **One request for first paint**; the fixture is precached on install.
- **No layout shift**: fixed aspect ratios for the metric row, and the card animates with `transform`/`opacity` only.
- **Battery/CPU**: no continuous animation except a single 2.4 s dot pulse, disabled under reduced motion.

### 10.4 Mobile acceptance checks
Before a ticket is done on the UI:
1. Install prompt available; launches **standalone** with no browser chrome.
2. Renders correctly at **320 px** (iPhone SE) and 375 px, portrait, with no horizontal scroll.
3. Header and tab bar respect safe-area insets on a notched device.
4. Cold launch with the network **off** renders the card and shows the age.
5. Every target ≥ 44×44; no zoom when a field is focused; 200% text zoom reflows.
6. `prefers-reduced-motion` removes motion without removing content.
