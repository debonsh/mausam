# 02: Advisory engine v0 + replay endpoint

**What to build:** Deterministic rules that turn a normalised IMD payload into an advisory card with its triggering facts, plus a `replay` endpoint that re-derives the same advisory byte-identically from logged inputs.

**Blocked by:** 01 (walking skeleton)

**Status:** done (agent, 03 Oct 2026)

- [ ] Given the ticket-01 fixture, the engine emits the same hero card the UI shows
- [ ] Hero selection is severity → persona weight → recency, and the rule is unit-tested
- [ ] Every card carries its triggering inputs
- [ ] `replay` on the same inputs returns byte-identical output

## Comments
- 2026-10-03: Landed. Engine extracted to `Mausam/app/engine/deriveCard.js` (framework-free, Node + browser).
  Stack: visibility/rain/heat rules over SYNOP obs; hero = severity, persona weight, recency, id.
  `replayStack` canonicalises with sorted keys; `node app/selftest.js` + `node --test tests/` assert byte identity.
  All four acceptance boxes hold on the frozen ticket-01 fixture (same hero card).

