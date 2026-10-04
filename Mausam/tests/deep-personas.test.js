"use strict";
// Tickets 08–10: deep-persona rules fire only on IMD fields we hold;
// absent sources degrade to honest gaps, never fabricated values.
const { test } = require("node:test");
const assert = require("assert");
const E = require("../app/engine/deriveCard.js");

const STORM_SIGWX = [17, 19, 27, 29, 91, 92, 93, 94, 95, 96, 97, 98, 99];
const stationWith = (over) => ({ p: { station: "Test", update_time: "2026-10-03T00:00:00Z",
  dbtemp: 27, rh: 60, visibility: 8000, "24hrlyrain": 0, windsp: 2, sigwx: 5, ...over } });
const CAP = { endpoint: "e", request: { typename: "l" } };

test("08: thunderstorm sigwx raises a storm card, calm codes do not", () => {
  const storm = E.deriveCards(stationWith({ sigwx: 95 }), "2026-10-03T01:00:00Z", CAP);
  const card = storm.find((c) => c.id === "storm");
  assert.ok(card, "storm card fires on sigwx 95");
  assert.strictEqual(card.sev, "high");
  assert.ok(card.triggers.includes("sigwx"), "card carries its trigger");
  const calm = E.deriveCards(stationWith({ sigwx: 5 }), "2026-10-03T01:00:00Z", CAP);
  assert.ok(!calm.some((c) => c.id === "storm"), "no warning we do not hold");
});

test("08: traffic with no labelled source is a gap, never a number", () => {
  const gaps = E.deriveGaps({ aqi: null });
  const t = gaps.find((g) => g.id === "gap-traffic");
  assert.ok(t, "traffic gap present without a labelled adapter");
  assert.ok(!t.facts || t.facts.length === 0);
  const labelled = E.deriveGaps({ aqi: null, traffic: "labelled" });
  assert.ok(!labelled.some((g) => g.id === "gap-traffic"));
});

test("09: ground frost fires at freezing obs, warm obs stay silent", () => {
  const frost = E.deriveCards(stationWith({ dbtemp: 1, rh: 90 }), "2026-10-03T01:00:00Z", CAP);
  assert.ok(frost.some((c) => c.id === "frost"), "frost card at 1°C");
  const warm = E.deriveCards(stationWith({ dbtemp: 27 }), "2026-10-03T01:00:00Z", CAP);
  assert.ok(!warm.some((c) => c.id === "frost"));
});

test("09: soil moisture without a source is a gap", () => {
  assert.ok(E.deriveGaps({ aqi: null }).some((g) => g.id === "gap-soil"));
  assert.ok(!E.deriveGaps({ aqi: null, soil: "labelled" }).some((g) => g.id === "gap-soil"));
});

test("10: cold obs raises a cold card, Delhi-October obs does not", () => {
  const cold = E.deriveCards(stationWith({ dbtemp: 4, rh: 80 }), "2026-10-03T01:00:00Z", CAP);
  assert.ok(cold.some((c) => c.id === "cold"), "cold card at 4°C");
  const warm = E.deriveCards(stationWith({ dbtemp: 27 }), "2026-10-03T01:00:00Z", CAP);
  assert.ok(!warm.some((c) => c.id === "cold"));
});

test("deep cards are weighted per persona and replay-stable", () => {
  for (const id of ["storm", "frost", "cold"]) {
    assert.ok(E.PERSONA_WEIGHTS[id], `${id} has persona weights`);
  }
  const inputs = (key) => ({ features: [{ geometry: { coordinates: [77.2, 28.6] },
    properties: stationWith({ sigwx: 95 }).p }], capture: { captured_at_utc: "2026-10-03T01:00:00Z", ...CAP },
    adapters: { aqi: null }, personaKey: key, location: { lat: 28.6, lon: 77.2 } });
  assert.strictEqual(E.replayStack(inputs("commuter")), E.replayStack(inputs("commuter")));
});
