# 18: Routine alerts — scheduler, ledger, Web Push

**What to build:** Scheduled routine alerts that fire with the app closed — a backend scheduler on the static-IP host, Web Push (VAPID) delivery to the installed PWA, and an append-only notification ledger that makes every alert replayable.

**Blocked by:** 13 (backend host + gateway), 17 (window engine)

**Status:** ready-for-human

- [ ] Scheduler runs server-side on the static-IP host; VAPID keys live in the backend secret store only; the service worker gains `push` + `notificationclick` handlers
- [ ] Alert types (Q26): evening "tomorrow plan" digest (default 21:00) · departure alert (default T−30 min, per-routine overridable) · IMD orange/red override fires immediately
- [ ] Quiet hours (default 21:30–06:30) apply to the two scheduled types only — IMD orange/red overrides them; daily cap 3 (override excluded); per-routine toggle
- [ ] Override triggers are IMD warnings only — adapter values (CPCB/CAMS) can never raise an alert (ADR-0002)
- [ ] Permission is requested at first routine creation, never at onboarding; denial leaves the in-app inbox fully working
- [ ] Every alert is written to an append-only ledger (payload · triggering inputs · config version · timestamp) and is replayable byte-identically (FR-19)
- [ ] Notification copy is template-first, human-reviewed EN + Hi (ticket 12); payload carries source · issue · age
- [ ] Demo: Android Chrome PWA receives a real push with the app closed; iOS caveat documented (install required — verify at finale)
- [ ] The minimal delivery config (routine schedule + place) is registered with the backend for delivery only — not an account row, not Firestore-synced, deleted with the routine/opt-out (ADR-0003)

## Notes

- Delivery semantics fixed in Q26; transport rationale in `docs/adr/0003-routine-alert-transport.md`.
- Ledger is the same audit posture as the advisory replay log — status is deduped per routine + slot so a retry can't double-send.

## Comments

- 2026-10-03: Created (v1.1, Q26; ADR-0003).
- 2026-10-03: Docs-only pass — host-gated via 13 (needs static-IP host + human-owned VAPID pair + Android-Chrome demo device). No code touched.
