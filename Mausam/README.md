# Mausam — a persona-aware, provenance-first home screen

**Smart India Hackathon 2026 · PS 26076 — "Development of personalized homepage for the 'Mausam' mobile application"**
Ministry of Earth Sciences (MoES) / India Meteorological Department (IMD) · Software · Smart Automation

> **One line:** *The Mausam home screen that tells you what to do — and proves where every number came from.*

This is **not** a separate weather app. It rebuilds IMD's own **Mausam home screen** as a persona-adaptive **decision layer**: it turns IMD's official data into *actions* rather than charts, and every number is traceable to its source, station, issue time, and age. Where no source exists (pollen) it renders an honest **gap card** instead of inventing a number; where a labelled adapter exists (Copernicus CAMS UV in the planner) the value carries its own source chip.

## What it is / is not

- **Is:** the app's home screen; a decision stack in the existing map + bottom-sheet shell; IMD-first by construction.
- **Is not:** a new app; a forecast generator (IMD forecasts — we consume); a chatbot; a tile dashboard.

## Status

| Stage | Deliverable | State |
|---|---|---|
| Idea submission (**5 Oct 2026**) | Official 6-slide deck + offline clickable mock on **real captured IMD payloads**, incl. onboarding + planner slice | Done 03 Oct — tickets 02–07, 16, 21 landed (Stitch UI direction: splash + 4-step onboarding, home, provenance, settings, map/places, dark mode); 14 partial (sign-in needs Firebase project); deck PDF in `docs/deck/` |
| Finale (Nov–Dec 2026) | Working pipeline vs keyed IMD APIs, 3 deep personas, provenance + replay, offline PWA, EN/HI, a11y, accounts, planner + alerts live | Not started (tickets 08–13, 15, 17–20) |

Live build state and done-when criteria: **[`ROADMAP.md`](./ROADMAP.md)**.

**Critical path:** IMD's keyed API is bound to a static public IP and needs an hourly user JWT — a **static-IP host must be provisioned** (ticket 13). Until then the mock runs on IMD's public **GeoServer WFS** so every displayed value is still genuinely IMD.

## Docs

| Doc | Contents |
|---|---|
| [`APP.md`](./APP.md) | Ecosystem, architecture, tech stack, auth/accounts, data chain, advisory engine, end-to-end flow, finished-prototype definition |
| [`DESIGN.md`](./DESIGN.md) | Design philosophy, token system, the card grammar, and every UI flow |
| [`ROADMAP.md`](./ROADMAP.md) | Phased sequencing, build state by surface, milestones, risk register |
| [`FILEMAP.md`](./FILEMAP.md) | Where every file lives: target layout, responsibilities, conventions |
| [`PRD-SIH26076-Mausam.md`](./PRD-SIH26076-Mausam.md) | Signed-off product requirements, decisions Q1–Q20, deep UI spec (Appendices A–C) |
| [`../docs/adr/0001-firebase-auth.md`](../docs/adr/0001-firebase-auth.md) | ADR: Firebase for auth + account data |
| [`../blueprint/content-02.md`](../blueprint/content-02.md) | The 4-PS blueprint section for this PS |
| [`../.scratch/mausam-homepage/issues/`](../.scratch/mausam-homepage/issues/) | The 20 implementation tickets |

## Repository layout

```
Mausam/                      ← this product
  app/                       ← the PWA (index.html, app.js, core.js, icons.js, views/, styles/, engine/, fixtures/, sw.js)
  docs/                      ← UI-DIRECTION.md · ui-references/ · evidence/ · deck/
  tests/  firebase/          ← landed; backend/ is finale (tickets 13, 17–20)
  README.md  APP.md  DESIGN.md  ROADMAP.md  FILEMAP.md  AGENTS.md
  PRD-SIH26076-Mausam.md
../blueprint/                ← build inputs + PDF generators for all four PSs
../.scratch/mausam-homepage/ ← tickets (local-markdown tracker)
../docs/adr/                 ← architecture decision records
../docs/agents/             ← tracker / domain / triage conventions
```

The full target layout and every file's responsibility are in **[`FILEMAP.md`](./FILEMAP.md)**.

Run the mock: `python3 -m http.server 8765 --directory Mausam/app` → <http://127.0.0.1:8765/> (works offline once loaded). Verify: `node Mausam/app/selftest.js` and `node --test Mausam/tests/`.

## Prior art

Built with reference to public SIH26076 solutions (all credited in `APP.md`): `Shreyansh303/team_mausam_sih_2026` (Flutter+FastAPI, 33-card catalog, scoring engine, admin demo console — MIT), `optimusprime123x/SIH2026-Mausam`, `Sovereign-Immortal/mausam`, `xarjunpatil/SIH26076-…`. **We borrow patterns, not branding**; verify each repo's licence before copying code, and attribute.

*This is a student prototype and is not affiliated with or endorsed by IMD or MoES.*
