"use strict";
// Mirrors app/engine/deriveCard.js. Run: node --test tests/
const { test } = require("node:test");
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const E = require("../app/engine/deriveCard.js");

const read = (f) => JSON.parse(fs.readFileSync(path.join(__dirname, "..", "app", "fixtures", f), "utf8"));
const LOCATION = { name: "New Delhi", lat: 28.6139, lon: 77.209 };
const fixture = read("imd-synop-delhi-2026-10-02.json");
const capture = read("imd-synop-delhi-2026-10-02.capture.json");
const inputs = { features: fixture.features, capture, adapters: { aqi: null }, personaKey: "commuter", location: LOCATION };

test("hero is severity-first on the frozen fixture", () => {
  const station = E.nearestStation(fixture.features, LOCATION);
  const ranked = E.rankStack(
    [...E.deriveCards(station, capture.captured_at_utc, capture), ...E.deriveGaps(inputs.adapters)], "commuter");
  assert.strictEqual(ranked[0].id, "vis");
  assert.ok(ranked[0].triggers.length > 0, "hero carries triggering inputs");
});

test("replay is byte-identical", () => {
  assert.strictEqual(E.replayStack(inputs), E.replayStack(JSON.parse(JSON.stringify(inputs))));
});

test("persona re-rank is deterministic", () => {
  for (const p of E.PERSONA_KEYS) {
    const a = E.replayStack({ ...inputs, personaKey: p });
    assert.strictEqual(a, E.replayStack({ ...inputs, personaKey: p }));
  }
});

test("gaps carry no numbers", () => {
  for (const g of E.deriveGaps({ aqi: null })) assert.ok(!g.facts || g.facts.length === 0);
});
