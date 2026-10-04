"use strict";

(function () {
// views/provenance.js — the reveal: source · station · issue time · age ·
// raw JSON, plus the replay proof. Opened from any value or source row;
// reversible and non-destructive (DESIGN §6.3).

const { esc, $, ageHours } = window.MausamCore;
const { icon } = window.MausamIcons;
const { t } = window.MausamI18n;
const { ageLabel, istTime } = window.MausamEngine;

function open({ item, raw, replay, lang, title, ask, askLabel }) {
  close();
  const p = item.prov || {};
  const age = ageLabel(p.issuedUtc, p.capturedAt);
  const hours = ageHours(p.issuedUtc, p.capturedAt);
  const fresh = hours != null && hours <= 3;
  const bytes = new TextEncoder().encode(raw).length;
  const summary = item.facts && item.facts.length
    ? item.facts.map((f) => `${f.label}: ${f.value}${f.unit}`).join(" · ")
    : (item.headline || "");
  const T = (k) => t(lang, k);

  const wrap = document.createElement("div");
  wrap.id = "prov-wrap";
  wrap.className = "modal";
  wrap.innerHTML = `
    <div class="modal__sheet" role="dialog" aria-modal="true" aria-label="${esc(title || T("prov.heading"))}">
      <div class="modal__grab"><span></span></div>
      <div class="modal__head">
        <div>
          <h2 class="modal__title">${esc(title || T("prov.heading"))}</h2>
          <p class="modal__sub">${esc(T("prov.sub"))}</p>
        </div>
        <button class="modal__close" type="button" id="prov-close" aria-label="${esc(T("close"))}">${icon("close", 16, { sw: 2.2 })}</button>
      </div>
      <div class="modal__body">
        <div class="kv">
          <div class="kv__row">
            <span class="kv__k">${esc(T("prov.source"))}</span>
            <span class="kv__v">${esc(p.source || "")}
              <span class="pill pill--ok">${icon("check", 10, { sw: 3 })}${esc(T("prov.verified"))}</span>
            </span>
          </div>
          <div class="kv__row">
            <span class="kv__k">${esc(T("prov.endpoint"))}</span>
            <span class="kv__v">
              <span class="mono-chip" title="${esc(p.endpoint || "")}">${esc(p.endpoint || "")}</span>
              <button class="copy-btn" type="button" data-copy-endpoint title="Copy endpoint">${icon("copy", 14)}</button>
            </span>
          </div>
          <div class="kv__row">
            <span class="kv__k">${esc(T("prov.station"))}</span>
            <span class="kv__v">${esc(p.station || "")}</span>
          </div>
          <div class="kv__row">
            <span class="kv__k">${esc(T("prov.issued"))}</span>
            <span class="kv__v tabular">${esc(p.issuedUtc ? istTime(p.issuedUtc) : "")}</span>
          </div>
          <div class="kv__row">
            <span class="kv__k">${esc(T("prov.age"))}</span>
            <span class="kv__v tabular">
              <span class="dot ${fresh ? "" : "dot--medium"}"></span>${esc(age)}
              ${fresh ? `<span class="pill pill--ok">${esc(T("prov.fresh"))}</span>` : ""}
            </span>
          </div>
          <div class="kv__row">
            <span class="kv__k">${esc(T("prov.type"))}</span>
            <span class="kv__v"><span class="pill pill--accent">${esc(item.category || "")}</span></span>
          </div>
          ${summary ? `<div class="kv__row">
            <span class="kv__k">${esc(T("prov.raw"))}</span>
            <span class="kv__v"><span class="mono-chip">${esc(summary)}</span></span>
          </div>` : ""}
        </div>

        <details class="raw" open>
          <summary><span>${icon("code", 14)} ${esc(T("prov.rawjson"))}</span>
            <span class="tabular">${bytes} B ${icon("chevronRight", 14)}</span></summary>
          <pre class="mono tabular">${esc(raw)}</pre>
        </details>

        <p class="cert">${icon("shieldCheck", 14)} ${esc(T("prov.cert"))}</p>
      </div>
      <div class="modal__foot">
        <button class="btn btn--block" type="button" id="replay-btn">${icon("play", 16)}${esc(T("replay"))}</button>
        <button class="btn btn--ghost btn--block" type="button" id="copy-cite">${icon("clipboard", 15)}${esc(T("prov.copy"))}</button>
        ${ask ? `<button class="btn btn--ghost btn--block" type="button" id="ask-bot">${icon("chat", 15)}${esc(askLabel || T("chat.ask"))}</button>` : ""}
        <p class="caption" id="prov-out" aria-live="polite" style="text-align:center"></p>
        <div class="modal__homebar"></div>
      </div>
    </div>`;

  document.body.appendChild(wrap);

  const out = $("#prov-out");
  $("#prov-close").addEventListener("click", close);
  if (ask) $("#ask-bot").addEventListener("click", () => { close(); ask(); });
  wrap.addEventListener("click", (e) => { if (e.target === wrap) close(); });
  document.addEventListener("keydown", escClose);
  $("#replay-btn").addEventListener("click", () => {
    out.textContent = replay ? replay() : "";
  });
  $("#copy-cite").addEventListener("click", async () => {
    const citation = `${p.source} · ${p.station} · issued ${istTime(p.issuedUtc)} · Mausam prototype on an IMD capture`;
    try {
      await navigator.clipboard.writeText(citation);
      out.textContent = T("prov.copied");
    } catch {
      out.textContent = citation;
    }
  });
  $("[data-copy-endpoint]").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(p.endpoint || "");
      out.textContent = T("prov.copied");
    } catch { /* clipboard unavailable; the endpoint is visible */ }
  });
}

function escClose(e) {
  if (e.key === "Escape") close();
}

function close() {
  document.getElementById("prov-wrap")?.remove();
  document.removeEventListener("keydown", escClose);
}

const Provenance = { open, close };
if (typeof window !== "undefined") window.MausamProvenance = Provenance;
})();
