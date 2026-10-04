"use strict";

// engine/chat.js — the grounded assistant matcher (PRD v1.2, FR-21–FR-27).
// Deterministic templates over the personal bundle. No DOM, no network, no
// clock. The matcher NEVER emits a weather number: every value in a reply is
// quoted from ctx (cards, window, gaps) or echoed from the user's own words
// (a routine time they typed). Anything unanswerable becomes the honest gap
// line, never a guess.

const ACTIVITY_SYNONYMS = [
  ["volleyball", ["volleyball", "volley", "volley ball"]],
  ["run", ["run", "running", "jog", "jogging", "morning run"]],
  ["walk", ["walk", "walking", "evening walk"]],
  ["office", ["office", "commute", "commuting", "work", "school run"]],
];

const PERSONA_WORDS = [
  ["health", ["health"]],
  ["fitness", ["fitness", "gym"]],
  ["beach", ["beach", "surf"]],
  ["travel", ["travel", "travelling", "traveling", "trip"]],
  ["parents", ["parents", "family", "kids", "school"]],
  ["agriculture", ["agriculture", "farmer", "farming", "crop", "sowing"]],
  ["commuter", ["commuter", "commute"]],
  ["events", ["event", "wedding", "planner"]],
];

const DAY_WORDS = [["Mon", ["mon", "monday"]], ["Tue", ["tue", "tuesday"]],
  ["Wed", ["wed", "wednesday"]], ["Thu", ["thu", "thursday"]],
  ["Fri", ["fri", "friday"]], ["Sat", ["sat", "saturday"]],
  ["Sun", ["sun", "sunday"]]];

// The comfort scale label. Pinned to windows-v1 like the weights: it is a
// display convention of the scoring model, never a weather reading.
const SCORE_SCALE = "/100";

function low(s) { return String(s || "").toLowerCase(); }

function findWord(text, table) {
  const t = ` ${low(text)} `;
  for (const [key, words] of table) {
    if (words.some((w) => t.includes(w))) return key;
  }
  return null;
}

function parseDays(text) {
  const t = low(text);
  if (/\b(daily|everyday|every day|all days)\b/.test(t)) return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  if (/\bweekdays?\b/.test(t)) return ["Mon", "Tue", "Wed", "Thu", "Fri"];
  if (/\bweekends?\b/.test(t)) return ["Sat", "Sun"];
  const days = DAY_WORDS.filter(([, words]) => words.some((w) => new RegExp(`\\b${w}\\b`).test(t))).map(([d]) => d);
  return days.length ? [...new Set(days)] : ["Sat"];
}

// "7", "7:30", "7am", "7:30pm" -> "07:00" / "19:30". Bare hours mean morning:
// routines are departure alerts, and the demo slice leaves at 07:00.
function parseTime(text) {
  const m = /(\d{1,2})(?::(\d{2}))?\s*(am|pm)?/i.exec(text);
  if (!m) return null;
  let h = parseInt(m[1], 10);
  const min = m[2] ? parseInt(m[2], 10) : 0;
  const ap = (m[3] || "").toLowerCase();
  if (h > 23 || min > 59) return null;
  if (ap === "pm" && h < 12) h += 12;
  if (ap === "am" && h === 12) h = 0;
  if (!ap && h > 23) return null;
  return `${String(h).padStart(2, "0")}:${String(min).padStart(2, "0")}`;
}

function matchActivity(text, customs) {
  const hit = findWord(text, ACTIVITY_SYNONYMS);
  if (hit) return hit;
  const t = low(text);
  for (const c of customs || []) {
    if (c.name && t.includes(low(c.name))) return c.name;
  }
  return null;
}

function cardLine(c) {
  const facts = (c.facts || []).map((f) => `${f.label} ${f.value}${f.unit || ""}`).join(", ");
  const p = c.prov || {};
  const src = [p.source, p.station].filter(Boolean).join(" · ");
  return { facts, src };
}

