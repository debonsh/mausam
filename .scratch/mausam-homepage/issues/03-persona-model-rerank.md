# 03: Persona model + deterministic re-rank

**What to build:** Persona selection (onboarding plus a chip row) and a deterministic home re-rank, so switching persona visibly reorders the action stack.

**Blocked by:** 02 (advisory engine v0)

**Status:** done (agent, 03 Oct 2026)

- [ ] A user can select and switch persona via chips
- [ ] Switching persona reorders the stack deterministically (same inputs → same order)
- [ ] The selection persists locally

## Comments
- 2026-10-03: Landed. Eight PS-word chips pinned in the sheet header; fixed persona-weight table in the engine;
  selection persists in localStorage; re-rank deterministic (same inputs, same order, replay-tested per persona).

