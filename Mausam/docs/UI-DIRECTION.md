# UI direction — working notes (not final)

We are **not** freezing UI yet. This file anchors the UI to the problem statement, records the frame decision, applies a design-direction framework, and lists what we need from the team.

## 0. The anchor: PS 26076 (do not drift)

- **Official title:** *Development of a personalized homepage for the 'Mausam' mobile application* — India Meteorological Department / MoES · Software · **Smart Automation**.
- **The statement's only content is eight personas** (its verbatim scope): *Health-conscious · Outdoor fitness enthusiasts · Beachgoers & surfers · Travelers · Parents & families · Agriculture & gardeners · Commuters · Event planners.*
- **Everything the UI does must trace to that.** Three non-negotiables from the statement: it is the **home screen of Mausam** (not a new app); it visibly serves **eight** personas; it shows **IMD's own** intelligence.
- **Our wedge** (PRD §3, and the judge's takeaway): *every number shows its IMD source and age; every advisory can be re-derived by hand.*
- **Depth split:** Agriculture, Commuter, Health built deep; the other five ship as competent labelled cards.

## 1. Frame decision (02 Oct)

The decorative phone bezel + fake status bar were **removed** at the team's request. The mock is now a **responsive, full-viewport mobile app** (`max-width: 480px`, safe-area insets) so it behaves correctly when opened on an actual phone. Supersedes PRD Q9's "phone frame".

## 2. Design direction (framework: purpose / audience / tone / detail / constraints)

- **Purpose:** convert IMD data into *what to do now*, and prove each number's origin.
- **Audience:** the eight personas on a phone, often outdoors, one-handed, sometimes on 2G — and, in the room, an **IMD judge** who knows real IMD products and can smell a foreign model.
- **Tone (to choose):** utilitarian-bulletin, calm-scan, or technical-instrument — see §3.
- **Memorable detail:** the **provenance reveal** — one toggle unmasks source · station · issue time · age on every value at once. This is the demo beat.
- **Constraints:** 8 personas is a lot for one screen → persona switch must be one tap; English + Hindi; a11y (contrast, ≥44px targets, reduced-motion); must read as IMD, so no invented numbers and no stock-blue branding we can't justify.

## 3. Three candidate directions (pick one, or mix)

| | **A — IMD Bulletin** | **B — Decision Deck** | **C — Field Instrument** |
|---|---|---|---|
| Tone | editorial, authoritative, calm | product, scannable, task-first | technical, dense, credible |
| Hero | a real IMD bulletin headline + map | one big imperative action card | the map, with station read-outs |
| Type | serif headings + clean sans body | bold sans, big action headline | mono numerals, small labels |
| Palette | IMD deep blue + warning colours | neutral surfaces, colour = severity only | slate/mono, colour = warning only |
| Persona switch | chip row (statement's own words) | chip row | segmented control |
| Strength vs judge | reads "official" | reads "useful daily" | reads "auditable" |
| Risk | can look like a website | can look generic | can look cold/hard to read |

**DECIDED 02 Oct (team):** an **Apple-leaning product surface** — B's decision-first spine, executed with Apple's restraint. Concretely: system font stack, iOS large-title header, one lead element (the action card), neutral chrome with a single restrained accent, severity as a dot + word (never colour alone), hairline separators over nested cards, translucent tab bar, light + dark, and motion only where it explains state. Implemented and rendered (light/dark/provenance) in `Mausam/app/`; evidence in `Mausam/docs/evidence/`.

Anti-patterns refused: decorative device frame, coloured left-border cards, glass panels as a style, gradient text, em dashes in copy, colour-only state.

## 4. What we need from you

Send **inspiration/references** — anything: apps, screenshots, Dribbble/Behance links, a colour you like, a phrase ("should feel like a railway timetable"). Specifically:

1. **Tone** — A, B, C, or a mix; and any app you think Mausam should feel like.
2. **Hero** — the *action* ("Leave 20 min early") or the *map* first?
3. **Persona switch** — chips, tabs, or a segmented control?
4. **Colour** — any palette references? (We have no official IMD brand guide; ours is ours to define.)
5. **Density** — how much to show before scrolling?

## 5. Reference screenshots

`docs/ui-references/` holds three screens from the leading public prototype (`Shreyansh303/team_mausam_sih_2026`, MIT) — a card-feed dashboard with global freshness and "Estimated" chips. Differences we keep: map + bottom sheet, per-value provenance, gap cards, IMD-native.
