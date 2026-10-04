"use strict";

// Ticket 16/17 — window engine (static-slice config `windows-v1`).
// Framework-free: runs in Node and in the browser as a classic script.
// Same determinism contract as deriveCard.js: inputs only, no clock.
// Safety: gates are IMD-only (ADR-0002). Adapter values shape comfort only.

const WINDOWS_V1 = {
  version: "windows-v1",
  grain: "3-hour blocks",
  weights: { heat: 0.35, humidity: 0.20, wind: 0.20, aqi: 0.15, uv: 0.10 },
  gates: {
    rainMm: 0,          // any observed rain gates the block (IMD SYNOP)
    heatIndexC: 45,     // heat extreme (IMD obs-derived)
    uvIndex: 11,        // UV extreme (labelled adapter)
    thunderstorm: [17, 19, 27, 29, 91, 92, 93, 94, 95, 96, 97, 98, 99],
  },
};

// Ticket 17 — activity presets inside personas. Same gates and grain;
// only the comfort weights shift per activity. Version pinned: a preset
// without a version never ships (tests assert it).
const ACTIVITY_PRESETS = {
  volleyball: { version: "windows-v1", weights: { ...WINDOWS_V1.weights } },
  run:        { version: "windows-v1", weights: { heat: 0.40, humidity: 0.20, wind: 0.10, aqi: 0.15, uv: 0.15 } },
  walk:       { version: "windows-v1", weights: { heat: 0.30, humidity: 0.15, wind: 0.10, aqi: 0.20, uv: 0.25 } },
  office:     { version: "windows-v1", weights: { heat: 0.25, humidity: 0.15, wind: 0.10, aqi: 0.30, uv: 0.20 } },
};

// Custom activities (planner UX pass): any name + the subset of
// weighted metrics that matter, carried at the same pinned
// version as the scoring model. Rain and storms are hard gates
// and are never weighted, so they are not offered here.
const METRIC_KEYS = ["heat", "humidity", "wind", "aqi", "uv"];

function checkCustomActivity({ name, version, weights }) {
  if (!name || !String(name).trim()) throw new Error("custom activity needs a name");
  if (ACTIVITY_PRESETS[name]) throw new Error(`activity is a built-in preset: ${name}`);
  if (!version || !String(version).trim()) throw new Error("custom activity needs a pinned version");
  if (!weights || typeof weights !== "object") throw new Error("custom activity needs weights");
  const keys = Object.keys(weights);
  if (keys.length === 0) throw new Error("custom activity needs at least one metric");
  for (const [k, v] of Object.entries(weights)) {
    if (!METRIC_KEYS.includes(k)) throw new Error(`unknown metric: ${k}`);
    if (typeof v !== "number" || !Number.isFinite(v) || v < 0) {
      throw new Error(`metric ${k} needs a finite weight >= 0`);
    }
  }
  if (keys.every((k) => weights[k] === 0)) throw new Error("custom activity weights sum to zero");
}

// Rothfusz regression, °C in/out. Deterministic; formula stated in provenance.
function heatIndexC(tC, rh) {
  const tF = (tC * 9) / 5 + 32;
  const R = rh;
  let hiF = -42.379 + 2.04901523 * tF + 10.14333127 * R
    - 0.22475541 * tF * R - 0.00683783 * tF * tF - 0.05481717 * R * R
    + 0.00122874 * tF * tF * R + 0.00085282 * tF * R * R
    - 0.00000199 * tF * tF * R * R;
  if (R < 13 && tF >= 80 && tF <= 112) {
    hiF -= ((13 - R) / 4) * Math.sqrt((17 - Math.abs(tF - 95)) / 17);
  } else if (R > 85 && tF >= 80 && tF <= 87) {
    hiF += ((R - 85) / 10) * ((87 - tF) / 5);
  }
  return Math.round((((hiF - 32) * 5) / 9) * 10) / 10;
}

function bandScore(v, bands) {
  for (const [max, s] of bands) if (v <= max) return s;
  return bands[bands.length - 1][1];
}

function humidityScore(rh) {
  return Math.max(0, Math.round(100 - 1.5 * Math.abs(rh - 50)));
}

function windScoreVolleyball(ms) {
  return bandScore(ms, [[3, 100], [6, 70], [9, 40], [Infinity, 15]]);
}

function uvScore(uv) {
  return bandScore(uv, [[2, 100], [5, 75], [7, 50], [10, 25], [Infinity, 0]]);
}

function heatScore(hiC) {
  return bandScore(hiC, [[27, 100], [32, 80], [38, 55], [45, 25], [Infinity, 0]]);
}

