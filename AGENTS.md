# Memory

## Project Overview
SIH 2026 workspace. Four problem-statement blueprints live in `blueprint/` (build inputs `content-0*.md`, `simple.md`; generators `build.py`, `build_final.py`, `build_tui.py`, `build_simple.py`).

The active project is **SIH26076 — "Personalised homepage for the 'Mausam' mobile application" (India Meteorological Department / MoES)**. Its product requirements live in `Mausam/PRD-SIH26076-Mausam.md`; the deep blueprint section is `blueprint/content-02.md`.

## Build & Run
- Regenerate the blueprint PDFs: `python3 blueprint/build.py`, `blueprint/build_final.py`, `blueprint/build_simple.py`, `blueprint/build_tui.py`.
- Requires `chromium`, `qpdf`, `pdftotext`, `pdfinfo` on PATH.

## Code Style Guidelines
- Use descriptive variable names
- Follow existing patterns in the codebase
- Extract complex conditions into meaningful boolean variables

## Architecture Notes
- The Mausam home is a **map + bottom-sheet decision stack** (faithful to the real app).
- Every value carries **IMD provenance** (source · station · issue time · age); advisories are **deterministic and replayable**.
- No fabricated numbers: missing data renders an **inline gap card**.
- The IMD keyed API is gated (key bound to a static public IP + hourly user JWT) — the key lives on a backend, never in the app.

## Common Workflows
- Issue tracking: local markdown under `.scratch/<feature>/` (see `docs/agents/issue-tracker.md`).

## Agent skills

### Issue tracker

Issues live as markdown files under `.scratch/<feature>/issues/`. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles, label strings equal to their names. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

<!-- antislop:start -->
## antislop
For UI, copy, people, mobile layout, or code comments work, read `.opencode/skills/antislop/SKILL.md` (core) and then the skill for the task:
- Copy & text: `.opencode/skills/antislop-copywriting/SKILL.md`
<!-- antislop:end -->
