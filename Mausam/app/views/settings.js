"use strict";

(function () {
// views/settings.js — Settings, Places, Map and Inbox. Honest about what
// needs the finale host: sync (ticket 14) and the WFS warning overlay (13).

const { esc, store, $, $$, latLabel } = window.MausamCore;
const { icon } = window.MausamIcons;
const { t } = window.MausamI18n;
const { ageLabel } = window.MausamEngine;
const Personal = window.MausamPersonal;
const PERSONA_SHORT = window.MausamCore.PERSONA_SHORT;

const DEFAULT_PLACES = [{ label: "New Delhi", lat: 28.6139, lon: 77.209 }];

function places() {
  return store.get("places", DEFAULT_PLACES).map((p, i) => (p.id ? p : { ...p, id: `legacy-${i}` }));
}

function personaValue(state) {
  const primary = PERSONA_SHORT[state.personas[0]] || PERSONA_SHORT.commuter;
  const extra = state.personas.length - 1;
  return extra > 0 ? `${primary} + ${extra}` : primary;
}

/* ---------- settings ---------- */

function settingsHTML(state, api) {
  const T = (k) => t(state.lang, k);
  const list = places();
  const heroId = api.ranked().hero.id;
  const count = Personal.verdictsFor(api.ledger(), heroId);
  const submitted = count.up + count.down;
  const placeRows = list.map((p, i) => `<a class="row" href="#/places">
      <span class="row__left">
        <span class="row__icon">${icon("pin", 17)}</span>
        <span class="row__label">${esc(p.label)}</span>
        ${i === 0 ? `<span class="pill pill--accent">${esc(T("settings.home"))}</span>` : ""}
      </span>
      <span class="row__value tabular">${latLabel(p.lat)}</span>
    </a>`).join("");

  return `<div class="screen" data-view="settings">
    <div class="pane">
      <div class="settings__head">
        <h1 class="settings__title">${esc(T("settings.title"))}</h1>
        <span class="pill pill--official">${icon("check", 11, { sw: 2.6 })}IMD Official</span>
      </div>

      <div class="card profile">
        <span class="profile__left">
          <span class="avatar">${icon("user", 20)}</span>
          <span>
            <span class="profile__name">${esc(T("settings.guest"))} <span class="badge-offline">${esc(T("settings.offline"))}</span></span>
            <p class="profile__text">${esc(T("settings.guestSub"))}</p>
          </span>
        </span>
        <button class="btn btn--mini" type="button" data-signin>${esc(T("settings.signin"))}</button>
      </div>
      <p class="note hide" id="settings-note" role="status">${icon("info", 15)}<span>${esc(T("settings.signinGap"))}</span></p>

      <div class="group">
        <p class="section-label">${esc(T("settings.saved"))}</p>
        <div class="rows">
          ${placeRows}
          <a class="row" href="#/places">
            <span class="row__left"><span class="row__icon row__icon--accent">${icon("plus", 17)}</span>
            <span class="row__label" style="color:var(--accent);font-weight:600">${esc(T("settings.addPlace"))}</span></span>
          </a>
        </div>
      </div>

      <div class="group">
        <p class="section-label">${esc(T("settings.prefs"))}</p>
        <div class="rows">
          <div class="row">
            <span class="row__left"><span class="row__icon">${icon("globe", 17)}</span><span class="row__label">${esc(T("settings.language"))}</span></span>
            <select class="row__select" id="settings-lang" aria-label="${esc(T("settings.language"))}">
              <option value="en"${state.lang === "en" ? " selected" : ""}>English</option>
              <option value="hi"${state.lang === "hi" ? " selected" : ""}>हिंदी</option>
            </select>
          </div>
          <button class="row" type="button" data-edit-personas>
            <span class="row__left"><span class="row__icon">${icon("users", 17)}</span><span class="row__label">${esc(T("settings.personas"))}</span></span>
            <span class="row__value row__value--accent">${esc(personaValue(state))} ${icon("chevronRight", 15)}</span>
          </button>
          <div class="row">
            <span class="row__left"><span class="row__icon">${icon("shieldCheck", 17)}</span>
              <span><span class="row__label">${esc(T("settings.provenance"))}</span>
              <span class="row__sub">${esc(T("settings.provSub"))}</span></span></span>
            <label class="toggle">
              <input type="checkbox" id="settings-prov" ${state.provenance ? "checked" : ""} aria-label="${esc(T("settings.provenance"))}" />
              <span class="toggle__track"><span class="toggle__thumb"></span></span>
            </label>
          </div>
          <a class="row" href="#/inbox">
            <span class="row__left"><span class="row__icon row__icon--accent">${icon("bell", 17)}</span><span class="row__label">${esc(T("settings.notifications"))}</span></span>
            <span class="row__value"><span class="pill pill--accent">${esc(T("settings.sevOnly"))}</span>${icon("chevronRight", 15)}</span>
          </a>
          <a class="row" href="#/planner">
            <span class="row__left"><span class="row__icon">${icon("clock", 17)}</span>
              <span><span class="row__label">${esc(T("settings.planner"))}</span>
              <span class="row__sub">${esc(T("settings.plannerSub"))}</span></span></span>
            <span class="row__value">${icon("chevronRight", 15)}</span>
          </a>
        </div>
      </div>

      <div class="group">
        <p class="section-label">${esc(T("settings.feedback"))}</p>
        <div class="card">
          <div class="spread">
            <span class="row__label">${esc(T("settings.useful"))}</span>
            <span class="caption tabular">${submitted} ${esc(T("settings.submitted"))}</span>
          </div>
          <div class="actions mt-3" style="grid-template-columns:1fr 1fr">
            <button class="btn btn--ghost btn--sm" type="button" data-fb="up">${icon("check", 15)}${esc(T("settings.yes"))}</button>
            <button class="btn btn--ghost btn--sm" type="button" data-fb="down">${icon("close", 14)}${esc(T("settings.no"))}</button>
          </div>
          <p class="caption mt-2">${esc(T("settings.useful"))} · ${esc(api.ranked().hero.category)}</p>
        </div>
      </div>

      <div class="group">
        <p class="section-label">${esc(T("settings.about"))}</p>
        <div class="rows">
          <div class="row">
            <span class="row__left"><span class="row__label">${esc(T("settings.source"))}</span></span>
            <span class="row__value">${esc(T("settings.sourceVal"))} · ${esc(T("settings.sourceSub"))}</span>
          </div>
          <div class="row">
            <span class="row__left"><span class="row__label">${esc(T("settings.version"))}</span></span>
            <span class="row__value tabular">${esc(T("settings.versionVal"))}</span>
          </div>
          <button class="row row--danger" type="button" data-delete>
            <span class="row__left"><span class="row__icon">${icon("trash", 17)}</span><span class="row__label">${esc(T("settings.delete"))}</span></span>
            <span class="row__value">${icon("chevronRight", 15)}</span>
          </button>
        </div>
        <p class="caption">${esc(T("settings.deleteNote"))}</p>
      </div>
    </div>
  </div>`;
}

function wireSettings(state, api) {
  const T = (k) => t(state.lang, k);
  const signin = $("[data-signin]");
  if (signin) signin.addEventListener("click", () => $("#settings-note")?.classList.remove("hide"));
  const lang = $("#settings-lang");
  if (lang) lang.addEventListener("change", () => api.setLang(lang.value));
  const prov = $("#settings-prov");
  if (prov) prov.addEventListener("change", () => api.setProvenance(prov.checked));
  $$("[data-fb]").forEach((b) => b.addEventListener("click", () => api.recordFeedback(b.dataset.fb)));
  const edit = $("[data-edit-personas]");
  if (edit) edit.addEventListener("click", () => api.editPersonas());
  const del = $("[data-delete]");
  if (del) del.addEventListener("click", () => {
    if (!window.confirm(`${T("settings.delete")}?`)) return;
    api.resetAll();
  });
}

/* ---------- places ---------- */

function placeRow(p) {
  return `<div class="station">
    <span class="station__left">
      <span class="row__icon">${icon("pin", 17)}</span>
      <span><span class="station__name">${esc(p.label)}</span>
      <p class="station__meta tabular">${latLabel(p.lat)} · ${p.lon.toFixed(3)}° E</p></span>
    </span>
    <span class="row-tight">
      <button class="btn btn--mini btn--ghost" type="button" data-place-rename="${esc(p.id)}">Rename</button>
      <button class="btn btn--mini btn--ghost" type="button" data-place-del="${esc(p.id)}">${icon("trash", 14)}</button>
    </span>
  </div>`;
}

function placesHTML(state) {
  const T = (k) => t(state.lang, k);
  return `<div class="screen" data-view="places">
    <div class="pane">
      <div class="pane__head">
        <div><h1 class="pane__title">${esc(T("places.title"))}</h1>
        <p class="pane__sub">${esc(T("places.stored"))}</p></div>
      </div>
      <div class="rows">${places().map(placeRow).join("")}</div>
      <div class="card">
        <p class="section-label" style="padding:0">${esc(T("places.add"))}</p>
        <div class="form-row mt-3">
          <label>Name <input id="place-label" size="12" placeholder="Work" aria-label="Place name" /></label>
          <button type="button" id="place-add">Add New Delhi</button>
        </div>
        <p class="caption mt-2">${esc(T("places.oneTap"))}</p>
      </div>
      <div class="note note--quiet">${icon("info", 15)}
        <span>${esc(T("settings.signinGap"))}</span></div>
    </div>
  </div>`;
}

function wirePlaces(state, api) {
  const add = $("#place-add");
  if (add) add.addEventListener("click", () => {
    const label = $("#place-label").value;
    try {
      store.set("places", Personal.addPlace(places(), { label, lat: 28.6139, lon: 77.209 }));
    } catch (e) { alert(e.message); return; }
    api.render();
  });
  $$("[data-place-del]").forEach((b) => b.addEventListener("click", () => {
    store.set("places", Personal.removePlace(places(), b.dataset.placeDel));
    api.render();
  }));
  $$("[data-place-rename]").forEach((b) => b.addEventListener("click", () => {
    const name = window.prompt("Rename place to:");
    if (!name) return;
    try {
      store.set("places", Personal.renamePlace(places(), b.dataset.placeRename, name));
    } catch (e) { alert(e.message); return; }
    api.render();
  }));
}

/* ---------- map ---------- */

function mapHTML(state, api) {
  const T = (k) => t(state.lang, k);
  const { station } = api.ranked();
  const feats = state.bundle.features;
  const rows = feats.map((f) => {
    const p = f.properties;
    const vis = p.visibility == null ? "—" : `${(p.visibility / 1000).toFixed(p.visibility < 1000 ? 1 : 0)} km`;
    const cls = p.visibility == null ? "" : p.visibility <= 1000 ? "dot--high" : p.visibility <= 4000 ? "dot--medium" : "";
    return `<div class="station">
      <span class="station__left">
        <span class="dot ${cls}"></span>
        <span><span class="station__name">${esc(p.station)}</span>
        <p class="station__meta">Observed ${esc(ageLabel(p.update_time, state.bundle.capture.captured_at_utc))}</p></span>
      </span>
      <span class="row-tight">
        <span class="station__val">${esc(vis)}</span>
        <span class="station__val" style="color:var(--label-3)">${p.dbtemp == null ? "—" : esc(p.dbtemp)} °C</span>
      </span>
    </div>`;
  }).join("");
  return `<div class="screen" data-view="map">
    <div class="pane">
      <div class="pane__head">
        <div><h1 class="pane__title">${esc(T("map.title"))}</h1>
        <p class="pane__sub">${esc(T("map.sub"))}</p></div>
      </div>
      <div class="card" style="padding:0;overflow:hidden">
        <div class="map-hero" style="height:300px;border-radius:16px 16px 0 0">${window.MausamHome.mapSVG(state, station)}</div>
        <p class="caption" style="padding:10px 14px">${esc(T("map.caption"))}</p>
      </div>
      <div class="note">${icon("info", 15)}<span>${esc(T("map.overlay"))}</span></div>
      <div class="group">
        <p class="section-label">${esc(T("map.stations"))}</p>
        <div class="rows">${rows}</div>
      </div>
    </div>
  </div>`;
}

/* ---------- inbox ---------- */

function inboxHTML(state, api) {
  const T = (k) => t(state.lang, k);
  const entries = Personal.inboxEntries(api.ledger());
  const items = entries.length
    ? entries.map((e) => `<div class="inbox__item">
        <span>${e.verdict === "up" ? icon("check", 14) : icon("close", 13)} ${esc(e.cardId)}</span>
        <span class="caption">${esc(new Date(e.at).toLocaleString("en-IN"))}</span>
      </div>`).join("")
    : `<p class="mini__text">${esc(T("inbox.empty"))}</p>`;
  return `<div class="screen" data-view="inbox">
    <div class="pane">
      <div class="pane__head">
        <div class="row-tight">
          <a class="icon-btn" href="#/settings" aria-label="${esc(T("back"))}">${icon("back", 18)}</a>
          <h1 class="pane__title">${esc(T("inbox.title"))}</h1>
        </div>
      </div>
      <div class="card">${items}</div>
      <div class="note note--quiet">${icon("info", 15)}<span>${esc(T("inbox.note"))}</span></div>
    </div>
  </div>`;
}

const Settings = { settingsHTML, wireSettings, placesHTML, wirePlaces, mapHTML, inboxHTML };
if (typeof window !== "undefined") window.MausamSettings = Settings;
})();
