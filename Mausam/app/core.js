"use strict";

(function () {
// core.js — infrastructure shared by every view: escaping, the on-device
// store, theme pinning (light/dark) and tiny format helpers. No DOM building
// here; views own their markup, the engine owns every number.

const esc = (s) =>
  String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const store = {
  get(k, d) {
    try {
      const v = localStorage.getItem("mausam:" + k);
      return v == null ? d : JSON.parse(v);
    } catch { return d; }
  },
  set(k, v) {
    try { localStorage.setItem("mausam:" + k, JSON.stringify(v)); } catch {}
  },
  clear() {
    try {
      Object.keys(localStorage)
        .filter((k) => k.startsWith("mausam:"))
        .forEach((k) => localStorage.removeItem(k));
    } catch {}
  },
};

// Theme: stored preference (light|dark|system), ?theme=light|dark pins it for
// demos and screenshots and wins over everything. The inline script in
// index.html sets data-theme before first paint; this keeps it in sync when
// the system flips and fixes the theme-color meta.
const MODES = ["light", "dark", "system"];
const theme = {
  // ?theme=light|dark pins the demo/screenshot and wins until the user
  // picks a mode in Settings, which drops the param (explicit choice wins).
  pinned() {
    if (typeof location === "undefined") return null;
    const t = new URLSearchParams(location.search).get("theme");
    return t === "light" || t === "dark" ? t : null;
  },
  mode: "system",
  current: "light",
  resolve(mode) {
    const pinned = this.pinned();
    if (pinned) return pinned;
    const m = mode || this.mode;
    if (m === "light" || m === "dark") return m;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  },
  init() {
    this.mode = MODES.includes(store.get("theme-mode", "system")) ? store.get("theme-mode", "system") : "system";
    this.apply(this.resolve());
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!this.pinned() && this.mode === "system") this.apply(e.matches ? "dark" : "light");
    });
  },
  setMode(mode) {
    if (!MODES.includes(mode)) return;
    this.mode = mode;
    store.set("theme-mode", mode);
    try {
      const url = new URL(location.href);
      if (url.searchParams.has("theme")) {
        url.searchParams.delete("theme");
        history.replaceState(null, "", url);
      }
    } catch {}
    this.apply(this.resolve());
  },
  apply(name) {
    this.current = name === "dark" ? "dark" : "light";
    document.documentElement.dataset.theme = this.current;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", this.current === "dark" ? "#000000" : "#ffffff");
  },
};

const $ = (sel, root) => (root || document).querySelector(sel);
const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

// Short persona labels for chips and cards. The full PS words live in the
// engine (PERSONAS); these are the same names, trimmed for a 12px chip.
const PERSONA_SHORT = {
  health: "Health conscious", fitness: "Fitness", beach: "Beach and surf",
  travel: "Travel", parents: "Parents and family", agriculture: "Agriculture",
  commuter: "Commuter", events: "Events",
};

// "New Delhi-Safdarjung" → "Safdarjung" (map chips, hero detail).
function placeShort(station) {
  const s = String(station || "");
  return s.includes("-") ? s.split("-").slice(1).join("-") : s;
}

// Coordinate label used on place rows: 28.61° N.
function latLabel(lat) {
  return `${Math.abs(lat).toFixed(2)}° ${lat >= 0 ? "N" : "S"}`;
}

// Data age in hours, for freshness chips in the provenance sheet.
function ageHours(issuedUtc, capturedAt) {
  const ms = new Date(capturedAt) - new Date(issuedUtc);
  return Number.isFinite(ms) ? ms / 3600000 : null;
}

const CoreAPI = { esc, store, theme, $, $$, placeShort, latLabel, ageHours, PERSONA_SHORT };
if (typeof module !== "undefined") module.exports = CoreAPI;
if (typeof window !== "undefined") window.MausamCore = CoreAPI;
})();
