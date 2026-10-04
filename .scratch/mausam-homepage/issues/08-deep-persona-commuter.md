# 08: Deep persona — Commuter

**What to build:** The Commuter persona built to depth: fog, nowcast (rain and lightning), and NHAI highway cards rendered from IMD data, with traffic shown as a labelled adapter or a gap.

**Blocked by:** 03 (persona model), 06 (bottom-sheet home shell)

**Status:** done-partial (agent, 03 Oct 2026)

- [x] Thunderstorm sigwx (17/19/27/29/91–99) renders a high-sev action card from the held obs; calm codes stay silent
- [x] Traffic appears as an honest gap card until ticket 20 lands a labelled adapter
- [x] The hero card follows the severity → persona → recency rule

## Comments

- 2026-10-03: Landed slice. Fog reads the existing visibility rule (≤1 km high, ≤4 km medium). Nowcast rain/lightning + NHAI 21/22 cards need keyed endpoints 6/21/22 — still host-gated via 13. Storm rule live but unobserved in fixtures (no thunderstorm sigwx held).
