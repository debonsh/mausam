# ADR-0003 — Routine-alert transport: Web Push (VAPID) + backend scheduler + notification ledger

- **Status:** Accepted
- **Date:** 2026-10-03
- **Context:** SIH26076 "Mausam personalised homepage" (`Mausam/`)
- **Deciders:** Team (product + engineering)
- **Related:** `Mausam/PRD-SIH26076-Mausam.md` Q25/Q26, FR-19; `Mausam/APP.md` §3.5, §9; tickets 18, 19; ADR-0001

## Context

The activity planner ships with **routine alerts** (Q21/Q26): an evening "tomorrow plan" digest, a departure alert relative to a routine's time, and an immediate override for IMD orange/red warnings. Alerts must fire **while the app is closed**, which rules out client-side timers.

Constraints that shaped the decision:

1. **Offline-first PWA, no bundler.** The delivery mechanism must work with the existing service-worker architecture and mobile browsers, with no app-store shell.
2. **A static-IP backend exists anyway** (ticket 13) to hold the IMD key and refresh the hourly JWT. Scheduling can live there at near-zero marginal cost.
3. **Guest-first, no behavioural tracking** (PRD §11, FR-16). Alerts must work signed-out, and must not create a behavioural history.
4. **Auditability is the product's moat** (FR-10). Alerts should be as replayable as advisories.
5. **Honesty rules** (ADR-0002): safety-critical triggers are IMD-only; quiet hours and caps are required to avoid notification fatigue.
6. `APP.md` §3.5 named **FCM** as the future production push transport; ADR-0001 cited FCM as a reason to prefer Firebase. Neither locks the web push mechanism — FCM can deliver web push, but the standard protocol under it is what matters here.

## Decision

**Web Push (VAPID) from the static-IP backend, with a server-side scheduler and an append-only notification ledger.**

- **Scheduler:** server-side, colocated with the gateway; evaluates each active routine against the window engine (ticket 17) and fires: evening plan (default 21:00) · departure alert (default T−30 min per routine) · IMD orange/red override (immediate, bypasses quiet hours).
- **Transport:** W3C Web Push with **VAPID** keys held in the backend secret store; the service worker gains `push` + `notificationclick` handlers (`Mausam/app/sw.js`). No Firebase SDK is added to the client for this.
- **Delivery config:** the minimal routine schedule + place is registered with the backend **for delivery only** — it is not an account row, is never sync'd through Firestore, and is deleted with the routine or an opt-out. No behavioural history is stored.
- **Ledger:** every sent alert is appended (payload · triggering inputs · config version · timestamp) and is replayable byte-identically; the in-app inbox reads the same ledger. Dedupe key = routine + slot, so retries cannot double-send.
- **Permission:** requested at first routine creation (teach → ask → fallback), never at onboarding; denial degrades to the in-app inbox, which always carries everything.
- **Copy:** template-first, human-reviewed EN + Hi (ticket 12); payload carries source · issue · age.
- **FCM:** remains the option for a future native shell only; not used for the PWA.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| **In-app inbox only (no OS notifications)** | No value when the app is closed — the entire premise of "leave at 7am, it rains at 7". The inbox stays as the fallback, not the transport. |
| **FCM web push via the Firebase JS SDK** | Adds the Firebase CDN SDK + token lifecycle to the client for no delivery benefit over VAPID; complicates the controller. Revisit only if VAPID operations hurt at pilot scale. |
| **Client-side scheduled notifications (Notification Triggers / periodic sync)** | Not standard, not reliable when the app is closed, and unavailable across target browsers. |
| **SMS / WhatsApp / email alerts** | Out of scope channels; collection of phone numbers/emails contradicts the minimal-data posture. |

## Consequences

**Positive**

- Real background notifications with zero third-party push dependency; one fewer SDK in the client.
- Alerts inherit the audit story: every alert is reconstructible from logged inputs, matching FR-10's posture.
- The same backend that must exist for the IMD key does the scheduling — no new infrastructure.

**Negative / costs**

- VAPID key management + subscription cleanup (stale endpoints) are now our problem; a cleanup job is required.
- iOS requires the PWA to be installed for web push; the demo runs on Android Chrome, with the caveat documented.
- The backend necessarily sees the routine schedule + place to deliver alerts — precisely scoped, deleted on opt-out, but it must be stated in the privacy copy.

**Neutral**

- Notification permission becomes a first-class product moment (teach → ask → fallback) rather than a hidden prompt.

## Compliance with existing decisions

Extends Q20/ADR-0001 (accounts) without amending them: alerts work signed-out; Firestore is untouched. Keeps FR-16 (guest-first, no behavioural tracking) and FR-14 (template-first, human-reviewed warning copy).

## Follow-ups

1. Generate VAPID keypair; store in the backend secret store; document rotation.
2. Ticket 18 implements the scheduler, ledger, and service-worker handlers; verify a real push on Android Chrome with the app closed.
3. Add subscription cleanup and per-routine/unsubscribe deletion paths.
4. Privacy copy: state exactly what the backend stores for delivery (schedule + place + push subscription), and that it is deleted on opt-out.
