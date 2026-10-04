"use strict";
// Mirrors app/engine/windows.js on real captures. Run: node --test tests/
const { test } = require("node:test");
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const E = require("../app/engine/deriveCard.js");
const W = require("../app/engine/windows.js");

const read = (f) => JSON.parse(fs.readFileSync(path.join(__dirname, "..", "app", "fixtures", f), "utf8"));
const LOCATION = { name: "New Delhi", lat: 28.6139, lon: 77.209 };

function plannerInputs() {
  const pf = read("imd-synop-delhi-2026-10-03.json");
  const pc = read("imd-synop-delhi-2026-10-03.capture.json");
  const uv = read("cams-uv-delhi-2026-10-03.json");
  const solar = read("solar-delhi-2026-10-03.json");
  const st = E.nearestStation(pf.features, LOCATION);
  const at = (h) => uv.hourly.uv_index[uv.hourly.time.indexOf(`2026-10-03T${h}:00`)];
  const mean = (hs) => Math.round((hs.reduce((s, h) => s + at(h), 0) / hs.length) * 10) / 10;
  return {
    obs: { tempC: st.p.dbtemp, rh: st.p.rh, windMS: st.p.windsp, rainMm: st.p["24hrlyrain"] || 0,
      sigwx: st.p.sigwx, station: `IMD SYNOP · ${st.p.station}`, issuedUtc: st.p.update_time,
      capturedAt: pc.captured_at_utc, endpoint: pc.endpoint, layer: pc.request.typename },
    uvBlocks: [
      { id: "b06", startIST: "06:00", endIST: "09:00", uv: mean(["06", "07", "08"]), uvSrc: "CAMS" },
      { id: "b09", startIST: "09:00", endIST: "12:00", uv: mean(["09", "10", "11"]), uvSrc: "CAMS" },
      { id: "b12", startIST: "12:00", endIST: "15:00", uv: mean(["12", "13", "14"]), uvSrc: "CAMS" },
      { id: "b15", startIST: "15:00", endIST: "18:00", uv: mean(["15", "16", "17"]), uvSrc: "CAMS" },
    ],
    solar: { sunriseIST: solar.sunriseIST, sunsetIST: solar.sunsetIST },
    activity: "volleyball", routine: { days: ["Sat"] }, adapters: { aqi: null },
  };
}

test("best window is deterministic on real captures", () => {
  const w = W.deriveWindows(plannerInputs());
  assert.strictEqual(w.state, "ready");
  assert.strictEqual(w.bestId, "b06");
  assert.deepStrictEqual(w.excluded, ["aqi", "pollen"]);
});

test("window replay is byte-identical", () => {
  const i = plannerInputs();
  assert.strictEqual(W.replayWindows(i), W.replayWindows(JSON.parse(JSON.stringify(i))));
});

test("no routine renders the rest-day state", () => {
  assert.strictEqual(W.deriveWindows({ ...plannerInputs(), routine: null }).state, "rest");
});

test("17: activity presets exist with a pinned config version", () => {
  for (const a of ["volleyball", "run", "walk", "office"]) {
    assert.ok(W.ACTIVITY_PRESETS[a], `${a} preset exists`);
    assert.strictEqual(W.ACTIVITY_PRESETS[a].version, "windows-v1");
  }
});

test("17: preset windows are deterministic and replay-identical", () => {
  const run = W.deriveWindows({ ...plannerInputs(), activity: "run" });
  assert.strictEqual(run.activity, "run");
  assert.strictEqual(W.replayWindows({ ...plannerInputs(), activity: "run" }),
    W.canonicalizeWindows(run));
  const unknown = W.deriveWindows({ ...plannerInputs(), activity: "surf" });
  assert.strictEqual(unknown.activity, "surf");
  assert.ok(unknown.bestId, "unknown activity falls back to default weights");
});

test("custom activity: supplied weights are used, disclosed, replay-identical", () => {
  const custom = { name: "cricket", version: "windows-v1", weights: { heat: 1, humidity: 1 } };
  const i = { ...plannerInputs(), activity: "cricket", custom };
  const w = W.deriveWindows(i);
  assert.strictEqual(w.activity, "cricket");
  assert.deepStrictEqual(w.weights, custom.weights, "result discloses the weights used");
  const best = w.blocks.find((b) => b.id === w.bestId);
  const obs = plannerInputs().obs;
  const hi = W.heatIndexC(obs.tempC, obs.rh);
  const expect = Math.round((W.heatScore(hi) + W.humidityScore(obs.rh)) / 2);
  assert.strictEqual(best.score, expect, "score renormalises over custom weights only");
  assert.strictEqual(W.replayWindows(i), W.canonicalizeWindows(w));
});

test("custom activity: a preset always wins over a same-name custom config", () => {
  const custom = { name: "volleyball", version: "windows-v1", weights: { heat: 1 } };
  const w = W.deriveWindows({ ...plannerInputs(), custom });
  assert.deepStrictEqual(w.weights, W.ACTIVITY_PRESETS.volleyball.weights);
});

test("custom activity: malformed configs never ship", () => {
  const base = () => ({ ...plannerInputs(), activity: "cricket" });
  const bad = [
    { name: "cricket", weights: { heat: 1 } },                          // no version
    { version: "windows-v1", weights: { rain: 1 } },                    // unknown metric
    { version: "windows-v1", weights: { heat: -1 } },                   // negative
    { version: "windows-v1", weights: { heat: 0 } },                    // zero sum
    { version: "windows-v1", weights: {} },                             // empty
    { version: "windows-v1", weights: "x" },                            // not an object
    { name: "volleyball", version: "windows-v1", weights: { heat: 1 } }, // preset name
  ];
  for (const custom of bad) assert.throws(() => W.deriveWindows({ ...base(), custom }));
  assert.throws(() => W.deriveWindows({
    ...base(), custom: { name: "surf", version: "windows-v1", weights: { heat: 1 } },
  }), "custom config must name the activity being derived");
});
