"use strict";
// Ticket 11: offline contract — cache-first same-origin GET, precached
// personal bundle, Offline pill + freshness strip in the shell.
const { test } = require("node:test");
const assert = require("assert");
const fs = require("fs");
const path = require("path");

const sw = fs.readFileSync(path.join(__dirname, "..", "app", "sw.js"), "utf8");
const home = fs.readFileSync(path.join(__dirname, "..", "app", "views", "home.js"), "utf8");

test("service worker is cache-first (match before network)", () => {
  assert.match(sw, /mausam-home-v\d+/);
  assert.ok(!sw.includes("mausam-home-v4"), "cache version bumped past v4");
  assert.ok(sw.indexOf("caches.match(e.request)") < sw.indexOf("fetch(e.request)"),
    "cache lookup precedes the network");
});

test("personal bundle is precached", () => {
  for (const f of ["fixtures/imd-synop-delhi-2026-10-02.json",
    "fixtures/imd-synop-delhi-2026-10-03.json", "engine/deriveCard.js"]) {
    assert.ok(sw.includes(f), `${f} precached`);
  }
});

test("shell carries the offline pill + freshness strip", () => {
  assert.ok(home.includes('id="offline-badge"'), "offline pill present");
  assert.ok(home.includes('id="freshness-text"'), "freshness strip present");
});
