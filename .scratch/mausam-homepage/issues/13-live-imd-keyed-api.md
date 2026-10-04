# 13: Live IMD keyed API integration

**What to build:** The backend gateway that calls IMD's keyed APIs for real — a static-IP host holding the API key, refreshing the hourly JWT, tracking per-endpoint staleness, and recording an attribution ledger.

**Blocked by:** 02 (advisory engine v0). Also gated externally by provisioning the static-IP host.

**Status:** ready-for-human

- [ ] A backend on a static public IP holds the IMD key and refreshes the hourly JWT
- [ ] Authenticated calls succeed against the keyed API
- [ ] Staleness is tracked per endpoint
- [ ] An attribution ledger records usage (shareable with IMD on request)

## Comments
- 2026-10-03: Mock runs on public WFS (proven reachable, real captures 02+03 Oct). Static-IP host still the critical path; provision first in the finale.
- 2026-10-03: Docs-only pass — host-gated, needs a human to register on `api.imd.gov.in` and stand up the static-IP host. No code touched.
