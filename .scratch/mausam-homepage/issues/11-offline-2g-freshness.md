# 11: Offline / 2G + freshness

**What to build:** Cache-first offline behaviour with visible freshness: a cached personal bundle that loads on 2G, per-value age badges, and a global "last updated / offline" strip.

**Blocked by:** 01 (walking skeleton)

**Status:** done-partial (agent, 03 Oct 2026)

- [x] The personal bundle (~15 KB) is cached; first render is cache-first
- [x] Every value shows an age badge
- [x] A global "last updated / offline" strip is shown
- [ ] A missing or expired source degrades to "last known, age shown" — never silent emptiness

## Comments

- 2026-10-03: Landed slice. SW is cache-first same-origin with background refresh (`mausam-home-v5`); fixtures + engine precached; Offline pill + freshness strip live. Expired-source "last known" labelling is finale work (needs the live staleness feed from 13).
