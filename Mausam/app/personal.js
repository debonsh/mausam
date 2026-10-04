"use strict";

// Tickets 15 + 19 — saved places, routines, feedback and the inbox ledger as
// pure on-device functions. No network, no Firebase. Sync across devices is
// a stated gap until the Firebase project exists (ticket 14); everything
// here survives a reload via localStorage and syncs on reconnect never.

const WinEng = (typeof require !== "undefined")
  ? require("./engine/windows.js")
  : window.MausamWindows;

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function uid() {
  return `p${Date.now().toString(36)}${Math.floor(Math.random() * 1e4)}`;
}

function checkPlace({ label, lat, lon }) {
  if (!label || !String(label).trim()) throw new Error("place needs a label");
  for (const [v, lo, hi, name] of [[lat, -90, 90, "lat"], [lon, -180, 180, "lon"]]) {
    if (!Number.isFinite(v) || v < lo || v > hi) throw new Error(`place ${name} out of range`);
  }
}

function addPlace(list, { label, lat, lon }) {
  checkPlace({ label, lat, lon });
  return [...list, { id: uid(), label: String(label).trim(), lat, lon }];
}

function renamePlace(list, id, label) {
  if (!label || !String(label).trim()) throw new Error("place needs a label");
  return list.map((p) => (p.id === id ? { ...p, label: String(label).trim() } : p));
}

function removePlace(list, id) {
  return list.filter((p) => p.id !== id);
}

function checkRoutine({ activity, days, departIST }, customs = []) {
  const known = WinEng.ACTIVITY_PRESETS[activity] ||
    (customs || []).some((c) => c.name === activity);
  if (!known) throw new Error(`unknown activity: ${activity}`);
  if (!Array.isArray(days) || days.length === 0 ||
      days.some((d) => !WEEKDAYS.includes(d))) throw new Error("routine needs valid days");
  if (!/^\d{2}:\d{2}$/.test(departIST || "")) throw new Error("routine needs HH:MM departure");
}

function addRoutine(list, { activity, days, departIST }, customs = []) {
  checkRoutine({ activity, days, departIST }, customs);
  return [...list, { id: uid(), activity, days: [...days], departIST }];
}

// Custom activities (planner UX pass): on-device only, like
// routines. The engine owns validation (checkCustomActivity);
// storage just pins an id and keeps the config verbatim.
function addCustomActivity(list, ca) {
  WinEng.checkCustomActivity(ca);
  return [...list, { id: uid(), name: String(ca.name).trim(),
    version: ca.version, weights: { ...ca.weights } }];
}

function removeCustomActivity(list, id) {
  return list.filter((c) => c.id !== id);
}

function customWeightsFor(customs, name) {
  const c = (customs || []).find((x) => x.name === name);
  return c ? { version: c.version, weights: { ...c.weights } } : null;
}

function removeRoutine(list, id) {
  return list.filter((r) => r.id !== id);
}

function routinesForDay(list, weekday) {
  return list.filter((r) => r.days.includes(weekday));
}

function recordFeedback(ledger, { cardId, verdict, at }) {
  if (!["up", "down"].includes(verdict)) throw new Error("verdict is up or down");
  return [...ledger, { kind: "feedback", cardId, verdict, at }];
}

function verdictsFor(ledger, cardId) {
  const counts = { up: 0, down: 0 };
  for (const e of ledger) if (e.kind === "feedback" && e.cardId === cardId) counts[e.verdict] += 1;
  return counts;
}

// Newest first. Fully usable when push is denied or unavailable — the inbox
// IS the fallback (ticket 18 stays host-gated).
function inboxEntries(ledger) {
  return [...ledger].sort((a, b) => (a.at < b.at ? 1 : a.at > b.at ? -1 : 0));
}

const PersonalAPI = { WEEKDAYS, addPlace, renamePlace, removePlace,
  addRoutine, removeRoutine, routinesForDay,
  addCustomActivity, removeCustomActivity, customWeightsFor,
  recordFeedback, verdictsFor, inboxEntries };
if (typeof module !== "undefined") module.exports = PersonalAPI;
if (typeof window !== "undefined") window.MausamPersonal = PersonalAPI;
