# 16: Planner screen — static best-window slice (real captured payloads)

**What to build:** An Activities/planner screen in the mock that renders one volleyball "best window" from committed real captures — a deterministic derive only (no engine generalisation, no push, no live adapters) so the idea-submission demo shows the activity layer on screen.

**Blocked by:** None (ticket 01 is done). Independent of 02–07 by design — it must never block the core mock.

**Status:** done (agent, 03 Oct 2026)

- [ ] Captures committed with provenance siblings (`.capture.json` pattern from ticket 01): IMD daily/nowcast + sun/moon; CPCB AQI (or the XKDR labelled mirror if `api.data.gov.in` is unreachable — ADR-0002); CAMS UV
- [ ] The screen renders: one best-window card + up to 2 alternate windows + at least one "avoid" block, in 3-hour blocks
- [ ] The window card obeys the fixed anatomy (imperative headline + triggering facts + source/age chip); every value carries a chip (IMD · station · issue · age; adapters labelled "Non-IMD · CPCB" / "Non-IMD · Copernicus CAMS")
- [ ] Window provenance shows config version, weights, per-component chips, and excluded (gap) metrics; grain is stated on screen ("3-hour blocks — IMD publishes no finer numeric forecast", Q27)
- [ ] Deterministic: same captures → same window; a fixture test asserts it (extends the `selftest.js` pattern)
- [ ] At least one named degradation state is rendered ("No good window today" and/or "Rest day — no routine")
- [ ] No live keys in the client; no push; no scheduler
- [ ] Screenshot captured to `docs/evidence/` for ticket 07

## Notes

- Source policy and attribution strings: `docs/adr/0002-labelled-adapters.md` (Q24). Safety triggers are IMD-only; adapter values never raise an alert.
- Score model: hard gates (rain, thunderstorm/lightning, heat extremes) → versioned weighted comfort score; daylight constraint via sun/moon (endpoint 15). The full engine is ticket 17; this slice freezes one config (`windows-v1`) and one activity preset (volleyball).
- Grain and copy must match the final engine, so the deck never promises minute precision (Q27).

## Comments

- 2026-10-03: Created (v1.1 amendment, Q23) — the Oct 5 pull-forward for the planner. Tripwire: if tickets 02–07 aren't green by 4 Oct evening, this drops to a deck design and ships at the finale instead.
- 2026-10-03: Landed, full static slice (tripwire not triggered: 02-07 green).
  Real captures: fresh IMD SYNOP 2026-10-03, CAMS UV via Open-Meteo (labelled Non-IMD), computed solar
  bounds (labelled, approximate). AQI has no reachable source from here (data.gov.in refused, XKDR paths
  404; attempt record committed) so it renders the adapter-unavailable gap and is excluded from the score
  with disclosure. Best window b06 (06:00-09:00, 72/100) + alternates + avoid + rest-day state + grain
  statement + window provenance with weights and replay. No keys, no push, no scheduler.
  Evidence: `docs/evidence/ticket-16-planner-best-window.png`, `ticket-16-rest-day.png`.
- 2026-10-03: Planner UX pass — "New activity…" in the picker opens a builder
  card (name + which weather matters) under the activity selector; custom
  activities then appear in both selectors and flow through the engine like
  presets. EN+HI chrome strings added via the ticket-12 template pattern.

