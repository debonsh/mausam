"use strict";
// Mirrors app/engine/chat.js. The grounding contract: every weather number in
// a reply is quoted from ctx, never generated. Run: node --test tests/
const { test } = require("node:test");
const assert = require("assert");
const Chat = require("../app/engine/chat.js");

const CTX = {
  persona: "commuter",
  hero: { id: "vis", action: "Allow extra time on the road",
    facts: [{ label: "Visibility", value: "2", unit: " km" }],
    prov: { source: "IMD SYNOP", station: "New Delhi-Safdarjung" } },
  cards: [],
  gaps: [{ id: "gap-pollen", category: "Pollen", reason: "IMD publishes no pollen data." }],
  window: { activity: "run", start: "06:00", end: "09:00", score: 72 },
  routines: [],
  customs: [],
};

test("help states the grounding rule", () => {
  const r = Chat.answer("help", CTX);
  assert.match(r.replies[0].text, /data on your screen/);
});

test("routine parse: 'run at 7' becomes 07:00 on Saturday", () => {
  const r = Chat.answer("remind me for my run at 7", CTX);
  assert.strictEqual(r.action.type, "routine");
  assert.strictEqual(r.action.activity, "run");
  assert.strictEqual(r.action.departIST, "07:00");
  assert.deepStrictEqual(r.action.days, ["Sat"]);
  assert.match(r.replies[0].text, /07:00/);
});

test("routine parse: pm, weekdays and named days", () => {
  assert.strictEqual(Chat.parseTime("7:30pm"), "19:30");
  assert.strictEqual(Chat.parseTime("12am"), "00:00");
  assert.deepStrictEqual(Chat.parseDays("weekdays"), ["Mon", "Tue", "Wed", "Thu", "Fri"]);
  assert.deepStrictEqual(Chat.parseDays("mon and fri"), ["Mon", "Fri"]);
});

test("persona switch returns an action, unknown stays chat", () => {
  const r = Chat.answer("switch to farmer", CTX);
  assert.deepStrictEqual(r.action, { type: "persona", key: "agriculture" });
  const r2 = Chat.answer("switch to astronaut", CTX);
  assert.strictEqual(r2.action, undefined);
});

test("best window quotes the scored block", () => {
  const r = Chat.answer("best time to run today?", CTX);
  assert.match(r.replies[0].text, /06:00 to 09:00/);
  assert.match(r.replies[0].text, /72\/100/);
});

test("gap question quotes the gap reason, never a number", () => {
  const r = Chat.answer("why no pollen?", CTX);
  assert.match(r.replies[0].text, /no pollen data/);
});

test("provenance quotes source and station", () => {
  const r = Chat.answer("where is this from?", CTX);
  assert.match(r.replies[0].text, /IMD SYNOP/);
  assert.match(r.replies[0].text, /Safdarjung/);
});

test("unknown question is the honest fallback", () => {
  const r = Chat.answer("will it rain on Mars?", CTX);
  assert.match(r.replies[0].text, /don't have that data/);
  assert.strictEqual(r.action, undefined);
});

test("no invented weather numbers: digits only from ctx or the user", () => {
  const ctxNums = new Set((JSON.stringify(CTX) + " 07:00" + Chat.SCORE_SCALE).match(/\d+(\.\d+)?/g));
  for (const q of ["help", "best time?", "where is this from?", "why no pollen?", "explain this card", "will it rain on Mars?"]) {
    const text = Chat.answer(q, CTX).replies.map((x) => x.text).join(" ");
    for (const n of (text.match(/\d+(\.\d+)?/g) || [])) {
      assert.ok(ctxNums.has(n), `${q} invents ${n}`);
    }
  }
});
