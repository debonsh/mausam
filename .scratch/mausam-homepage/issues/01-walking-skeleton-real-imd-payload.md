# 01: Walking skeleton — real IMD payload → one frozen hero card, offline

**What to build:** A phone-frame PWA shell that renders a single action card — imperative action, triggering facts, and a source/age chip — driven by one real captured IMD response, and that loads with the network disabled.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] A real IMD response is captured (public GeoServer WFS, or the API Test Console) and committed as a fixture
- [x] The home renders exactly one action card from that fixture
- [x] The card shows action + triggering facts + source/age chip
- [x] It renders with the network disabled (cache-first)
- [x] ~~It runs inside a phone frame~~ → **superseded** by team request: the decorative phone bezel/status-bar was removed; the mock is now a responsive full-viewport mobile app (`max-width: 480px`, safe-area insets)

## What landed

- **App:** `Mausam/app/` — vanilla PWA (no bundler): `index.html`, `styles.css`, `app.js`, `sw.js`, `manifest.webmanifest`.
- **Fixture (real):** `Mausam/app/fixtures/imd-synop-delhi-2026-10-02.json` — a live `GetFeature` from IMD's public GeoServer (`reactjs.imd.gov.in/geoserver/wfs`, layer `imd:synop_data_layer`, BBOX over Delhi, captured 2026-10-02). Provenance in the sibling `.capture.json` (URL, request, timestamp, sha256).
- **Derived card:** nearest station = *New Delhi-Safdarjung* → visibility 2 km ⇒ **“Reduced visibility — allow extra time on the road”**, facts `Visibility 2 km · Temp 25.8 °C · Humidity 90% · Rain 24 h 0 mm`, chip `IMD SYNOP · New Delhi-Safdarjung · 02 Oct, 23:38 IST · 2 h 38 min old`.
- **Check:** `node app/selftest.js` (asserts nearest station + severity + action).
- **Evidence:** `Mausam/docs/evidence/ticket-01-home-offline.png` (rendered with Chrome offline mode on).

## Why this data source

`api.imd.gov.in` returned `401 — needs to be whitelisted` from this network (the static-IP gate). The public IMD GeoServer is keyless and returns genuine IMD observations, so the fixture stays IMD-native rather than falling back to a foreign model.

## Comments

- 2026-10-02: Implemented and verified (browser offline reload renders the card cache-first).
- 2026-10-02 (follow-up): removed the decorative phone bezel per team request (now responsive, full-viewport). Found and fixed an inverted offline-badge condition (badge showed while online). Switched the service worker from **cache-first to network-first with a cache fallback** — the offline guarantee is unchanged, but code changes are no longer served stale and the manual cache-version bump is gone.
- 2026-10-02 (UI): refined the card into an Apple-leaning product surface (large-title header, eyebrow + imperative action, 3-metric row, source row that reveals the raw endpoint via the provenance toggle, translucent tab bar, light/dark). Removed the coloured left-border card as a generic tell. Measured WCAG contrast on all small text: light 5.20–8.67, dark 5.22–6.61, all ≥ AA.
- 2026-10-02 (mobile): locked to a **white theme** (dark tokens parked, `color-scheme: light` pinned); added the motion inventory (header stagger, live-dot pulse, card 3-beat, metric stagger, endpoint grid reveal, chevron rotate, press states); made it an **installable mobile app** (standalone display, portrait, maskable + standard SVG icons, `theme-color` white, apple/mobile web-app meta, safe-area insets, `overscroll-behavior: none`, tap-highlight suppressed).
- 2026-10-02 (mobile verification): iPhone 12 viewport renders with no horizontal scroll; 320 px reflows with no horizontal scroll; `prefers-reduced-motion` collapses 0.32 s → 0.01 ms; provenance reveal verified expanding (0px → 22.09px) with the chevron rotating. Evidence: `docs/evidence/mobile-home.png`, `mobile-provenance.png`, `mobile-320.png`.
- 2026-10-02 (caveat): Chrome's CDP offline emulation does **not** flip `navigator.onLine`, so the offline badge can't be exercised that way; offline *rendering* is proven (the card renders with the network emulated off). The badge is driven by `navigator.onLine` + the `online`/`offline` events, which are correct on a real device.