// inputs: {
//   obs: { tempC, rh, windMS, rainMm, sigwx, station, issuedUtc, capturedAt,
//          endpoint, layer },
//   uvBlocks: [{ id, startIST, endIST, uv }],   // labelled adapter, real forecast
//   solar: { sunriseIST, sunsetIST, note },     // computed, labelled non-IMD
//   activity: 'volleyball', routine: { days } | null,
//   adapters: { aqi: null | {...} }             // null → excluded + disclosed
// }
function deriveWindows(inputs) {
  const cfg = WINDOWS_V1;
  // Resolution: a preset wins; otherwise a validated custom config;
  // otherwise the default weights. Unknown activities never score zero.
  const preset = ACTIVITY_PRESETS[inputs.activity];
  const custom = preset ? null : (inputs.custom || null);
  if (custom) {
    if (custom.name !== inputs.activity) {
      throw new Error("custom config names a different activity");
    }
    checkCustomActivity(custom);
  }
  const weights = preset ? preset.weights
    : custom ? custom.weights : cfg.weights;
  if (!inputs.routine) {
    return { config: cfg.version, activity: inputs.activity, state: "rest",
      stateLabel: "Rest day: no routine scheduled", blocks: [],
      excluded: ["aqi", "pollen"], grain: cfg.grain, weights };
  }
  const hi = heatIndexC(inputs.obs.tempC, inputs.obs.rh);
  const blocks = inputs.uvBlocks.map((b) => {
    const gates = [];
    if ((inputs.obs.rainMm || 0) > cfg.gates.rainMm) gates.push("Rain observed (IMD)");
    if (cfg.gates.thunderstorm.includes(inputs.obs.sigwx)) gates.push("Thunderstorm risk (IMD)");
    if (hi >= cfg.gates.heatIndexC) gates.push(`Heat index ${hi} °C (IMD obs)`);
    if (b.uv != null && b.uv >= cfg.gates.uvIndex) gates.push(`UV ${b.uv} extreme (labelled adapter)`);
    const gated = gates.length > 0;
    const components = {
      heat: heatScore(hi),
      humidity: humidityScore(inputs.obs.rh),
      wind: windScoreVolleyball(inputs.obs.windMS),
      ...(b.uv != null ? { uv: uvScore(b.uv) } : {}),
      // aqi excluded: no adapter value (named in `excluded`, never zero-filled)
    };
    const available = Object.keys(weights).filter((k) => k in components);
    const denom = available.reduce((s, k) => s + weights[k], 0);
    const score = gated ? 0 : Math.round(
      available.reduce((s, k) => s + weights[k] * components[k], 0) / denom);
    return {
      id: b.id, startIST: b.startIST, endIST: b.endIST, gated, gateReason: gates[0] || null,
      score, heatIndexC: hi, uv: b.uv, components,
      prov: {
        imd: `${inputs.obs.station} · issued ${inputs.obs.issuedUtc}`,
        uv: b.uvSrc || "labelled adapter",
        daylight: `${inputs.solar.sunriseIST}–${inputs.solar.sunsetIST} IST (computed solar times, not IMD)`,
      },
    };
  });
  const open = blocks.filter((b) => !b.gated).sort((a, b) => b.score - a.score || (a.id < b.id ? -1 : 1));
  if (open.length === 0) {
    return { config: cfg.version, activity: inputs.activity, state: "no-window",
      stateLabel: "No good window today", blocks,
      excluded: ["aqi", "pollen"], grain: cfg.grain, weights };
  }
  const [best, ...rest] = open;
  const avoid = [...blocks].filter((b) => b.id !== best.id)
    .sort((a, b) => (a.gated ? -1 : 1) - (b.gated ? -1 : 1) || a.score - b.score)[0];
  return {
    config: cfg.version, activity: inputs.activity, state: "ready",
    bestId: best.id, alternateIds: rest.slice(0, 2).map((b) => b.id),
    avoidId: avoid && avoid.id !== best.id ? avoid.id : null,
    blocks, excluded: ["aqi", "pollen"], grain: cfg.grain, weights,
  };
}

function canonicalizeWindows(result) {
  const sort = (v) => {
    if (Array.isArray(v)) return `[${v.map(sort).join(",")}]`;
    if (v && typeof v === "object") {
      return `{${Object.keys(v).sort().map((k) => `${JSON.stringify(k)}:${sort(v[k])}`).join(",")}}`;
    }
    if (typeof v === "number") return JSON.stringify(Math.round(v * 1e6) / 1e6);
    return JSON.stringify(v);
  };
  return sort(result);
}

function replayWindows(inputs) {
  return canonicalizeWindows(deriveWindows(inputs));
}

const WindowsAPI = {
  WINDOWS_V1, ACTIVITY_PRESETS, METRIC_KEYS, CANONICAL_WEIGHTS: WINDOWS_V1.weights,
  checkCustomActivity,
  heatIndexC, humidityScore, windScoreVolleyball, uvScore, heatScore,
  deriveWindows, canonicalizeWindows, replayWindows,
};
if (typeof module !== "undefined") module.exports = WindowsAPI;
if (typeof window !== "undefined") window.MausamWindows = WindowsAPI;
