# ADR-0001 — Firebase for authentication and account data

- **Status:** Accepted
- **Date:** 2026-10-03
- **Context:** SIH26076 "Mausam personalised homepage" (`Mausam/`)
- **Deciders:** Team (product + engineering)
- **Related:** `Mausam/APP.md` §3.3, §4; `Mausam/PRD-SIH26076-Mausam.md` §11
- **Supersedes:** an earlier draft that chose Supabase (never landed).

## Context

The product is an offline-first PWA (vanilla JS, no bundler) with a Python FastAPI
backend. We needed accounts for exactly two things — **syncing saved places** and
**collecting feedback** — while keeping the home screen fully usable **signed-out**
(PRD §11: "auth only for saved places", personalisation on-device, no behavioural
tracking).

Constraints that shaped the decision:

1. The client has **no bundler**, so the auth SDK must work from a CDN `<script>`
   (or a native ES-module import from a CDN).
2. The backend is **Python**, so server-side token verification must have a
   first-class SDK.
3. Per-user data must be **secure by default**, enforced in the store rather than
   re-checked in every handler.
4. The product is **offline-first**; the account/session layer must survive no
   network, and ideally the store offers offline persistence.
5. The prototype runs on a **free tier**; a pilot needs a clear upgrade path.
6. Secrets discipline is strict: the IMD API key and any privileged key live on the
   backend only (`Mausam/APP.md` §2). The auth provider must expose a **public,
   safely-embeddable** client config.

## Decision

Use **Firebase** — Authentication + Cloud Firestore + Security Rules — as the
identity and account-data plane.

- **Sign-in:** passwordless **email link** (primary, no password) and **Google
  OAuth** (secondary).
- **Client:** the Firebase **modular JS SDK** from the gstatic CDN, using the
  **public Firebase web config** (the `apiKey` is designed to be embedded; access is
  constrained by Security Rules).
- **Backend:** the Python **`firebase-admin` SDK** verifies the ID token
  (`auth.verify_id_token`) on user-scoped routes; the **service-account key** lives
  only in the backend secret store.
- **Data:** Firestore with **Security Rules on every path**, each scoped to the
  authenticated `uid` (`request.auth.uid`).
- **Guest-first:** onboarding and the home work without an account; auth gates only
  sync and write, never reading weather.

Config is versioned as code under `Mausam/firebase/` (`FILEMAP.md` §2):
`firebase.json`, `firestore.rules`, `firestore.indexes.json`.

### Why Firebase over the alternatives, for *this* product

- **One vendor for identity and push.** The build plan already uses **FCM** for
  warning notifications (`APP.md` §3.5); consolidating auth on Firebase means one
  console, one project, one billing surface.
- **Offline-first alignment.** Firebase Auth persists sessions locally and Firestore
  offers client-side offline persistence, which matches the "render with no network"
  invariant better than a network-only SQL/RLS path.
- **No-bundler friendly.** The modular SDK is importable straight from the CDN.
- **Python story.** `firebase-admin` is mature and the canonical way to verify ID
  tokens from FastAPI.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| **Supabase** | Strong option (Postgres + SQL RLS) and a live "public anon key" model; rejected on team preference for Firebase's unified auth + FCM story and its built-in offline persistence for an offline-first PWA. |
| **Clerk** | Excellent DX, but auth-only (we also need a per-user store) and a component UI that fights a hand-built vanilla surface. |
| **Auth0 / Okta** | Mature, but heavier setup, pricier at small scale, and no bundled per-user database. |
| **Better Auth** | Great for a bundler/Node app; assumes a JS server runtime and a `package.json` build we deliberately avoid. |
| **Roll our own (password hashing + sessions)** | Rejected outright: hand-rolled auth is a security liability and a distraction from the moat (the advisory engine). |

## Consequences

**Positive**
- One service for auth, account store, and push; no bespoke session code.
- Security Rules mean ownership is enforced by the store, so a client bug cannot
  leak another user's rows.
- Offline session persistence and Firestore cache align with the offline-first rule.

**Negative / costs**
- Firestore is **NoSQL**: queries are denormalised and composite indexes are declared
  in `firestore.indexes.json`; no SQL joins.
- Security lives in the **Rules language**, a second thing to review besides backend
  endpoints; rules must be tested (emulator suite).
- A second hosted dependency beside the static-IP backend host; pick the Firestore
  **location** closest to that host (follow-up).
- The `apiKey` in the web config is public: all protection must live in rules.

**Neutral**
- Adds one CDN import to the client.

## Compliance with existing decisions

This **extends** PRD Q3/§11 rather than contradicting it: personalisation stays
on-device; an account only enables cross-device sync of explicitly saved places and
opted-in feedback, both deletable. No behavioural tracking is introduced.

## Follow-ups

1. Create the Firebase project and choose the Firestore location (`Mausam/ROADMAP.md` R4).
2. Land `firestore.rules` (+ indexes) and test them with the emulator.
3. Decide OAuth providers: Google only, or Google + Apple (`Mausam/APP.md` §14).
4. Add account **deletion** (user-initiated) before any pilot.
5. Confirm FCM sender setup alongside Auth (shared project).
