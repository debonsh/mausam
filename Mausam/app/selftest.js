"use strict";
// Runnable checks for the advisory + window engines, on real captures.
// Run: node app/selftest.js
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const E = require("./engine/deriveCard.js");
const W = require("./engine/windows.js");

const read = (f) => JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures", f), "utf8"));
const LOCATION = { name: "New Delhi", lat: 28.6139, lon: 77.209 };

// --- Ticket 01 contract (frozen fixture) ---
const fixture = read("imd-synop-delhi-2026-10-02.json");
const capture = read("imd-synop-delhi-2026-10-02.capture.json");
const station = E.nearestStation(fixture.features, LOCATION);
assert.strictEqual(station.p.station, "New Delhi-Safdarjung", "nearest station changed");
const card = E.deriveCard(station, capture.captured_at_utc, capture);
assert.strictEqual(card.sev, "medium");
assert.strictEqual(card.category, "Reduced visibility");
assert.match(card.action, /allow extra time/i);
assert.deepStrictEqual(card.facts[0], { label: "Visibility", value: "2", unit: "km" });
assert.strictEqual(card.endpoint, capture.endpoint);

// --- Ticket 02: stack, hero rule, replay identity ---
const inputs = { features: fixture.features, capture, adapters: { aqi: null },
  personaKey: "commuter", location: LOCATION };
const stack = E.rankStack(
  [...E.deriveCards(station, capture.captured_at_utc, capture), ...E.deriveGaps(inputs.adapters)],
  "commuter");
assert.strictEqual(stack[0].id, "vis", "hero must be the visibility card");
assert.ok(stack[0].triggers.includes("visibility"), "hero carries triggering inputs");
assert.strictEqual(E.replayStack(inputs), E.replayStack(JSON.parse(JSON.stringify(inputs))),
  "replay must be byte-identical");
// Persona re-rank is deterministic and can change the hero's company.
const byHealth = E.rankStack(stack, "health");
const byAgri = E.rankStack(stack, "agriculture");
assert.strictEqual(E.replayStack({ ...inputs, personaKey: "health" }),
  E.replayStack({ ...inputs, personaKey: "health" }));
assert.ok(byHealth.length === byAgri.length && byHealth.length > 0);
// Gaps carry no numbers.
for (const g of E.deriveGaps({ aqi: null })) {
  assert.ok(!("facts" in g) || g.facts.length === 0, "gap must carry no values");
}

// --- Ticket 16: window engine determinism on real captures ---
const pf = read("imd-synop-delhi-2026-10-03.json");
const pc = read("imd-synop-delhi-2026-10-03.capture.json");
const uv = read("cams-uv-delhi-2026-10-03.json");
const solar = read("solar-delhi-2026-10-03.json");
const pst = E.nearestStation(pf.features, LOCATION);
const at = (h) => uv.hourly.uv_index[uv.hourly.time.indexOf(`2026-10-03T${h}:00`)];
const winInputs = {
  obs: { tempC: pst.p.dbtemp, rh: pst.p.rh, windMS: pst.p.windsp,
    rainMm: pst.p["24hrlyrain"] || 0, sigwx: pst.p.sigwx,
    station: `IMD SYNOP · ${pst.p.station}`, issuedUtc: pst.p.update_time,
    capturedAt: pc.captured_at_utc, endpoint: pc.endpoint, layer: pc.request.typename },
  uvBlocks: [
    { id: "b06", startIST: "06:00", endIST: "09:00", uv: (at("06") + at("07") + at("08")) / 3, uvSrc: "CAMS" },
    { id: "b09", startIST: "09:00", endIST: "12:00", uv: (at("09") + at("10") + at("11")) / 3, uvSrc: "CAMS" },
    { id: "b12", startIST: "12:00", endIST: "15:00", uv: (at("12") + at("13") + at("14")) / 3, uvSrc: "CAMS" },
    { id: "b15", startIST: "15:00", endIST: "18:00", uv: (at("15") + at("16") + at("17")) / 3, uvSrc: "CAMS" },
  ],
  solar: { sunriseIST: solar.sunriseIST, sunsetIST: solar.sunsetIST },
  activity: "volleyball", routine: { days: ["Sat"] }, adapters: { aqi: null },
};
const wres = W.deriveWindows(winInputs);
assert.strictEqual(wres.state, "ready");
assert.ok(wres.bestId, "a best window is chosen");
assert.deepStrictEqual(wres.excluded, ["aqi", "pollen"]);
assert.strictEqual(W.replayWindows(winInputs),
  W.replayWindows(JSON.parse(JSON.stringify(winInputs))), "window replay byte-identical");
const rest = W.deriveWindows({ ...winInputs, routine: null });
assert.strictEqual(rest.state, "rest", "no routine renders the rest-day state");

// --- Finale slices: deep cards silent on the frozen fixtures, gaps honest ---
const frozenIds = stack.map((c) => c.id);
for (const id of ["storm", "frost", "cold"]) {
  assert.ok(!frozenIds.includes(id), `${id} stays silent on the Delhi-October fixture`);
}
const gapIds = E.deriveGaps({ aqi: null }).map((g) => g.id);
for (const id of ["gap-pollen", "gap-aqi", "gap-traffic", "gap-soil"]) {
  assert.ok(gapIds.includes(id), `${id} renders honestly with no source`);
}
// --- Ticket 17: presets pinned + deterministic ---
for (const a of ["volleyball", "run", "walk", "office"]) {
  assert.strictEqual(W.ACTIVITY_PRESETS[a].version, "windows-v1");
  const r1 = W.deriveWindows({ ...winInputs, activity: a });
  const r2 = W.deriveWindows(JSON.parse(JSON.stringify({ ...winInputs, activity: a })));
  assert.strictEqual(W.canonicalizeWindows(r1), W.canonicalizeWindows(r2), `${a} deterministic`);
}

// --- Planner UX pass: custom activities, pinned + deterministic ---
const custom = { name: "cricket", version: "windows-v1", weights: { heat: 1, humidity: 1 } };
const cInputs = { ...winInputs, activity: "cricket", custom };
assert.deepStrictEqual(W.deriveWindows(cInputs).weights, custom.weights);
assert.strictEqual(W.replayWindows(cInputs),
  W.replayWindows(JSON.parse(JSON.stringify(cInputs))), "custom replay byte-identical");
assert.throws(() => W.deriveWindows({ ...winInputs, activity: "cricket",
  custom: { name: "cricket", version: "windows-v1", weights: { rain: 1 } } }),
  "unknown metric never ships");

console.log("selftest ok — hero:", stack[0].category + ":", stack[0].action,
  "| best window:", wres.bestId, wres.blocks.find((b) => b.id === wres.bestId).score + "/100",
  "| custom: cricket");
