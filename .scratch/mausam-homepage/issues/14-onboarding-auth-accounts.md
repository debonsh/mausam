# 14: Onboarding, auth & accounts (Firebase)

**What to build:** The product's front door and its optional identity layer — a
three-step, fully skippable first run (language → location → persona) and, when the
user wants sync, sign-in via Firebase Authentication (passwordless email link, or
Google OAuth) that persists a session and syncs saved places.

**Blocked by:** 01 (shell). Unblocks 15 (settings/sync UI).

**Status:** done-partial (agent, 03 Oct 2026)

- [ ] First run is ≤3 steps (language · location · persona); **every step skippable**
- [ ] Each step has a sensible default; "Skip" lands on the commuter home, not a blank screen
- [ ] Personas use the PS's own eight words (recognisable to a judge)
- [ ] Guest mode is default: the home is fully usable with no account
- [ ] Sign-in works via passwordless email link and via Google OAuth
- [ ] Session (Firebase ID token) is persisted client-side and **survives offline** (cached)
- [ ] Sign-out is available and clears local account state
- [ ] No secret is shipped in the client (only the public Firebase web config)
- [ ] Firestore Security Rules are the only thing protecting user rows (verified with a second account)

## Notes

- Decision record: `../../docs/adr/0001-firebase-auth.md`.
- Architecture: `../../Mausam/APP.md` §3.3, §4; design flow: `../../Mausam/DESIGN.md` §6.1.
- Onboarding was previously referenced as "ticket 12" in `DESIGN.md` §6.1; this
  ticket takes ownership of onboarding so 12 (i18n + a11y) stays scoped. Update that
  reference when this lands.
- Keep account creation out of the critical demo path: the judge must reach the home
  without signing in.

## Comments

- 2026-10-03: Created. Pulled into the mock phase (see `Mausam/ROADMAP.md` §3) because
  onboarding is the first thing a judge sees.
- 2026-10-03: Landed partial. Three-step skippable onboarding (language, location, persona) with defaults;
  Skip lands on the commuter home; guest-first throughout; Places screen works on-device with an honest
  signed-out sync explanation. `firebase/firestore.rules` + `firebase.json` + `.env.example` (names only)
  committed; no secret ships. NOT live: passwordless/OAuth sign-in and second-account Rules verification
  need the Firebase project (ADR-0001 follow-up, finale with ticket 15). DESIGN.md sixth reference to
  onboarding-as-ticket-12 still to be updated when ticket 12 lands.
  Evidence: `docs/evidence/ticket-14-onboarding.png`, `ticket-14-places-guest.png`.

