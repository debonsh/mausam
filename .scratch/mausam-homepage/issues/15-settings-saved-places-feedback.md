# 15: Settings, saved places & feedback

**What to build:** The account-scoped surface behind the home — edit profile and
personas, manage saved places (traveller persona), leave feedback on an action, and
delete your data. Signed-in only for sync; every screen has an honest signed-out
state.

**Blocked by:** 14 (auth/session). Related: 03 (persona model), 06 (Places tab).

**Status:** done-partial (agent, 03 Oct 2026)

- [ ] Settings screen: profile (display name), personas, language, sign-out
- [x] Saved places: add / rename / remove, on-device (account sync needs the Firebase project)
- [x] A saved place syncs across a reload (second device/session needs the Firebase project)
- [x] Feedback: "was this action useful?" from a card, on-device with counts
- [ ] Account deletion removes the user's rows
- [x] Fully usable offline: cached places render
- [x] Signed-out state teaches what signing in unlocks, and never blocks the home

## Notes

- Data model: `Mausam/APP.md` §4; security rules in `Mausam/firebase/firestore.rules`.
- Privacy: only explicit saves and feedback are stored; no behavioural tracking
  (`Mausam/PRD-SIH26076-Mausam.md` §11).

## Comments

- 2026-10-03: Created alongside ticket 14.
- 2026-10-03: Landed local slice (`app/personal.js`, pure + tested). Profile name, cross-device sync, queued-sync and account deletion need the Firebase project (14).
