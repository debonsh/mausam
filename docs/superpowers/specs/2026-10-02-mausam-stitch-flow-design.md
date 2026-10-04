# Mausam Stitch Flow — Apple-grade spec (2026-10-02)

Approach A approved: one Stitch project, light full flow + dark variants of 3 deck shots.
Goal: full flow for deck + PWA rebuild. Device: mobile portrait. Theme: light first, dark deck variants.

## 1. Direction (frontend-design-direction + HIG + industry)

- Purpose: 6 a.m. instrument — tell me what to do, prove where every number came from.
- Audience: commuter / farmer / health user repeating daily check; scan hero first.
- Tone: calm, refined, minimal. Neutral chrome, one authority-blue accent (#0b3d66), color is signal.
- Memorable detail: provenance sweep — one (i) toggle unmasks source·station·issue·age on every value at once.
- Constraints: mobile 480px, 44×44 targets, AA contrast, system stack, no fabricated numbers, guest-first.

Industry applied:
- Apple HIG onboarding: fast, fun, optional. 3 steps max, Skip always visible, sensible defaults, permission primed with why ("to show your district warning"), never a form.
- Apple Weather: detail (hero+metrics) + list (saved places) + map (overlays: warning/precip/air-quality). Severe banner interrupts calm.
- Bottom-sheet UX (LogRocket): full-bleed sheet, drag handle, non-modal paired with map, subtle 160–320ms slide, low density, close affordance, no backdrop-dismiss data loss.
- Polish (make-interfaces-feel-better): concentric radius (card 22/control 14/pill 999), tabular numbers, balance headings, tactile press scale .94–.96, transitions scoped (transform/opacity only), 44×44 hits.

## 2. IA — 10 screens (Apple-grade revision)

0. Launch/splash — Mausam mark + "IMD data, actions not charts", auto-advances, never blocks.
1. Language — English / हिंदी cards, default = device, Skip → commuter home. (1 OF 4)
2. Auth — "Sign in to sync" (link + Google), Skip + Continue-as-guest prominent; user-placed 2nd page, guest-first preserved via Skip. (2 OF 4, screen 216ef13e)
3. Location — Use current location (primed why) · search · popular. One tap, Skip → Delhi. (3 OF 4)
4. Persona — 8 PS personas as mobile 2-col icon cards (b0938e9e), multi-pick, first = primary. Skip → Commuter. (4 OF 4)
4. Home-Commutter — map behind + half-sheet: hero "Allow extra time on the road", fog code 15 + vis/temp/humidity, source/age chips, persona chip row, (i) toggle, tab bar Home/Map/Places/Settings.
5. Home-Agriculture — same shell, hero "Delay sowing by 3 days", agromet + rain-vs-normal + frost + basin QPF, soil-moisture gap card in place.
6. Home-Health — hero heat "Avoid outdoor exertion 12–4", 3 honest gaps (AQI/CPCB-labelled, UV, pollen) in place, never zeros.
7. Provenance sheet — grouped rows: Source/Endpoint/Station/Issued/Age/Raw JSON(collapsible)/[Replay advisory]. Swipe-down dismiss.
8. Auth — also reachable from Settings; onboarding placement is user-driven (deviates from DESIGN §6.1 three-step max and APP guest-first(Settings-only); mitigated by Skip-everywhere + Continue-as-guest).
9. Settings/Places — profile, language, saved places (synced), feedback "was this useful?", delete account, about/provenance note.

Homes (03 Oct refresh): pinned sticky persona header — 48px icon+label chips, active solid #0b3d66 + check, right-fade swipe cue, first-three visible; data visuals — map legend + glowing pin, hero severity top-edge + 22px headline, 3 icon metric cards tabular, 48px source bar. Honesty: no invented corridors/speeds/dew-points (commuter stripped 03 Oct).

Tab bar (Apple HIG): Home · Map · Places · Settings. Auth reached from Settings only, never blocks home.

## 3. Tokens — Authority Teal (user-picked 03 Oct, replaces #0b3d66 system)

Systems: `Mausam Authority Teal Light` (assets/16006490377248466860, seed #074E5C) · `Mausam Authority Teal Dark` (assets/2439719481266578077, seed #0E7C7B). Inter, ROUND_TWELVE. Teal ≤10% coverage (gov pattern), severity amber/red/green kept on heroes only, Settings notification row calm blue.
CAVEAT: Stitch apply regenerates from original prompts, so teal copies predate the 4-step renumber + honesty strips + blue-bell fixes — re-apply those edits on teal IDs before deck screenshots.

Light: --bg #f2f2f7, --surface #fff, --label #1c1c1e/2 #4b4b50/3 #656569, --accent #0b3d66, --ok #34c759, --alert #ff9500, --warn #ff3b30. Dark: bg #000, surface #1c1c1e, label #f2f2f7, accent #4aa3ff. Type: system stack, Large 34/700, Action 22/600, Metric 26/600 tabular, Unit 14, Body 17, Label 13/600, Caption 12, Tab 10, Footnote 11. Space 4·8·12·16·20·24·32. Motion 160/320ms, decelerate-out, reduced-motion collapses.

Rules: one lead element per screen (hero), severity = dot+word never color alone, sentence case, numbers carry unit+age, gap card muted in same slot. NO amber/orange/yellow anywhere (user call 03 Oct): watch-level renders Authority Teal light #074E5C / azure dark #4aa3ff; red warnings + green ok unchanged; words carry severity. Settings notification row calm blue (not amber).

## 4. Flows

- Onboard → Home (guest): every step skippable, progress dots, primary Continue + text Skip.
- Persona chip → deterministic re-rank, chrome static, chips animate only.
- (i) → global provenance sweep on/off, reversible, lifting-a-lid feel.
- Tap source row → provenance sheet for that value.
- Severe (orange/red) → sheet auto-raises to half, banner in words, urgency beats preference, never forces full.
- Offline → cached bundle renders, "Offline, showing cached data" + pill, live dot amber, ages kept.
- Auth → sync only; signed-out teaches value; delete path present.

## 5. Honesty

Real IMD captures only. Missing = gap card in slot ("IMD does not publish pollen"), labelled adapter (CPCB) with own chip where exists. No spinner-as-value, no dash, no zero.

## 6. Build order (Stitch) + verify

Project "Mausam Home" → light design system → screens mobile in order → full dark set via fresh generation (variants endpoint timed out 4x, generation used instead). Dark IDs: Settings 030b64b9 · Login2  c54417fc · Language d6aeae1a · Location 93825bc1 · Persona 11dfa82b · Commuter d6d7eb82 · Health 7c0affd3 · Provenance 3a45b4f1a · Agri 252637c6 (honesty strip pending verify). Old pre-refresh darks (b4219db4, e7be22da, 8c0ca05d) superseded. CANONICAL — project "Mausam Home Final" (projects/1778510294756867102), systems Final Blue Light (assets/8134080829265176999) + Final Blue Dark (assets/3184869390514897390). Apple tweaks baked in (safe-area, 44px, balanced type, tabular numerals, one accent, no gradients/glow) + harden (Skip paths, offline notes, Hindi room) + harmonized verbs. All 11 lights verified zero-amber + honest (sweep 03 Oct; commuter "amber" hit was a code comment only).
LIGHT: 01 splash 9ed57300 · 02 getstarted 5d0553e3 · 03 language 56f377b1 · 04 login 364cbf7b · 05 location 55b9ca29 · 06 persona 3a5b133c · 07 commuter c667e9d4 · 08 agri 606c5e7d · 09 health 4d872ba8 · 10 provenance dff26f57 · 11 settings fa49170c.
DARK: D01 d397765f · D02 dedb1580 · D03 963bdf82 · D04 d4c65c0d · D05 4352c0f8 · D06 dc649b6f · D07+D08 text-verified · D09 5f59f5cc (visually verified) · D10 d6d8ddcf · D11 486cccda (has invented 28.61°N/19.07°N coords — strip before deck). Old project 2618803029930949637 parked; delete only on user yes. Verify: 320px + 375px no h-scroll, 44×44 targets, AA, standalone feel, reduced-motion safe. Then port tokens/flows to PWA per FILEMAP.

## 7. Self-review

No TBD. Consistent with PRD/APP/DESIGN (dark variants explicitly user-overrode DESIGN white-only park). Scope = one flow, single plan. No ambiguous requirement: Stitch prompts carry real fixture numbers.