// Every reply quotes ctx or the user's words. ctx: { persona, placeName,
// hero, cards, gaps, window, routines }.
function answer(text, ctx) {
  const c = ctx || {};
  const cards = c.cards || [];
  const hero = c.hero || cards[0] || null;
  const say = (s) => ({ text: s, cardRef: null });
  const t = low(text).trim();

  if (!t) return { replies: [say("Ask about a card, a routine, or the best time today.")] };
  if (/^(hi|hello|hey|namaste)\b/.test(t) || t.includes("help") || t.includes("what can you")) {
    return { replies: [say("I explain cards, read out sources, set routine reminders, and tell you the best time today. Everything I say comes from the data on your screen.")] };
  }

  // Routine creation: "remind me for my run at 7am", "alert me weekdays 8:30".
  if (/\b(remind|reminder|alert|notify|routine)\b/.test(t)) {
    const activity = matchActivity(t, c.customs) || "run";
    const departIST = parseTime(t) || "07:00";
    const days = parseDays(t);
    return {
      replies: [say(`Done: ${activity}, ${days.join(", ")}, leaving ${departIST}. It is saved on this phone, with a departure alert 30 minutes before.`)],
      action: { type: "routine", activity, days, departIST },
    };
  }

  // Persona switch: "switch to farmer", "I am a commuter".
  if (/\b(switch|change|persona|i am a|i'm a)\b/.test(t)) {
    const key = findWord(t, PERSONA_WORDS);
    if (key) return { replies: [say(`Switched. The home now reorders for ${key}.`)], action: { type: "persona", key } };
  }

  // Best window: "best time to play", "when should I run".
  if (/\b(best time|best window|when should|when to|good time)\b/.test(t)) {
    const w = c.window;
    if (w) return { replies: [say(`${w.activity}: ${w.start} to ${w.end} scores ${w.score}${SCORE_SCALE}, the best window today. Open the planner for the alternates.`) ] };
    return { replies: [say("No routine covers today, so there is no window scored. Add a routine and I will score it.")] };
  }

  // Gaps: "why no AQI", "pollen".
  const gaps = c.gaps || [];
  const gapHit = gaps.find((g) => t.includes(low(g.id).replace("gap-", "")) || (g.reason && t.includes("why")));
  if (/\b(why|pollen|aqi|traffic|soil)\b/.test(t) && gaps.length) {
    const g = gapHit || gaps[0];
    return { replies: [say(`${g.category || "That"}: ${g.reason || "not published"}. The card says so instead of guessing.`)] };
  }

  // Provenance: "where is this from", "which station".
  if (/\b(where|source|station|from|issued|how old|provenance)\b/.test(t) && hero && hero.prov) {
    const p = hero.prov;
    return { replies: [say(`${p.source}, ${p.station}. That is what the top card is built from.`)] };
  }

  // Explain: seeded card context, or "what does visibility mean".
  const seed = c.seed || null;
  if (/\b(what does|mean|explain|this card|fog|visibility|humidity|heat)\b/.test(t)) {
    const item = seed || hero;
    if (item) {
      const { facts, src } = cardLine(item);
      const body = facts ? `${item.action}. Behind it: ${facts}.` : `${item.action}.`;
      return { replies: [say(src ? `${body} Source: ${src}.` : body)] };
    }
  }

  // Seeded card with no question words: explain it.
  if (seed) {
    const { facts, src } = cardLine(seed);
    return { replies: [say(facts ? `${seed.action}. Behind it: ${facts}.${src ? ` Source: ${src}.` : ""}` : `${seed.action}.`)] };
  }

  return { replies: [say("I don't have that data. I only read what is on your screen: the cards, the planner, and your routines.")] };
}

const ChatAPI = { answer, parseTime, parseDays, matchActivity, ACTIVITY_SYNONYMS, SCORE_SCALE };
if (typeof module !== "undefined") module.exports = ChatAPI;
if (typeof window !== "undefined") window.MausamChat = ChatAPI;
