// Ticket 11 origin: the shell must render with the network disabled.
// Cache-first for same-origin GET (first render never waits on 2G), with a
// background refresh so a deploy is picked up on the next load.
const CACHE = "mausam-home-v7";
const ASSETS = [
  "./",
  "index.html",
  "styles/tokens.css",
  "styles/components.css",
  "app.js",
  "core.js",
  "icons.js",
  "i18n.js",
  "personal.js",
  "views/onboarding.js",
  "views/home.js",
  "views/provenance.js",
  "views/settings.js",
  "views/planner.js",
  "engine/deriveCard.js",
  "engine/windows.js",
  "manifest.webmanifest",
  "icon.svg",
  "icon-maskable.svg",
  "fixtures/imd-synop-delhi-2026-10-02.json",
  "fixtures/imd-synop-delhi-2026-10-02.capture.json",
  "fixtures/imd-synop-delhi-2026-10-03.json",
  "fixtures/imd-synop-delhi-2026-10-03.capture.json",
  "fixtures/cams-uv-delhi-2026-10-03.json",
  "fixtures/cams-uv-delhi-2026-10-03.capture.json",
  "fixtures/solar-delhi-2026-10-03.json",
  "fixtures/aqi-delhi-2026-10-03.unavailable.json",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request).then((hit) => {
      const network = fetch(e.request)
        .then((res) => {
          if (res.ok && new URL(e.request.url).origin === self.location.origin) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(e.request, copy)).catch(() => {});
          }
          return res;
        })
        .catch(() => hit || caches.match("index.html"));
      // Cache-first: a cached bundle renders instantly on 2G; the network
      // only refreshes the cache in the background. Uncached requests wait.
      return hit || network;
    })
  );
});
