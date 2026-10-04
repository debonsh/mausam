# 05: Gap card (honesty state)

**What to build:** An inline gap card shown *in place of* a metric IMD does not publish — no number, with a one-line reason — and a labelled-adapter card where a licensed non-IMD source exists (CPCB AQI · Copernicus CAMS UV; ADR-0002). Pollen stays the pure gap. The deck's third visual block shows the **mixed state** (v1.1).

**Blocked by:** 01 (walking skeleton)

**Status:** done (agent, 03 Oct 2026)

- [ ] A missing metric renders in place of the value, not beside it
- [ ] No number, no spinner, no "—", no fabricated zero
- [ ] It states "not published by IMD" plus a one-line reason
- [ ] Where a labelled adapter exists, its value shows with its own source chip
- [ ] A labelled-adapter card carries a **provisional** tag where the upstream says so (CPCB); an adapter outage degrades back to the gap card (ADR-0002)

## Comments

- 2026-10-03: v1.1 — third deck visual becomes the mixed state (IMD-native · labelled adapter · pollen gap); adapter values per ADR-0002.
- 2026-10-03: Landed. Pure pollen gap + AQI adapter-outage gap render in place (no number, reason stated).
  Labelled-adapter value card ships in the planner (CAMS UV with its own source chip, ticket 16).
  CPCB provisional tag is vacuous in the mock (no CPCB value reachable; outage renders the gap instead).
  Evidence: `docs/evidence/ticket-05-honesty-mixed.png`.

