"use strict";

(function () {
// app.js — bootstrap, state, routing and the api the views talk to.
// The home renders from real IMD captures (fixtures/) with every value
// carrying its source; the engine owns all rules, the backend owns nothing
// yet (ticket 13). Classic scripts: load after engine and views.

const { esc, store, theme, $ } = window.MausamCore;
const { icon } = window.MausamIcons;
const Engine = window.MausamEngine;
const Windows = window.MausamWindows;
const I18n = window.MausamI18n;
const Personal = window.MausamPersonal;
const Onboarding = window.MausamOnboarding;
const Home = window.MausamHome;
const Provenance = window.MausamProvenance;
const Settings = window.MausamSettings;
const Planner = window.MausamPlanner;

const FIXTURES = {
  home: ["fixtures/imd-synop-delhi-2026-10-02.json", "fixtures/imd-synop-delhi-2026-10-02.capture.json"],
  plan: ["fixtures/imd-synop-delhi-2026-10-03.json", "fixtures/imd-synop-delhi-2026-10-03.capture.json"],
  uv: "fixtures/cams-uv-delhi-2026-10-03.json",
  solar: "fixtures/solar-delhi-2026-10-03.json",
};

const params = (typeof location !== "undefined") ? new URLSearchParams(location.search) : new URLSearchParams("");

const state = {
  route: "home",               // home · map · places · settings · planner · inbox · onboarding
  obStep: Onboarding.STEPS.SPLASH,
  obEdit: false,
  bundle: null,                // { features, capture }
  planner: null,               // { features, capture, uv, solar }
  persona: params.get("persona") || store.get("persona", "commuter"),
  personas: store.get("personas", ["commuter"]),
  lang: store.get("lang", "en"),
  place: { name: "New Delhi", lat: 28.6139, lon: 77.209 },
  provenance: params.get("prov") === "1",
  snap: ["peek", "half", "full"].includes(params.get("snap")) ? params.get("snap") : "half",
  activity: store.get("activity", "volleyball"),
  customs: store.get("customs", []),
  loading: true,
  error: null,
};

if (!Engine.PERSONA_KEYS.includes(state.persona)) state.persona = "commuter";
if (!I18n.LANGS.includes(state.lang)) state.lang = "en";
state.personas = state.personas.filter((k) => Engine.PERSONA_KEYS.includes(k));
if (state.personas.length === 0) state.personas = ["commuter"];
// The active persona is always the primary: reconcile after a stored switch.
state.personas = [state.persona, ...state.personas.filter((k) => k !== state.persona)];
const knownActivity = (a) => Boolean(Windows.ACTIVITY_PRESETS[a] || Personal.customWeightsFor(state.customs, a));
if (!knownActivity(state.activity)) state.activity = "volleyball";

const ledger = () => store.get("ledger", []);
const tr = (key) => I18n.t(state.lang, key);

/* ---------- data ---------- */

function ranked() {
  const features = state.bundle.features;
  const capture = state.bundle.capture;
  const station = Engine.nearestStation(features, state.place);
  const all = Engine.rankStack(
    [...Engine.deriveCards(station, capture.captured_at_utc, capture), ...Engine.deriveGaps({ aqi: null })],
    state.persona);
  const cards = all.filter((x) => x.kind !== "gap");
  const gaps = all.filter((x) => x.kind === "gap");
  return { station, list: all, cards, gaps, hero: cards[0] };
}

function replayStack() {
  const inputs = { features: state.bundle.features, capture: state.bundle.capture,
    adapters: { aqi: null }, personaKey: state.persona, location: state.place };
  const a = Engine.replayStack(inputs);
  const b = Engine.replayStack(JSON.parse(JSON.stringify(inputs)));
  return a === b ? a.length : -1;
}

/* ---------- api ---------- */

const api = {
  render,
  ledger,
  ranked,
  todayWindow: () => Planner.today(state),

  set(partial) { Object.assign(state, partial); render(); },

  setRoute(route, extra) {
    Object.assign(state, extra || {});
    state.route = route;
    if (route !== "onboarding") {
      const hash = route === "home" ? "#/" : `#/${route}`;
      if (location.hash !== hash) history.replaceState(null, "", hash);
    }
    render();
    window.scrollTo({ top: 0 });
  },

  setLang(lang) {
    if (!I18n.LANGS.includes(lang)) return;
    state.lang = lang;
    store.set("lang", lang);
    render();
  },

  setPersona(key) {
    if (!Engine.PERSONA_KEYS.includes(key)) return;
    state.persona = key;
    state.personas = [key, ...state.personas.filter((k) => k !== key)];
    store.set("persona", key);
    store.set("personas", state.personas);
    render();
  },

  setPersonas(list) {
    const clean = (list || []).filter((k) => Engine.PERSONA_KEYS.includes(k));
    state.personas = clean.length ? clean : ["commuter"];
    state.persona = state.personas[0];
    store.set("personas", state.personas);
    store.set("persona", state.persona);
    render();
  },

  setProvenance(on) {
    state.provenance = on;
    document.body.dataset.provenance = String(on);
    const hb = $("[data-prov-toggle]");
    if (hb) hb.setAttribute("aria-pressed", String(on));
    const sb = $("#settings-prov");
    if (sb) sb.checked = on;
  },

  setSnap(snap) {
    state.snap = snap;
    const sheet = $("#sheet");
    if (sheet) sheet.dataset.snap = snap;
  },

  setActivity(a) {
    if (!knownActivity(a)) return;
    state.activity = a;
    store.set("activity", a);
    render();
  },

  recordFeedback(verdict) {
    store.set("ledger", Personal.recordFeedback(ledger(),
      { cardId: ranked().hero.id, verdict, at: new Date().toISOString() }));
    render();
  },

  editPersonas() {
    api.setRoute("onboarding", { obStep: Onboarding.STEPS.PERSONA, obEdit: true });
  },

  finishOnboarding() {
    store.set("personas", state.personas);
    store.set("persona", state.persona);
    store.set("onboarded", true);
    state.obEdit = false;
    api.setRoute("home");
  },

  resetAll() {
    store.clear();
    const fresh = { persona: "commuter", personas: ["commuter"], lang: state.lang,
      provenance: false, snap: "half", activity: "volleyball", customs: [] };
    Object.assign(state, fresh, { obStep: Onboarding.STEPS.SPLASH, obEdit: false, route: "onboarding" });
    history.replaceState(null, "", location.pathname);
    render();
  },

  openProvenance(id) {
    const { list } = ranked();
    const item = list.find((x) => x.id === id) || list[0];
    let raw = "{}";
    if (item.kind === "gap") {
      raw = JSON.stringify({ gap: item.id, reason: item.reason, value: null }, null, 2);
    } else {
      const props = state.bundle.features.map((f) => f.properties)
        .find((x) => x.station === item.prov.station);
      raw = JSON.stringify(props || {}, null, 2);
    }
    Provenance.open({ item, raw, lang: state.lang, replay: () => {
      const bytes = replayStack();
      return bytes >= 0
        ? `Re-derived ${bytes} bytes, byte-identical.`
        : "Replay mismatch, please report this.";
    } });
  },

  openWindowProvenance(blockId) {
    const inp = Planner.inputs(state);
    const w = Windows.deriveWindows(inp);
    const b = w.blocks.find((x) => x.id === blockId);
    if (!b) return;
    const item = {
      id: blockId, sev: b.gated ? "high" : "ok",
      category: `Window ${b.startIST} to ${b.endIST}`,
      facts: [
        { label: "Comfort", value: String(b.score), unit: "/100" },
        { label: "Heat index", value: String(b.heatIndexC), unit: "°C" },
        { label: "UV", value: String(b.uv), unit: "" },
      ],
      prov: { source: "IMD SYNOP + CAMS UV (labelled)", endpoint: inp.obs.endpoint,
        layer: inp.obs.layer, station: inp.obs.station.replace("IMD SYNOP · ", ""),
        issuedUtc: inp.obs.issuedUtc, capturedAt: inp.obs.capturedAt },
    };
    const raw = JSON.stringify({ score: b.score, components: b.components,
      gates: Windows.WINDOWS_V1.gates, weights: w.weights, excluded: w.excluded }, null, 2);
    Provenance.open({ item, raw, lang: state.lang, title: `Window ${b.startIST} to ${b.endIST}`, replay: () => {
      const a = Windows.replayWindows(inp);
      const b2 = Windows.replayWindows(JSON.parse(JSON.stringify(inp)));
      return a === b2 ? `Re-derived ${a.length} bytes, byte-identical.` : "Replay mismatch, please report this.";
    } });
  },
};

/* ---------- chrome ---------- */

function tabbarHTML() {
  const tabs = [
    ["home", "home", "tabs.home"], ["map", "map", "tabs.map"],
    ["places", "pin", "tabs.places"], ["settings", "gear", "tabs.settings"],
  ];
  return `<nav class="tabbar" aria-label="Primary">${tabs.map(([route, ic, key]) => {
    const on = state.route === route;
    return `<a class="tab${on ? " tab--active" : ""}" href="${route === "home" ? "#/" : `#/${route}`}"
      ${on ? 'aria-current="page"' : ""}>${icon(ic, 22)}<span>${esc(tr(key))}</span></a>`;
  }).join("")}</nav>`;
}

function errorHTML(err) {
  return `<div class="screen"><div class="pane">
    <h1 class="pane__title">Mausam</h1>
    <div class="note note--warn">${icon("alert", 16)}<span>Could not load the IMD capture (${esc(err.message)}).
    Reload to retry; the cached copy renders when offline.</span></div>
  </div></div>`;
}

function render() {
  const app = $("#app");
  if (!app) return;
  document.documentElement.lang = state.lang === "hi" ? "hi" : "en";
  document.body.dataset.provenance = String(state.provenance);
  document.body.dataset.offline = String(!navigator.onLine);

  if (state.error) { app.innerHTML = errorHTML(state.error); return; }

  if (state.route === "onboarding") {
    app.innerHTML = Onboarding.html(state, api);
    Onboarding.wire(state, api);
  } else if (state.route === "home") {
    app.innerHTML = Home.html(state, api) + tabbarHTML();
    Home.wire(state, api);
  } else if (state.route === "map") {
    app.innerHTML = Settings.mapHTML(state, api) + tabbarHTML();
  } else if (state.route === "places") {
    app.innerHTML = Settings.placesHTML(state, api) + tabbarHTML();
    Settings.wirePlaces(state, api);
  } else if (state.route === "settings") {
    app.innerHTML = Settings.settingsHTML(state, api) + tabbarHTML();
    Settings.wireSettings(state, api);
  } else if (state.route === "planner") {
    app.innerHTML = Planner.html(state, api);
    Planner.wire(state, api);
  } else if (state.route === "inbox") {
    app.innerHTML = Settings.inboxHTML(state, api);
  } else {
    app.innerHTML = Home.html(state, api) + tabbarHTML();
    Home.wire(state, api);
  }
  updateFreshness();
}

function updateFreshness() {
  const badge = $("#offline-badge");
  const text = $("#freshness-text");
  const off = !navigator.onLine;
  document.body.dataset.offline = String(off);
  if (badge) badge.hidden = !off;
  if (text && state.bundle) {
    const { station } = ranked();
    const age = Engine.ageLabel(station.p.update_time, state.bundle.capture.captured_at_utc);
    text.textContent = off ? `${tr("home.offlineLine")} · ${age}` : `Updated ${age}`;
  }
}

/* ---------- boot ---------- */

async function loadJSON(url) {
  const res = await fetch(url, { cache: "no-cache" });
  if (!res.ok) throw new Error(`${url}: ${res.status}`);
  return res.json();
}

function routeFromHash() {
  const h = location.hash;
  if (h === "#/map") return "map";
  if (h === "#/places") return "places";
  if (h === "#/settings") return "settings";
  if (h === "#/planner") return "planner";
  if (h === "#/inbox") return "inbox";
  return "home";
}

function firstRun() {
  if (params.has("persona") || params.has("prov")) return false;
  return !store.get("onboarded", false);
}

async function main() {
  theme.init();
  try {
    const [fixture, capture] = await Promise.all(FIXTURES.home.map(loadJSON));
    state.bundle = { features: fixture.features, capture };
    try {
      const [pf, pc, uvf, solar] = await Promise.all(
        [FIXTURES.plan[0], FIXTURES.plan[1], FIXTURES.uv, FIXTURES.solar].map(loadJSON));
      state.planner = { features: pf.features, capture: pc, uv: uvf, solar };
    } catch { state.planner = null; }
  } catch (err) {
    state.error = err;
  }
  state.loading = false;

  const forced = params.get("onboarding") === "1" || params.has("ob");
  if (state.error) {
    state.route = "home";
  } else if (firstRun() || forced) {
    state.route = "onboarding";
    const n = parseInt(params.get("ob"), 10);
    state.obStep = Number.isFinite(n) ? Math.min(Math.max(n, 0), Onboarding.STEPS.PERSONA) : Onboarding.STEPS.SPLASH;
  } else {
    state.route = routeFromHash();
    if (params.get("prov") === "1") state.provenance = true;
  }
  render();
  if (params.get("prov") === "1" && state.bundle && state.route === "home") {
    api.openProvenance(ranked().hero.id);
  }
}

if (typeof document !== "undefined") {
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js");
  window.addEventListener("offline", updateFreshness);
  window.addEventListener("online", updateFreshness);
  window.addEventListener("hashchange", () => {
    if (state.route === "onboarding") return;
    state.route = routeFromHash();
    render();
  });
  main();
}
})();
