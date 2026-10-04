"use strict";

(function () {
// views/onboarding.js — the first run: splash → get started → language →
// login → location → persona (four steps, every step skippable; Skip lands
// on the commuter home). Login is honest about the Firebase gap (ticket 14).

const { esc, $, $$, PERSONA_SHORT } = window.MausamCore;
const { icon, PERSONA_ICONS } = window.MausamIcons;
const { t } = window.MausamI18n;
const { PERSONA_KEYS } = window.MausamEngine;

const STEPS = { SPLASH: 0, START: 1, LANG: 2, LOGIN: 3, LOC: 4, PERSONA: 5 };
const STEP_PILL = { 2: "1 / 4", 3: "2 / 4", 4: "3 / 4", 5: "4 / 4" };

const CITIES = ["Delhi", "Mumbai", "Chennai", "Kolkata"];

function topbar(state, api, opts) {
  const back = opts.back != null
    ? `<button class="ob__back" type="button" data-back="${opts.back}" aria-label="${esc(t(state.lang, "back"))}">${icon("back", 20, { sw: 2.2 })}</button>`
    : "<span></span>";
  const pill = opts.step
    ? `<span class="pill pill--step"><span class="dot dot--medium"></span><span class="tabular">${STEP_PILL[opts.step]}</span></span>`
    : "<span></span>";
  const skip = opts.skip
    ? `<button class="ob__skip" type="button" data-skip>${esc(t(state.lang, "skip"))}</button>`
    : "<span></span>";
  return `<header class="ob__top">${back}${pill}${skip}</header>`;
}

function brand(state) {
  return `<div class="brand ob__brand">
    <span class="brand__mark">${icon("sun", 17, { sw: 2.2 })}</span>
    <span class="brand__name">Mausam</span>
    <span class="pill pill--official">${icon("check", 11, { sw: 2.6 })}${esc(t(state.lang, "gs.badge"))}</span>
  </div>`;
}

function footer(cta, api, extra) {
  return `<footer class="ob__footer">
    <button class="btn btn--block ${cta.class || ""}" type="button" ${cta.attrs}>${esc(cta.label)}</button>
    ${extra || ""}
    <div class="ob__homebar"></div>
  </footer>`;
}

/* ---------- 0 · splash ---------- */

function splashHTML(state, api) {
  const ready = Boolean(state.bundle);
  return `<div class="ob ob--center" data-view="splash">
    <div class="ob__top ob__top--center">
      <span class="pill pill--official">${icon("check", 11, { sw: 2.6 })}IMD Official</span>
    </div>
    <div class="ob__body ob__body--center">
      <div class="brand__mark brand__mark--xl">${icon("mark", 44, { sw: 1.8 })}</div>
      <div>
        <h1 class="ob__brand-title">Mausam</h1>
        <p class="sub ob__tagline">${esc(t(state.lang, "splash.tagline"))}</p>
      </div>
      <span class="pill pill--step ob__status ${ready ? "" : "ob__status--loading"}">
        ${ready ? icon("check", 12, { sw: 2.6 }) : icon("refresh", 12, { sw: 2.4 })}
        <span class="tabular">${esc(ready ? "IMD data ready" : t(state.lang, "splash.loading"))}</span>
      </span>
    </div>
    <div class="ob__footer ob__footer--plain">
      <button class="btn btn--block" type="button" data-go="${STEPS.START}">${esc(t(state.lang, "ob.getStarted"))}</button>
      <button class="btn btn--quiet btn--block" type="button" data-finish="guest">${esc(t(state.lang, "ob.guest"))}</button>
      <p class="caption ob__foot">${esc(t(state.lang, "splash.foot"))}</p>
    </div>
  </div>`;
}

/* ---------- 1 · get started ---------- */

function startHTML(state, api) {
  const rows = [
    ["zap", "gs.f1", "gs.f1s"], ["shieldCheck", "gs.f2", "gs.f2s"], ["alert", "gs.f3", "gs.f3s"],
  ].map(([ic, ti, tx]) => `<div class="feature">
      <span class="feature__icon">${icon(ic, 20)}</span>
      <span><span class="feature__title">${esc(t(state.lang, ti))}</span>
      <span class="feature__text">${esc(t(state.lang, tx))}</span></span>
    </div>`).join("");
  return `<div class="ob" data-view="start">
    ${topbar(state, api, { back: STEPS.SPLASH, skip: true })}
    <div class="ob__body">
      <span class="pill pill--official ob__badge">${icon("check", 11, { sw: 2.6 })}${esc(t(state.lang, "gs.badge"))}</span>
      <h1 class="h1 ob__title">${esc(t(state.lang, "gs.title"))}</h1>
      <div class="ob__list">${rows}</div>
      <div class="primer mt-4">${icon("lock", 15)}<span>${esc(t(state.lang, "gs.primer"))}</span></div>
    </div>
    ${footer({ label: t(state.lang, "ob.getStarted"), attrs: `data-go="${STEPS.LANG}"` }, api,
      `<button class="btn btn--quiet btn--block" type="button" data-finish="guest">${esc(t(state.lang, "ob.guest"))}</button>`)}
  </div>`;
}

/* ---------- 2 · language ---------- */

function option({ selected, title, sub, value, lang }) {
  return `<button class="option${selected ? " option--selected" : ""}" type="button" data-lang="${value}" aria-pressed="${selected}" ${lang ? `lang="${lang}"` : ""}>
    <span>
      <span class="option__title">${esc(title)}${selected ? ` <span class="pill pill--accent">${esc(t(value, "lang.sel"))}</span>` : ""}</span>
      <span class="option__sub">${esc(sub)}</span>
    </span>
    ${selected ? `<span class="option__check">${icon("check", 13, { sw: 2.8 })}</span>` : `<span class="option__radio"></span>`}
  </button>`;
}

function langHTML(state, api) {
  return `<div class="ob" data-view="lang">
    ${topbar(state, api, { back: STEPS.START, step: STEPS.LANG, skip: true })}
    ${brand(state)}
    <div class="ob__body">
      <h1 class="h1 ob__title">${esc(t(state.lang, "lang.title"))}</h1>
      <p class="sub">${esc(t(state.lang, "lang.sub"))}</p>
      <p class="section-label mt-4">${esc(t(state.lang, "lang.select"))}</p>
      <div class="ob__list">
        ${option({ selected: state.lang === "en", title: "English", sub: t(state.lang, "lang.enSub"), value: "en" })}
        ${option({ selected: state.lang === "hi", title: "हिंदी", sub: t("en", "lang.hiSub"), value: "hi", lang: "hi" })}
      </div>
      <div class="ob__privacy mt-4">${icon("lock", 15)}<span>${esc(t(state.lang, "lang.note"))}</span></div>
    </div>
    ${footer({ label: t(state.lang, "ob.continue"), attrs: `data-go="${STEPS.LOGIN}"` }, api)}
  </div>`;
}

/* ---------- 3 · login (step 2 of 4) ---------- */

function loginHTML(state, api) {
  const checks = ["login.b1", "login.b2", "login.b3"].map((k) =>
    `<div class="ob__checkrow"><span class="ob__checkicon">${icon("check", 10, { sw: 3 })}</span>
     <span>${esc(t(state.lang, k))}</span></div>`).join("");
  return `<div class="ob" data-view="login">
    ${topbar(state, api, { back: STEPS.LANG, step: STEPS.LOGIN, skip: true })}
    ${brand(state)}
    <div class="ob__body">
      <h1 class="h1 ob__title">${esc(t(state.lang, "login.title"))}</h1>
      <p class="sub">${esc(t(state.lang, "login.sub"))}</p>
      <form class="ob__list" id="ob-login" novalidate>
        <label class="sr-only" for="ob-email">Email address</label>
        <input class="field" type="email" id="ob-email" name="email" placeholder="you@example.com" autocomplete="email" />
        <button class="btn btn--block" type="submit">${esc(t(state.lang, "login.send"))}</button>
        <div class="or">OR</div>
        <button class="btn btn--ghost btn--block" type="button" data-google>${icon("globe", 16)}${esc(t(state.lang, "login.google"))}</button>
      </form>
      <p class="note hide" id="ob-note" role="status">${icon("info", 15)}<span></span></p>
      <div class="ob__checks mt-4">${checks}</div>
    </div>
    ${footer({ label: t(state.lang, "ob.guest"), attrs: `data-go="${STEPS.LOC}"`, class: "btn--quiet" }, api,
      `<p class="caption ob__foot-note">${esc(t(state.lang, "login.note"))}</p>`)}
  </div>`;
}

/* ---------- 4 · location (step 3 of 4) ---------- */

function locHTML(state, api) {
  const chips = CITIES.map((c) =>
    `<button class="chip${c === "Delhi" ? " chip--active" : ""}" type="button" data-city="${esc(c)}" aria-pressed="${c === "Delhi"}">${esc(c)}</button>`).join("");
  return `<div class="ob" data-view="loc">
    ${topbar(state, api, { back: STEPS.LOGIN, step: STEPS.LOC, skip: true })}
    ${brand(state)}
    <div class="ob__body">
      <h1 class="h1 ob__title">${esc(t(state.lang, "loc.title"))}</h1>
      <p class="sub">${esc(t(state.lang, "loc.sub"))}</p>
      <div class="ob__list">
        <button class="option option--row" type="button" data-gps>
          <span class="option__row">
            <span class="feature__icon">${icon("pin", 19)}</span>
            <span class="option__text"><span class="option__title">${esc(t(state.lang, "loc.gps"))}</span>
            <span class="option__sub">${esc(t(state.lang, "loc.gpsSub"))}</span></span>
          </span>
          ${icon("chevronRight", 18)}
        </button>
        <div class="or">${esc(t(state.lang, "loc.or"))}</div>
        <form class="field-row" id="ob-search">
          ${icon("search", 16)}
          <input class="field" type="search" id="ob-search-input" placeholder="${esc(t(state.lang, "loc.search"))}" aria-label="${esc(t(state.lang, "loc.search"))}" />
        </form>
        <div>
          <p class="section-label">${esc(t(state.lang, "loc.popular"))}</p>
          <div class="chips chips--wrap mt-2">${chips}</div>
        </div>
      </div>
      <p class="note hide" id="ob-note" role="status">${icon("info", 15)}<span></span></p>
      <div class="ob__privacy mt-4">${icon("shieldCheck", 15)}<span>${esc(t(state.lang, "loc.privacy"))}</span></div>
    </div>
    ${footer({ label: t(state.lang, "ob.continue"), attrs: `data-go="${STEPS.PERSONA}"` }, api)}
  </div>`;
}

/* ---------- 5 · persona (step 4 of 4) ---------- */

function personaHTML(state, api) {
  const selected = state.personas;
  const primary = selected[0];
  const cards = PERSONA_KEYS.map((k) => {
    const on = selected.includes(k);
    const isPrimary = k === primary;
    return `<button class="persona-card${on ? " persona-card--on" : ""}" type="button"
        data-persona-card="${k}" aria-pressed="${on}">
      <span class="persona-card__top">
        <span class="persona-card__icon">${icon(PERSONA_ICONS[k], 16)}</span>
        <span class="row-tight">
          ${isPrimary ? `<span class="persona-card__badge">${esc(t(state.lang, "persona.primary"))}</span>` : ""}
          <span class="persona-card__ring">${on ? icon("check", 10, { sw: 3 }) : ""}</span>
        </span>
      </span>
      <span class="persona-card__name">${esc(PERSONA_SHORT[k])}</span>
    </button>`;
  }).join("");
  const edit = state.obEdit;
  return `<div class="ob" data-view="persona">
    ${topbar(state, api, edit
      ? { back: "settings", skip: false }
      : { back: STEPS.LOC, step: STEPS.PERSONA, skip: true })}
    ${brand(state)}
    <div class="ob__body">
      <h1 class="h1 ob__title">${esc(t(state.lang, edit ? "persona.edit" : "persona.title"))}</h1>
      <p class="sub">${esc(t(state.lang, "persona.sub"))}</p>
      <div class="persona-grid mt-4">${cards}</div>
    </div>
    <footer class="ob__footer">
      <div class="ob__hint">${icon("lock", 13)}<span>${esc(t(state.lang, "persona.hint"))}</span></div>
      <button class="btn btn--block" type="button" data-persona-done>${esc(t(state.lang, edit ? "custom.save" : "persona.see"))}</button>
      <div class="ob__homebar"></div>
    </footer>
  </div>`;
}

/* ---------- dispatch + wiring ---------- */

function html(state) {
  switch (state.obStep) {
    case STEPS.SPLASH: return splashHTML(state);
    case STEPS.START: return startHTML(state);
    case STEPS.LANG: return langHTML(state);
    case STEPS.LOGIN: return loginHTML(state);
    case STEPS.LOC: return locHTML(state);
    default: return personaHTML(state);
  }
}

function showNote(sel, text) {
  const el = $(sel);
  if (!el) return;
  el.classList.remove("hide");
  el.querySelector("span").textContent = text;
}

function wire(state, api) {
  const T = (k) => t(state.lang, k);
  const stepGo = (n) => api.set({ obStep: Number(n) });

  $$("[data-back]").forEach((b) => b.addEventListener("click", () => {
    const to = b.dataset.back;
    if (to === "settings") api.setRoute("settings");
    else stepGo(to);
  }));
  $$("[data-skip]").forEach((b) => b.addEventListener("click", () => api.finishOnboarding()));
  $$("[data-go]").forEach((b) => b.addEventListener("click", () => stepGo(b.dataset.go)));
  $$("[data-finish]").forEach((b) => b.addEventListener("click", () => api.finishOnboarding()));

  const langBtn = (v) => $(`[data-lang="${v}"]`);
  ["en", "hi"].forEach((v) => {
    const b = langBtn(v);
    if (b) b.addEventListener("click", () => api.setLang(v));
  });

  const login = $("#ob-login");
  if (login) {
    login.addEventListener("submit", (e) => {
      e.preventDefault();
      showNote("#ob-note", T("login.gap"));
    });
    const g = login.querySelector("[data-google]");
    if (g) g.addEventListener("click", () => showNote("#ob-note", T("login.gap")));
  }

  const gps = $("[data-gps]");
  if (gps) gps.addEventListener("click", () => showNote("#ob-note", T("loc.gap")));
  const search = $("#ob-search");
  if (search) search.addEventListener("submit", (e) => {
    e.preventDefault();
    showNote("#ob-note", T("loc.gap"));
    const i = $("#ob-search-input");
    if (i) i.value = "";
  });
  $$("[data-city]").forEach((b) => b.addEventListener("click", () => {
    if (b.dataset.city === "Delhi") return;
    showNote("#ob-note", T("loc.gap"));
  }));

  $$("[data-persona-card]").forEach((b) => b.addEventListener("click", () => {
    const k = b.dataset.personaCard;
    const list = [...state.personas];
    const i = list.indexOf(k);
    if (i >= 0) {
      if (list.length === 1) return; // at least one persona (PRD §4)
      list.splice(i, 1);
    } else {
      list.push(k);
    }
    api.setPersonas(list);
  }));

  const done = $("[data-persona-done]");
  if (done) done.addEventListener("click", () => {
    if (state.obEdit) api.setRoute("settings", { obEdit: false });
    else api.finishOnboarding();
  });
}

const Onboarding = { STEPS, html, wire };
if (typeof window !== "undefined") window.MausamOnboarding = Onboarding;
})();
