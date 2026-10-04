# 21: Stitch UI direction — full screen suite

**What to build:** Implement the approved Stitch design suite
(`Mausam/stitch_mausam_home_final/`, 11 screens × light/dark) as the product UI:
splash + get started, the four-step skippable onboarding (language · sign-in ·
location · persona), the map + bottom-sheet home in the new visual language,
the provenance sheet, Settings (with saved places, preferences, feedback,
about), the Map and Places tabs, the inbox, and an OLED dark theme. Keep every
existing engine behaviour and ticket (re-rank, provenance + replay, gaps,
offline, planner, i18n) intact.

**Blocked by:** 01–07, 14–19 (behavioural slices this restyles)

**Status:** done (agent, 03 Oct 2026)

- [x] Token system replaced with the Stitch palette: slate light + true-black
      dark, authority blue `#0b3d66`, azure `#4aa3ff`; Plus Jakarta Sans /
      JetBrains Mono / Noto Sans Devanagari with system fallbacks
- [x] Splash, get started, language (1/4), sign-in (2/4), location (3/4),
      persona (4/4) — every step skippable, Skip lands on the commuter home
- [x] Home: map hero (schematic, station tint by the visibility rule), sheet
      with peek/half/full, active-first persona chips, hero card, metric tiles,
      source row, today's window card, honest gap rows
- [x] Provenance sheet restyled: source · endpoint (copy) · station · issued ·
      age (+ fresh chip) · type · raw summary · raw JSON · replay · citation
- [x] Settings: profile, saved places, language select, persona editor,
      provenance toggle, notifications → inbox, planner row, feedback, about,
      delete-data (clears on-device state and returns to first run)
- [x] Map tab with station list + honesty caption; Places tab restyled;
      Planner restyled, reachable from Settings and the today card
- [x] Dark theme follows the system; `?theme=light|dark` pins it for demos
- [x] App split into `core.js`, `icons.js`, `views/*`, `app.js` (FILEMAP §2)
- [x] Offline contract intact (SW v7 precaches the new asset set)

## Comments
- 2026-10-03: Implemented from the Stitch export. Faithful where it counts
  (structure, palette, typography, severity = dot + word, 44px targets) and
  honest where the mock was ahead of the build: sign-in shows its Firebase gap,
  GPS/search show the keyed-API gap, notifications open the real inbox, and the
  map keeps its schematic caption. Medium severity is authority blue (no amber),
  per the mock. `node --test` 32 pass; `node app/selftest.js` green; offline
  cold start and 320px reflow verified in a browser.
