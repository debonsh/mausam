# 09: Deep persona — Agriculture

**What to build:** The Agriculture persona built to depth: the agromet advisory rendered as templated imperative actions, plus ground-frost, rainfall-vs-normal, and basin-QPF cards, with soil moisture as a gap card.

**Blocked by:** 03 (persona model), 06 (bottom-sheet home shell)

**Status:** done-partial (agent, 03 Oct 2026)

- [ ] The agromet advisory (API 28) renders as templated, human-reviewed imperative actions, with the raw advisory text visible in provenance
- [x] Ground-frost renders from held obs (≤2 °C, high sev); warm obs stay silent
- [ ] Rainfall-vs-normal and river-basin QPF cards render
- [x] Soil moisture renders a gap card

## Comments

- 2026-10-03: Landed slice. Agromet text (API 28), rainfall-vs-normal climatology and basin QPF need keyed endpoints — still host-gated via 13. Rain card already re-ranks agriculture-first via the fixed weight table.
