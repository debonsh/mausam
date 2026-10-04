# ADR-0002 — Non-IMD data policy: labelled adapters, India-first

- **Status:** Accepted
- **Date:** 2026-10-03
- **Context:** SIH26076 "Mausam personalised homepage" (`Mausam/`)
- **Deciders:** Team (product + engineering)
- **Related:** `Mausam/PRD-SIH26076-Mausam.md` §4, §9, §15, FR-18/FR-20, Q24; tickets 16, 17, 20
- **Amends:** PRD §9's open-ended "others as available"; refines the Health/Fitness gap presentation in §4

## Context

The product's moat is **IMD-native lineage**: the field reality is that most rival "Mausam" apps surface a global model (e.g. Open-Meteo) under IMD branding, and our opening is provenance depth — source · station · issue time · age on every value, and honest gap cards where IMD publishes nothing.

But the personas (volleyball player, health-conscious user, office commuter) legitimately want metrics IMD does not publish — **AQI, UV, pollen** — and "always show a gap" answers the honesty question but not the user need. We needed a sourcing rule that satisfies both.

Research findings (2026-10-03, web-verified — see ticket capture notes):

1. **AQI:** CPCB publishes the national AQI via a documented, keyed API on `api.data.gov.in` (dataset "Real time Air Quality Index from various locations"), licensed under GODL, hourly, all-India — but the data is "live, without human intervention … may display errors". `api.data.gov.in` was unreachable from one test environment — reachability must be validated from the production host.
2. **AQI (traps):** `app.cpcbccr.com` is **not** CPCB in 2026 (a private project re-serving multiple datasets). SAFAR (MoES/IITM) has **no AQI API** and its public channels are degraded.
3. **UV:** **No Indian API exists.** SAFAR's city UV page (Pune/Mumbai/Ahmedabad only, Delhi absent) has no API, no licence, degrading channels, and showed internally inconsistent same-timestamp readings (Pune: 3.3 vs 8.8). IMD has no UV product (its radiation stations are request/payment-gated with a non-commercial clause). Copernicus **CAMS** (EU) offers a free, licensed, hourly UV forecast with WHO methodology.
4. **Pollen:** **No official Indian source**, no API. Google's Pollen API does not cover India; Open-Meteo/CAMS pollen is Europe-only; Ambee's is paid model data with species-level data unavailable for India.
5. XKDR's "India Air Quality Database" (CC BY 4.0, no rate limits) mirrors 558 CPCB stations plus 5 US-embassy monitors — usable as a **labelled** fallback, never as an official source.

## Decision

A three-tier policy, applied to every non-IMD value:

1. **Tier 1 — IMD** is always first: keyed API, then public WFS, then CAP/RSS floor.
2. **Tier 2 — labelled official-Indian adapters:** CPCB national AQI via `data.gov.in` (GODL); the **XKDR** database may stand in only when CPCB is unreachable/stale, always labelled as a mirror citing CPCB and XKDR.
3. **Tier 3 — labelled public-institution adapter where India has none:** **Copernicus CAMS** (EU) for UV only. Free, licensed (attribution required), hourly forecast.
4. **No licensed source → gap card.** Pollen stays a pure gap card; it anchors the honesty showcase.

Invariants:

- **Safety-critical triggers are IMD-only.** Any warning or alert trigger (heat, fog, lightning, etc.) must originate from IMD; adapter values may inform comfort/activity scoring but can never raise a severe alert.
- **Every adapter value carries its own provenance**: source · station/grid · issue time (or model run) · age, plus a **provisional** flag where the upstream says so (CPCB).
- **Never unlabelled, never IMD-branded.** No global-model data presented as IMD; no private mirrors presented as government sources; attribution strings are tracked per source and shown in provenance.
- **`app.cpcbccr.com` is banned** as a source and as a label.
- **SAFAR is not integrated** (no API, no licence, degraded, unreliable values) — it is cited in docs only.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| **Open-Meteo (or any global model) as a general provider** | Exactly what the rival field does; destroys the IMD-native moat. Allowed only as CAMS's licensed UV feed if needed — and then labelled as CAMS/Open-Meteo, never IMD. |
| **Scrape SAFAR's UV page** | No API, no licence, three cities only (Delhi absent), degraded site, and observed inconsistent values. Ungovernable and unlicensable. |
| **Buy Ambee pollen** | Paid model data (not monitoring); species-level data unavailable for India; "monitoring" would be an overclaim. Pollen gap kept instead. |
| **Keep gaps everywhere (status quo)** | Honest but fails the personas' real need and the plan/alert features; invalidated as the default by this ADR. |
| **AirNow (US embassy monitors)** | Official and API-friendly, but covers 5 cities with a foreign-monitor story that confuses an Indian product. Skipped. |

## Consequences

**Positive**

- The planner/alert features get real values for AQI and UV without breaking honesty: each is a *labelled* adapter with its own provenance.
- The honesty showcase survives in a stronger form: one screen can show IMD-native + labelled adapter + gap (pollen) side by side.
- Attribution and licence posture are documented up front (GODL for CPCB; CC BY 4.0 for XKDR; Copernicus notice for CAMS).

**Negative / costs**

- Keys/credentials for `data.gov.in` and CAMS live on the backend; adapter staleness and terms must be re-checked (licences can drift — SAFAR is the cautionary tale).
- `api.data.gov.in` reliability is unproven; the XKDR mirror path must exist and be labelled.
- CAMS is model data — copy must say "forecast/model", never "monitoring".

**Neutral**

- The PRD's Health persona presentation changes: AQI/UV become labelled adapters where coverage exists; the gap card remains for pollen and for any adapter outage.

## Compliance with existing decisions

Extends PRD §5 principle 1 ("Every value is an IMD product, or explicitly labelled non-IMD") and FR-8 (gap cards). Does not alter guest-first/privacy (ADR-0001) or the no-fabrication rule.

## Follow-ups

1. Ticket 20 implements the adapter clients + fixtures; validate `api.data.gov.in` reachability from the static-IP host on day one.
2. Add per-source attribution strings to the provenance sheet and the attribution ledger.
3. Deck copy: say "labelled adapters — CPCB / Copernicus CAMS", never "IMD UV" or "CPCB data" when it is the XKDR mirror.
4. Re-check CPCB/CAMS terms before any pilot.
