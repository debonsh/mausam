# 06: Bottom-sheet home shell

**What to build:** The map + bottom-sheet home shell — peek/half/full snap points, persona chips pinned in the sheet header, and the IMD WFS district-warning overlay.

**Blocked by:** 01 (walking skeleton), 03 (persona model)

**Status:** done-partial (agent, 03 Oct 2026)

- [ ] The sheet snaps at peek / half / full; it opens at half
- [ ] It auto-raises on a severe (orange/red) warning and never forces full
- [ ] Persona chips are pinned in the sheet header and switch persona
- [ ] The map shows the IMD WFS district-warning overlay in IMD's four-colour convention
- [ ] `prefers-reduced-motion` is respected (snap without spring)

## Comments
- 2026-10-03: Landed partial. Sheet snaps peek/half/full (opens at half), drag handle + tap cycle,
  `prefers-reduced-motion` respected, persona chips pinned in the header.
  Severe auto-raise is implemented (hero sev high raises peek to half, never full) but unobserved:
  no severe warning exists in the frozen fixtures. Map is a labelled schematic tinted by the live SYNOP
  visibility rule in IMD four-colour convention; the full WFS district-warning overlay needs keyed
  endpoint 6 (finale, ticket 13). The Map tab became the Planner tab; the map lives on Home (DESIGN Q9 open).
  Evidence: `docs/evidence/ticket-06-sheet-shell.png`.

