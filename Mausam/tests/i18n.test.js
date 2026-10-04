"use strict";
// Ticket 12: template-first EN + HI. Human-reviewed strings only;
// nothing here is machine translation of a live warning.
const { test } = require("node:test");
const assert = require("assert");
const I = require("../app/i18n.js");

test("hi differs from en on core chrome", () => {
  assert.notStrictEqual(I.t("hi", "tabs.home"), I.t("en", "tabs.home"));
  assert.strictEqual(I.t("en", "tabs.home"), "Home");
});

test("missing key falls back to en, unknown lang falls back to en", () => {
  assert.strictEqual(I.t("hi", "no.such.key"), I.t("en", "no.such.key"));
  assert.strictEqual(I.t("xx", "tabs.home"), I.t("en", "tabs.home"));
});

test("no template is ever empty", () => {
  for (const lang of I.LANGS) for (const key of Object.keys(I.STRINGS.en)) {
    assert.ok(I.t(lang, key).length > 0, `${lang}:${key} is non-empty`);
  }
});
