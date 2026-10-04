"use strict";
// Tickets 15 + 19: places, routines, feedback and the inbox ledger as pure,
// on-device functions. No network, no Firebase; sync is a stated gap.
const { test } = require("node:test");
const assert = require("assert");
const P = require("../app/personal.js");

test("15: saved places add / rename / remove without mutating", () => {
  const mine = P.addPlace([], { label: "Home", lat: 28.6, lon: 77.2 });
  assert.strictEqual(mine.length, 1);
  const renamed = P.renamePlace(mine, mine[0].id, "Work");
  assert.strictEqual(renamed[0].label, "Work");
  assert.strictEqual(mine[0].label, "Home", "no mutation");
  assert.deepStrictEqual(P.removePlace(renamed, mine[0].id), []);
});

test("15: places reject empties and coordinate garbage", () => {
  assert.throws(() => P.addPlace([], { label: "  ", lat: 28.6, lon: 77.2 }));
  assert.throws(() => P.addPlace([], { label: "X", lat: 999, lon: 77.2 }));
});

test("19: routines validate activity + days, query per weekday", () => {
  const rs = P.addRoutine([], { activity: "run", days: ["Mon", "Sat"], departIST: "07:00" });
  assert.strictEqual(rs.length, 1);
  assert.deepStrictEqual(P.routinesForDay(rs, "Sat").length, 1);
  assert.deepStrictEqual(P.routinesForDay(rs, "Tue").length, 0);
  assert.throws(() => P.addRoutine([], { activity: "surf", days: ["Sat"], departIST: "07:00" }));
  assert.throws(() => P.addRoutine([], { activity: "run", days: ["Funday"], departIST: "07:00" }));
});

test("19: feedback ledger appends and the inbox reads newest-first", () => {
  let ledger = P.recordFeedback([], { cardId: "vis", verdict: "up", at: "2026-10-03T01:00:00Z" });
  ledger = P.recordFeedback(ledger, { cardId: "vis", verdict: "down", at: "2026-10-03T02:00:00Z" });
  assert.deepStrictEqual(P.verdictsFor(ledger, "vis"), { up: 1, down: 1 });
  const inbox = P.inboxEntries(ledger);
  assert.strictEqual(inbox[0].at, "2026-10-03T02:00:00Z", "newest first");
});

test("custom activities: create, look up, remove; preset names are reserved", () => {
  const cricket = { name: "cricket", version: "windows-v1", weights: { heat: 1, wind: 1 } };
  const mine = P.addCustomActivity([], cricket);
  assert.strictEqual(mine.length, 1);
  assert.deepStrictEqual(P.customWeightsFor(mine, "cricket"),
    { version: "windows-v1", weights: { heat: 1, wind: 1 } });
  assert.strictEqual(P.customWeightsFor(mine, "surf"), null);
  assert.deepStrictEqual(P.removeCustomActivity(mine, mine[0].id), []);
  assert.throws(() => P.addCustomActivity([],
    { name: "volleyball", version: "windows-v1", weights: { heat: 1 } }));
  assert.throws(() => P.addCustomActivity([],
    { name: "  ", version: "windows-v1", weights: { heat: 1 } }));
  assert.throws(() => P.addCustomActivity([], { name: "surf", weights: { heat: 1 } }));
  assert.throws(() => P.addCustomActivity([],
    { name: "surf", version: "windows-v1", weights: {} }));
});

test("routines accept custom activities and still reject unknowns", () => {
  const customs = P.addCustomActivity([],
    { name: "cricket", version: "windows-v1", weights: { heat: 1 } });
  const rs = P.addRoutine([], { activity: "cricket", days: ["Sat"], departIST: "06:30" }, customs);
  assert.strictEqual(rs.length, 1);
  assert.throws(() => P.addRoutine([], { activity: "surf", days: ["Sat"], departIST: "06:30" }, customs));
});
