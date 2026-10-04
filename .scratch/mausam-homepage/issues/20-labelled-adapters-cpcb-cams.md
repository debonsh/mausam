# 20: Labelled adapters — CPCB AQI (+ XKDR mirror) & CAMS UV

**What to build:** Backend adapter clients for the two accepted non-IMD sources, normalised into the same provenance envelope as IMD values and demoted to gap cards when unavailable.

**Blocked by:** 13 (backend host + gateway). Related: 05 (display states), 16 (captures), 17 (engine inputs).

**Status:** ready-for-human

- [ ] CPCB national AQI via data.gov.in (GODL), key backend-only; normalised with station · issue time · age · **provisional** flag ("live data, may display errors")
- [ ] XKDR labelled mirror (CC BY 4.0) used only when CPCB is unreachable/stale, always labelled "mirror — India Air Quality Database, XKDR Forum"; `app.cpcbccr.com` is never used or labelled CPCB
- [ ] CAMS UV (Copernicus ADS or an equivalent licensed feed): hourly forecast with model run + age; UI label "Non-IMD · Copernicus CAMS"; attribution "Generated using Copernicus Atmosphere Monitoring Service Information 2026"
- [ ] SAFAR is not integrated (no API, no licence, degraded — ADR-0002); pollen stays a gap card (no official Indian source)
- [ ] Unavailable → gap card with a one-line reason; adapters never trigger severe alerts (IMD-only rule)
- [ ] Reachability validated from the static-IP host on day one; captures committed as fixtures with provenance for tests
- [ ] Attribution ledger updated per source; `.env.example` lists key names only (no values)

## Comments

- 2026-10-03: Created (v1.1, Q24; ADR-0002).
- 2026-10-03: Day-one signal from the build host: api.data.gov.in connection refused; XKDR keyless paths 404/DNS-unknown. Attempt record: Mausam/app/fixtures/aqi-delhi-2026-10-03.unavailable.json. Validate from the static-IP host on finale day one; CAMS-via-Open-Meteo path proven working (ticket 16).
- 2026-10-03: Docs-only pass — host-gated via 13 (day-one `api.data.gov.in` validation needs the static-IP host + a human-held GODL key). No code touched.
