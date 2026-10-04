# 04: Provenance interaction

**What to build:** Tapping any number opens a provenance sheet (source, endpoint, station, issue time, age, a collapsible raw-payload view, and a Replay action); a global toggle reveals source chips on every number at once.

**Blocked by:** 02 (advisory engine v0)

**Status:** done (agent, 03 Oct 2026)

- [ ] Tapping any value opens the sheet with endpoint / station / issue time / age
- [ ] The raw API JSON is viewable (collapsible) and matches the source payload
- [ ] The global toggle reveals source chips on all numbers simultaneously
- [ ] The Replay action re-derives the card

## Comments
- 2026-10-03: Landed. Tap any metric or source row opens the sheet (source, endpoint, station, issue, age,
  triggering facts, collapsible raw JSON, Replay action asserting byte identity live).
  Global (i) toggle chips every value. Evidence: `docs/evidence/ticket-04-provenance.png`.

