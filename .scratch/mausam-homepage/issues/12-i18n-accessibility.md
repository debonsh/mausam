# 12: i18n (EN + Hindi) + accessibility pass

**What to build:** Template-first localisation for English and Hindi (with a language toggle), and an accessibility pass covering screen-reader labels, keyboard navigation, and high-contrast severe-weather states — including the planner, routine setup, and alert/inbox surfaces (v1.1).

**Blocked by:** 03 (persona model), 06 (bottom-sheet home shell)

**Status:** done-partial (agent, 03 Oct 2026)

- [x] UI strings come from templates; a language toggle switches EN/HI
- [x] Warning and alert text is human-reviewed, never raw machine translation
- [ ] Alert copy is template-first (title + body + source line), EN + Hi, and the payload carries source · issue · age
- [x] Screen-reader labels, keyboard navigation, and high-contrast severe states are in place across the new surfaces (planner, activities, inbox)

## Comments

- 2026-10-03: v1.1 — added alert copy + planner/activities/inbox surfaces to the scope.
- 2026-10-03: Landed slice. `app/i18n.js` holds reviewed EN+HI chrome strings with EN fallback; toggle persists; `:focus-visible` rings + high-contrast severe borders + labelled controls. Live warning HI copy stays EN until a reviewer signs it; push-payload copy is ticket 18.
- 2026-10-03: Planner UX pass chrome added (custom-activity builder, routine
  form labels, metric names), template-first EN + HI; Hindi awaits the same
  human review as the existing chrome.
