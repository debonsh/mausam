"use strict";
// Onboarding contract: three skippable steps with defaults (ticket 14).
// Run: node --test tests/
const { test } = require("node:test");
const assert = require("assert");
const E = require("../app/engine/deriveCard.js");

test("eight personas with PS words", () => {
  assert.strictEqual(E.PERSONA_KEYS.length, 8);
  assert.ok(E.PERSONA_KEYS.includes("commuter"));
  assert.ok(E.PERSONA_KEYS.includes("agriculture"));
  assert.ok(E.PERSONA_KEYS.includes("health"));
});

test("unknown persona falls back to commuter", () => {
  const ranked = E.rankStack([], "nobody");
  assert.deepStrictEqual(ranked, []);
});
