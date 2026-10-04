# 10: Deep persona — Health

**What to build:** The Health persona built to depth: heat/cold warning codes rendered as actions, with AQI, UV, and pollen shown as the honesty showcase (gap cards, or a labelled CPCB value for AQI).

**Blocked by:** 03 (persona model), 05 (gap card), 06 (bottom-sheet home shell)

**Status:** done-partial (agent, 03 Oct 2026)

- [x] Heat (existing) + cold obs cards render as actions (≤5 °C high, ≤10 °C medium), humidity and wind carried as facts
- [x] AQI renders a gap card until ticket 20 lands the labelled CPCB value
- [x] UV and pollen render gap cards with a one-line reason

## Comments

- 2026-10-03: Landed slice. Heat/cold warning codes 9–13 and AWS temperature need keyed endpoints — still host-gated via 13. Cold/frost rules live but unobserved in fixtures (Delhi-October obs held).
