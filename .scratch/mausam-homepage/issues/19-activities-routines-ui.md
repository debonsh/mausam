# 19: Activities & routines UI

**What to build:** The real surfaces behind ticket 16's static slice — routine setup/editing, the week strip, per-day window detail, the notification inbox, and the "best window" card in the decision stack.

**Blocked by:** 15 (settings), 17 (activity model + window engine). Related: 16 (static slice), 12 (strings).

**Status:** done-partial (agent, 03 Oct 2026)

- [x] Create/delete routines (activity preset · days · departure); guest-first, nothing blocked on auth
- [x] Week strip: scheduled days show their routine, the rest show rest (same observed inputs every day, stated; per-day forecasts need 13)
- [x] Decision-stack card ("Play HH–HH — best window today") appears when a routine covers today
- [x] Inbox: ledger entries newest-first; fully usable when notifications are denied or unavailable
- [x] No permission prompt at onboarding; push permission is ticket 18 (host-gated)
- [x] EN + HI via ticket-12 templates; new screens covered by the a11y pass

## Comments

- 2026-10-03: Created (v1.1, Q10/Q26).
- 2026-10-03: Landed slice (evidence `ticket-19-home-feedback.png`, `ticket-19-planner-routines.png`). Routine places + per-day detail tap + contextual push prompt ride with 13/18.
- 2026-10-03: Planner UX pass — routine entry friction cut: days are tapped
  chips (no free-text "Mon,Sat" to typo), leave time defaults to the
  best-window start minus a 30-minute buffer, and both activity selectors
  remember the last activity and accept custom activities (or open the
  builder). Custom activities are on-device only, like routines.
