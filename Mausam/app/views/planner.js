"use strict";

(function () {
// views/planner.js — activity windows and routines (tickets 16–19), restyled
// to the current design. Deterministic: the engine owns every score; this
// file owns forms and the week strip. Stored on-device only.

const { esc, store, $, $$ } = window.MausamCore;
const { icon } = window.MausamIcons;
const { t } = window.MausamI18n;
const { nearestStation } = window.MausamEngine;
const Windows = window.MausamWindows;
const Personal = window.MausamPersonal;

// Planner form state: survives re-renders at module level (the form is
// re-rendered on every state change, so DOM state alone would not).
let builderOpen = false;
let formDays = new Set();

const routines = () => store.get("routines", null); // null = Saturday demo slice

// The demo slice is real product state: until a routine is saved, Saturday
// shows the current activity — the same default the week strip renders.
function effectiveRoutines(state) {
  const stored = routines();
  if (stored) return stored;
  return [{ id: "demo", activity: state.activity, days: ["Sat"], departIST: "07:00" }];
}

function inputs(state, activity) {
  const act = activity || state.activity;
  const f = state.planner;
  const st = nearestStation(f.features, state.place);
  const p = st.p;
  const uv = f.uv.hourly;
  const idx = (iso) => uv.time.indexOf(iso);
  const mean = (hours) => {
    const vs = hours.map((h) => uv.uv_index[idx(`2026-10-03T${h}:00`)]);
    return Math.round((vs.reduce((a, b) => a + b, 0) / vs.length) * 10) / 10;
  };
  const blocks = [
    { id: "b06", startIST: "06:00", endIST: "09:00", uv: mean(["06", "07", "08"]) },
    { id: "b09", startIST: "09:00", endIST: "12:00", uv: mean(["09", "10", "11"]) },
    { id: "b12", startIST: "12:00", endIST: "15:00", uv: mean(["12", "13", "14"]) },
    { id: "b15", startIST: "15:00", endIST: "18:00", uv: mean(["15", "16", "17"]) },
  ].map((b) => ({ ...b, uvSrc: "Non-IMD · Copernicus CAMS via Open-Meteo" }));
  const rest = new URLSearchParams(typeof location !== "undefined" ? location.search : "").get("planner") === "rest";
  return {
    obs: { tempC: p.dbtemp, rh: p.rh, windMS: p.windsp, rainMm: p["24hrlyrain"] || 0,
      sigwx: p.sigwx, station: `IMD SYNOP · ${p.station}`,
      issuedUtc: p.update_time, capturedAt: f.capture.captured_at_utc,
      endpoint: f.capture.endpoint, layer: f.capture.request.typename },
    uvBlocks: blocks,
    solar: { sunriseIST: f.solar.sunriseIST, sunsetIST: f.solar.sunsetIST },
    activity: act,
    custom: Windows.ACTIVITY_PRESETS[act] ? null : Personal.customWeightsFor(state.customs, act),
    routine: rest ? null : { days: ["Sat"], departIST: "07:00" },
    adapters: { aqi: null },
  };
}

// Ticket 19 — when a routine covers today, its best window joins the home
// stack. Date is display-only; the engine never sees a clock.
function today(state) {
  if (!state.planner) return null;
  const day = Personal.WEEKDAYS[(new Date().getDay() + 6) % 7];
  const todays = Personal.routinesForDay(effectiveRoutines(state), day);
  if (todays.length === 0) return null;
  const r = todays[0];
  const w = Windows.deriveWindows(inputs(state, r.activity));
  if (w.state !== "ready") return null;
  const best = w.blocks.find((b) => b.id === w.bestId);
  return { activity: r.activity, start: best.startIST, end: best.endIST, score: best.score, config: w.config };
}

/* ---------- pieces ---------- */

function weightsLine(w) {
  return `weights ${Object.entries(w.weights).map(([k, v]) => `${k} ${String(v).replace("0.", ".")}`).join(" · ")}`;
}

// Leave time default: best-window start minus a 30-minute buffer.
function minusMin(hhmm, m) {
  const [h, mm] = hhmm.split(":").map(Number);
  const v = (h * 60 + mm - m + 1440) % 1440;
  return `${String(Math.floor(v / 60)).padStart(2, "0")}:${String(v % 60).padStart(2, "0")}`;
}

function activityOptions(state, selected) {
  return Object.keys(Windows.ACTIVITY_PRESETS)
    .concat(state.customs.map((c) => c.name))
    .map((a) => `<option value="${esc(a)}"${a === selected ? " selected" : ""}>${esc(a)}</option>`)
    .join("") + `<option value="__new__">${esc(t(state.lang, "custom.new"))}</option>`;
}

function windowCard(state, w, b, tag) {
  const inputsObj = inputs(state, w.activity);
  const status = b.gated ? `gated: ${b.gateReason}` : "no gates tripped";
  return `<article class="mini" data-sev="${b.gated ? "high" : "ok"}">
    <p class="hero__eyebrow"><span class="dot ${b.gated ? "dot--high" : "dot--medium"}"></span>
      <span class="text">${esc(tag)}</span></p>
    <h3 class="mini__title mt-2">${b.gated ? "Skip" : "Play"} ${esc(b.startIST)} to ${esc(b.endIST)}${b.id === w.bestId ? ", best window today" : ""}</h3>
    <div class="metrics mt-3">
      <div class="metric"><span class="metric__top"><span class="metric__label">Comfort</span>${icon("check", 14)}</span>
        <span><span class="metric__value">${b.score}<span class="metric__unit">/100</span></span></span></div>
      <div class="metric"><span class="metric__top"><span class="metric__label">Heat index</span>${icon("thermometer", 14)}</span>
        <span><span class="metric__value">${b.heatIndexC}<span class="metric__unit">°C</span></span></span></div>
      <div class="metric"><span class="metric__top"><span class="metric__label">UV index</span>${icon("sun", 14)}</span>
        <span><span class="metric__value">${b.uv}</span></span></div>
    </div>
    <button class="source mt-3" type="button" data-window="${esc(b.id)}" aria-label="Show window provenance">
      <span class="source__icon">${icon("shield", 13)}</span>
      <span class="source__main">
        <span class="source__text">${esc(inputsObj.obs.station)} · CAMS UV (labelled)</span>
        <span class="source__endpoint"><span>${esc(weightsLine(w))} · AQI excluded (no source)</span></span>
      </span>
      ${icon("chevronRight", 16)}
    </button>
  </article>`;
}

function customBuilder(state) {
  if (!builderOpen) return "";
  const checks = Windows.METRIC_KEYS.map((k) =>
    `<label class="check"><input type="checkbox" id="cb-${k}" checked /> ${esc(t(state.lang, "metric." + k))}</label>`).join("");
  return `<div class="card">
    <p class="hero__eyebrow"><span class="dot dot--medium"></span><span class="text">${esc(t(state.lang, "custom.title"))}</span></p>
    <p class="form-row mt-3"><label>${esc(t(state.lang, "custom.name"))} <input id="custom-name" size="14" maxlength="40" placeholder="Cricket" aria-label="${esc(t(state.lang, "custom.name"))}" /></label></p>
    <p class="form-row">${esc(t(state.lang, "custom.matters"))} ${checks}</p>
    <p class="caption">${esc(t(state.lang, "custom.always"))}</p>
    <p class="form-row mt-2"><button type="button" id="custom-save">${esc(t(state.lang, "custom.save"))}</button>
    <button type="button" id="custom-cancel" style="background:none;color:var(--label-3);border:1px solid var(--line)">${esc(t(state.lang, "custom.cancel"))}</button></p>
  </div>`;
}

function weekStrip(state) {
  const list = effectiveRoutines(state);
  const days = Personal.WEEKDAYS.map((d) => {
    const rs = Personal.routinesForDay(list, d);
    return `<span class="week__day${rs.length ? " week__day--on" : ""}">${esc(d)}${rs.length ? ` · ${esc(rs[0].activity)}` : ""}</span>`;
  }).join("");
  return `<p class="week" aria-label="Week routines">${days}</p>`;
}

function routineForm(state, w) {
  const best = w.state === "ready" ? w.blocks.find((b) => b.id === w.bestId) : null;
  const leave = best ? minusMin(best.startIST, 30) : "07:00";
  const days = Personal.WEEKDAYS.map((d) =>
    `<button type="button" class="chip${formDays.has(d) ? " chip--active" : ""}" data-day="${d}" aria-pressed="${formDays.has(d)}">${esc(d)}</button>`).join("");
  return `<div class="card">
    <p class="hero__eyebrow"><span class="dot dot--medium"></span><span class="text">Routines</span></p>
    <p class="form-row mt-3"><label>${esc(t(state.lang, "routine.activity"))}
      <select id="routine-activity" aria-label="${esc(t(state.lang, "routine.activity"))}">${activityOptions(state, state.activity)}</select></label></p>
    <p class="form-row"><span id="routine-days-label">${esc(t(state.lang, "routine.days"))}</span>
      <span class="chips chips--wrap" role="group" aria-labelledby="routine-days-label">${days}</span></p>
    <p class="form-row"><label>${esc(t(state.lang, "routine.leave"))}
      <input id="routine-depart" inputmode="numeric" placeholder="07:00" size="5" value="${leave}" aria-label="${esc(t(state.lang, "routine.leave"))}" /></label>
      <button type="button" id="routine-add">Add</button></p>
    <div id="routine-list">${routineList(state)}</div>
    <p class="caption">Stored on this device only; deleted with the routine. Push alerts need the finale host (ticket 18).</p>
  </div>`;
}

function routineList(state) {
  const stored = routines();
  if (!stored) return `<p class="caption">Demo slice: Saturday ${esc(state.activity)}. Add a routine to make it yours.</p>`;
  if (stored.length === 0) return `<p class="caption">No routines. Every day is a rest day.</p>`;
  return stored.map((r) =>
    `<p class="routine"><span>${esc(r.activity)} · ${esc(r.days.join(","))} · leave ${esc(r.departIST)}</span>
     <button type="button" data-routine-del="${esc(r.id)}">Remove</button></p>`).join("");
}

/* ---------- screen ---------- */

function html(state, api) {
  const T = (k) => t(state.lang, k);
  if (!state.planner) {
    return `<div class="screen" data-view="planner"><div class="pane">
      <div class="pane__head"><a class="icon-btn" href="#/" aria-label="${esc(T("back"))}">${icon("back", 18)}</a>
        <h1 class="pane__title">${esc(T("planner.title"))}</h1></div>
      <div class="note note--quiet">${icon("info", 15)}<span>The planner fixture did not load.</span></div>
    </div></div>`;
  }
  const head = `<div class="pane__head">
    <div class="row-tight">
      <a class="icon-btn" href="#/" aria-label="${esc(T("back"))}">${icon("back", 18)}</a>
      <div><h1 class="pane__title">${esc(T("planner.title"))}</h1>
      <p class="pane__sub">${esc(state.activity)} · Saturday · 3-hour blocks</p></div>
    </div>
  </div>`;

  const w = Windows.deriveWindows(inputs(state));
  let body;
  if (w.state !== "ready") {
    body = `<div class="card">
      <p class="hero__eyebrow"><span class="dot dot--medium"></span><span class="text">${esc(w.stateLabel)}</span></p>
      <p class="mini__text">${w.state === "rest"
        ? "No routine is scheduled for today. Add a Saturday routine below to see windows."
        : "Every daylight block is gated. Check the gate reasons in a window's provenance."}</p>
      <p class="caption mt-2">Excluded metrics: ${esc(w.excluded.join(", "))} (no source) · grain: ${esc(w.grain)}</p>
    </div>`;
  } else {
    const byId = Object.fromEntries(w.blocks.map((b) => [b.id, b]));
    body = windowCard(state, w, byId[w.bestId], "Best window") +
      w.alternateIds.map((id) => windowCard(state, w, byId[id], "Also good")).join("") +
      (w.avoidId ? windowCard(state, w, byId[w.avoidId], byId[w.avoidId].gated ? "Avoid" : "Weakest") : "") +
      `<div class="note note--quiet">${icon("info", 15)}<span>AQI excluded: CPCB unreachable, no labelled mirror responded. Pollen: no source exists. The score renormalises over available metrics.</span></div>`;
  }

  return `<div class="screen" data-view="planner"><div class="planner">
    ${head}
    <div class="card">
      <p class="form-row"><label>${esc(T("routine.activity"))}
        <select id="preset-select" aria-label="${esc(T("routine.activity"))}">${activityOptions(state, state.activity)}</select></label></p>
      ${customBuilder(state)}
      ${weekStrip(state)}
    </div>
    ${body}
    ${routineForm(state, w)}
  </div></div>`;
}

/* ---------- wiring ---------- */

function wire(state, api) {
  const preset = $("#preset-select");
  if (preset) preset.addEventListener("change", () => {
    if (preset.value === "__new__") { builderOpen = true; api.render(); return; }
    api.setActivity(preset.value);
  });
  const save = $("#custom-save");
  if (save) save.addEventListener("click", () => {
    const name = $("#custom-name").value.trim();
    const weights = {};
    for (const k of Windows.METRIC_KEYS) {
      const cb = document.getElementById("cb-" + k);
      if (cb && cb.checked) weights[k] = Windows.CANONICAL_WEIGHTS[k];
    }
    try {
      const ca = { name, version: Windows.WINDOWS_V1.version, weights };
      state.customs = Personal.addCustomActivity(state.customs, ca);
      store.set("customs", state.customs);
      builderOpen = false;
      api.setActivity(ca.name);
    } catch (e) { alert(e.message); }
  });
  const cancel = $("#custom-cancel");
  if (cancel) cancel.addEventListener("click", () => { builderOpen = false; api.render(); });

  $$("[data-day]").forEach((b) => b.addEventListener("click", () => {
    const d = b.dataset.day;
    if (formDays.has(d)) formDays.delete(d); else formDays.add(d);
    api.render();
  }));
  const add = $("#routine-add");
  if (add) add.addEventListener("click", () => {
    const activity = $("#routine-activity").value;
    if (activity === "__new__") { builderOpen = true; api.render(); return; }
    const days = [...formDays];
    const departIST = $("#routine-depart").value || "07:00";
    try {
      store.set("routines", Personal.addRoutine(routines() || [], { activity, days, departIST }, state.customs));
      formDays = new Set();
    } catch (e) { alert(e.message); return; }
    api.render();
  });
  $$("[data-routine-del]").forEach((b) => b.addEventListener("click", () => {
    store.set("routines", Personal.removeRoutine(routines() || [], b.dataset.routineDel));
    api.render();
  }));
  $$("[data-window]").forEach((b) => b.addEventListener("click", () => api.openWindowProvenance(b.dataset.window)));
}

const Planner = { html, wire, inputs, today };
if (typeof window !== "undefined") window.MausamPlanner = Planner;
})();
