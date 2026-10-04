# 17: Activity model + window engine v1

**What to build:** The activity/routine model (presets inside personas; explicit manual entry; stored on-device) and the deterministic window engine — hard gates + a versioned weighted comfort score, daylight-constrained, resolution-adaptive — with `replay` extended to windows.

**Blocked by:** 02 (advisory engine v0 + replay), 03 (persona model)

**Status:** done-partial (agent, 03 Oct 2026)

- [x] Activity presets ship (volleyball/run/walk/office, version-pinned); routines added/removed on-device, never synced to Firestore
- [x] Routine record: activity · days · departure time — user-entered only; stored on-device
- [x] Windows: hard gates first (IMD sigwx + rain + heat-index bands), then a versioned weighted comfort score — 3-h blocks baseline (1-h needs MausamGram #27 via 13)
- [x] Weights live in a versioned config; unknown activities fall back to default weights
- [x] Every window/score exposes formula, weights, per-component source chips, and excluded/gap metrics
- [x] Same logged inputs → byte-identical window; `replay` extended to windows
- [x] Named states: no-good-window · rest day · adapter unavailable → excluded + disclosed · offline → cached with age
- [x] Unit tests: weight-config version pinning, determinism, preset fallback

## Notes

- Adapter inputs (CPCB AQI, CAMS UV) arrive through ticket 20's normalised provenance envelope; when absent → the metric is excluded and disclosed, never fabricated.
- Score model accepted in Q28; volleyball preset example in `PRD-SIH26076-Mausam.md` A.3 (Fitness table).

## Comments

- 2026-10-03: Created (v1.1, Q21/Q22/Q27/Q28).
- 2026-10-03: Landed slice (`ACTIVITY_PRESETS` + fallback + tests). Gate-boundary tests for live nowcast categories and 1-h resolution need keyed endpoints (13).
- 2026-10-03: Planner UX pass — custom activities landed (Q22's "later"
  pulled forward). Any name + the weighted metrics that matter
  (heat/humidity/wind/AQI/UV), carried at the pinned `windows-v1` version.
  The engine validates (`checkCustomActivity`) and discloses the weights
  used in the result and replay; a preset always beats a same-name custom;
  malformed configs throw, never zero-fill. Rain/storms stay hard gates —
  never weighted, so not offered in the builder.
