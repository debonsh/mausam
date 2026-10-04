"use strict";

(function () {
// views/home.js — the map + bottom-sheet home: persona chips, the hero
// action card with its triggering facts and source row, the ranked stack,
// and the honest gap rows. Every number comes from the engine.

const { esc, placeShort, $, $$, PERSONA_SHORT } = window.MausamCore;
const { icon, METRIC_ICONS, PERSONA_ICONS } = window.MausamIcons;
const { t } = window.MausamI18n;
const { PERSONA_KEYS, ageLabel, istTime } = window.MausamEngine;

const GAP_LABELS = {
  "gap-aqi": { label: "Air quality (AQI)", chip: "CPCB" },
  "gap-pollen": { label: "Pollen" },
  "gap-traffic": { label: "Traffic" },
  "gap-soil": { label: "Soil moisture" },
};

/* ---------- schematic map (shared with the Map tab) ---------- */

function stationPos(lon, lat) {
  return { x: 195 + (lon - 77.17) * 600, y: 148 - (lat - 28.58) * 500 };
}

function visibilityClass(vis) {
  if (vis == null) return "";
  if (vis <= 1000) return "mg-dot--high";
  if (vis <= 4000) return "mg-dot--medium";
  return "mg-dot--ok";
}

// Schematic Delhi: boundaries, roads and the observed stations, tinted by
// IMD's own visibility thresholds. Never a tile claim.
function mapSVG(state, nearest) {
  const feats = state.bundle ? state.bundle.features : [];
  let stations = "";
  feats.forEach((f, i) => {
    const [lon, lat] = f.geometry.coordinates;
    const { x, y } = stationPos(lon, lat);
    const p = f.properties;
    const isNearest = nearest && p.station === nearest.p.station;
    const above = i % 2 === 0;
    if (isNearest) {
      stations += `<circle class="mg-halo" cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="14"/>` +
        `<circle class="mg-pin" cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="6"/>` +
        `<circle class="mg-pin-core" cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="2.5"/>`;
    } else {
      stations += `<circle class="mg-dot ${visibilityClass(p.visibility)}" cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="4.5"/>`;
    }
    const ly = above ? y - 11 : y + 19;
    stations += `<text class="mg-station-label" x="${x.toFixed(0)}" y="${ly.toFixed(0)}" text-anchor="middle">${esc(placeShort(p.station))}</text>`;
  });
  return `<svg class="map-svg" viewBox="0 0 390 292" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <path class="mg-road" d="M-20 60 C80 50, 180 90, 410 70"/>
    <path class="mg-road" d="M30 -20 C50 100, 120 180, 160 300"/>
    <path class="mg-road" d="M210 -20 C190 80, 260 200, 320 300"/>
    <path class="mg-road mg-road--2" d="M-10 180 C120 160, 240 220, 410 190"/>
    <path class="mg-road mg-road--dash" d="M80 40 L340 260"/>
    <path class="mg-road mg-road--dash" d="M300 20 L90 270"/>
    <circle class="mg-ring" cx="195" cy="148" r="110"/>
    <circle class="mg-ring" cx="195" cy="148" r="72"/>
    <path class="mg-boundary" d="M120 70 C160 55, 230 65, 265 100 C295 130, 280 185, 245 215 C210 240, 150 245, 125 210 C100 180, 90 130, 105 95 Z"/>
    ${stations}
  </svg>`;
}

/* ---------- pieces ---------- */

function chips(state) {
  // The mock keeps the active persona first so it is always visible in the
  // 8-chip row; the rest keep the engine's canonical order.
  const order = [state.persona, ...PERSONA_KEYS.filter((k) => k !== state.persona)];
  return order.map((k) => {
    const on = k === state.persona;
    return `<button class="chip${on ? " chip--active" : ""}" type="button" data-persona="${k}" aria-pressed="${on}">
      ${icon(PERSONA_ICONS[k], 14)}<span>${esc(PERSONA_SHORT[k])}</span>${on ? `<span class="chip__check">${icon("check", 12, { sw: 2.6 })}</span>` : ""}
    </button>`;
  }).join("");
}

function sevClass(sev) {
  return sev === "high" ? "high" : sev === "ok" || sev === "low" ? "ok" : "medium";
}

function heroCard(item) {
  return `<article class="hero" data-sev="${esc(item.sev)}" data-id="${esc(item.id)}">
    <p class="hero__eyebrow"><span class="dot dot--${sevClass(item.sev)}"></span><span class="text">${esc(item.category)}</span></p>
    <h2 class="hero__action">${esc(item.action)}</h2>
    ${item.detail ? `<p class="hero__detail">${esc(item.detail)}</p>` : ""}
  </article>`;
}

function metricTile(f) {
  const ic = METRIC_ICONS[f.label] || "eye";
  return `<button class="metric" type="button" data-metric aria-label="${esc(f.label)} ${esc(f.value)}${esc(f.unit)}, show provenance">
    <span class="metric__top"><span class="metric__label">${esc(f.label)}</span>${icon(ic, 14)}</span>
    <span>
      <span class="metric__value">${esc(f.value)}<span class="metric__unit">${esc(f.unit)}</span></span>
    </span>
  </button>`;
}

function sourceRow(item, label) {
  const p = item.prov;
  return `<button class="source" type="button" data-source="${esc(item.id)}" aria-label="${esc(label || "Show where these values come from")}">
    <span class="source__icon">${icon("shield", 13)}</span>
    <span class="source__main">
      <span class="source__text">${esc(p.source)} ${esc(p.station)}, issued ${esc(istTime(p.issuedUtc))}</span>
      <span class="source__endpoint"><span>${esc(p.endpoint)} · ${esc(p.layer)}</span></span>
    </span>
    ${icon("chevronRight", 16)}
  </button>`;
}

function miniCard(item) {
  return `<article class="mini stack-more" data-sev="${esc(item.sev)}" data-id="${esc(item.id)}">
    <p class="hero__eyebrow"><span class="dot dot--${sevClass(item.sev)}"></span><span class="text">${esc(item.category)}</span></p>
    <h3 class="mini__title mt-2">${esc(item.action)}</h3>
    ${item.detail ? `<p class="mini__text">${esc(item.detail)}</p>` : ""}
    ${sourceRow(item, "Show where this value comes from")}
  </article>`;
}

function gapRow(gap) {
  const meta = GAP_LABELS[gap.id] || { label: gap.category };
  return `<div class="gap-row">
    <span class="gap-row__label">${esc(meta.label)}${meta.chip ? ` <span class="pill pill--source">${esc(meta.chip)}</span>` : ""}</span>
    <span class="gap-row__why">${esc(gap.reason)}</span>
  </div>`;
}

function todayCard(state, api) {
  const w = api.todayWindow();
  if (!w) return "";
  return `<article class="mini stack-more">
    <p class="hero__eyebrow"><span class="dot dot--medium"></span><span class="text">${esc(w.activity)} · today</span></p>
    <h3 class="mini__title mt-2">Play ${esc(w.start)} to ${esc(w.end)}, best window today</h3>
    <p class="mini__text"><a href="#/planner">See the planner</a> · score ${w.score}/100 (${esc(w.config)})</p>
  </article>`;
}

/* ---------- screen ---------- */

function html(state, api) {
  const { station, cards, gaps, hero } = api.ranked();
  const rest = cards.slice(1);
  return `<div class="screen" data-view="home">
    <div class="map-hero">
      ${mapSVG(state, station)}
      <div class="map-hero__head">
        <div class="map-hero__row">
          <div>
            <h1 class="map-hero__place">${esc(state.place.name)}</h1>
            <p class="map-hero__fresh">
              <span class="live-dot" aria-hidden="true"></span>
              <span id="freshness-text">Updated ${esc(ageLabel(station.p.update_time, state.bundle.capture.captured_at_utc))}</span>
              <span class="offline-pill" id="offline-badge" hidden>${esc(t(state.lang, "offline"))}</span>
            </p>
          </div>
          <button class="icon-btn" type="button" data-prov-toggle aria-pressed="${state.provenance}"
                  aria-label="Show where every value comes from">${icon("info", 19)}</button>
        </div>
      </div>
      <div class="map-legend">
        <span class="dot dot--${sevClass(hero.sev)}"></span>
        ${esc(hero.category)} · ${esc(placeShort(station.p.station))}
      </div>
    </div>

    <section class="sheet" id="sheet" data-snap="${esc(state.snap)}" aria-label="Decision stack">
      <div class="sheet__grab"><button id="handle" type="button" aria-label="Change sheet height"><span></span></button></div>
      <div class="sheet__chips">
        <div class="chips" role="group" aria-label="Persona">${chips(state)}</div>
        <div class="chips__fade" aria-hidden="true"></div>
      </div>
      <div class="sheet__scroll">
        ${heroCard(hero)}
        <div class="metrics">${hero.facts.map(metricTile).join("")}</div>
        ${sourceRow(hero)}
        ${todayCard(state, api)}
        ${rest.map(miniCard).join("")}
        ${gaps.length ? `<section class="gaps stack-more--deep" aria-label="${esc(t(state.lang, "home.gaps"))}">
          <p class="section-label gaps__title">${esc(t(state.lang, "home.gaps"))}</p>
          ${gaps.map(gapRow).join("")}
        </section>` : ""}
      </div>
    </section>
  </div>`;
}

/* ---------- wiring ---------- */

function wire(state, api) {
  $$("[data-persona]").forEach((b) =>
    b.addEventListener("click", () => api.setPersona(b.dataset.persona)));

  const toggle = $("[data-prov-toggle]");
  if (toggle) toggle.addEventListener("click", () => api.setProvenance(!state.provenance));

  $$(".source[data-source]").forEach((b) =>
    b.addEventListener("click", () => api.openProvenance(b.dataset.source)));
  $$(".metric[data-metric]").forEach((b) => {
    const card = b.closest("[data-id]");
    b.addEventListener("click", () => api.openProvenance(card ? card.dataset.id : null));
  });

  const handle = $("#handle");
  if (handle) {
    const order = ["peek", "half", "full"];
    handle.addEventListener("click", () =>
      api.setSnap(order[(order.indexOf(state.snap) + 1) % order.length]));
    let y0 = null;
    handle.addEventListener("pointerdown", (e) => {
      y0 = e.clientY;
      handle.setPointerCapture(e.pointerId);
    });
    handle.addEventListener("pointerup", (e) => {
      if (y0 == null) return;
      const dy = e.clientY - y0;
      y0 = null;
      const i = order.indexOf(state.snap);
      if (dy < -24 && i < 2) api.setSnap(order[i + 1]);
      else if (dy > 24 && i > 0) api.setSnap(order[i - 1]);
    });
  }
}

const Home = { html, wire, mapSVG };
if (typeof window !== "undefined") window.MausamHome = Home;
})();
