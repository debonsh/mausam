"use strict";

// Ticket 02 — advisory engine v0. Framework-free: runs in Node and in the
// browser as a classic script (no DOM, no clock, no network).
// Determinism: every output derives from the passed inputs only. Ages are
// computed from the capture's own timestamps, never Date.now().

const SEV_RANK = { ok: 0, low: 1, medium: 2, high: 3 };

// The PS's eight personas, in the statement's own words (DESIGN §6.1).
const PERSONAS = [
  "Health-conscious",
  "Outdoor fitness enthusiasts",
  "Beachgoers & surfers",
  "Travelers",
  "Parents & families",
  "Agriculture & gardeners",
  "Commuters",
  "Event planners",
];
const PERSONA_KEYS = [
  "health", "fitness", "beach", "travel",
  "parents", "agriculture", "commuter", "events",
];

// Persona weight per card id. Fixed table, stated on the Tech slide (PRD Q18).
const PERSONA_WEIGHTS = {
  vis:         { commuter: 3, parents: 3, travel: 2, events: 2, health: 1, fitness: 1, beach: 1, agriculture: 1 },
  rain:        { agriculture: 3, commuter: 2, events: 2, parents: 2, travel: 2, fitness: 1, health: 1, beach: 1 },
  heat:        { health: 3, fitness: 3, agriculture: 2, parents: 2, commuter: 1, events: 1, beach: 1, travel: 1 },
  storm:       { commuter: 3, events: 2, travel: 2, parents: 2, agriculture: 1, health: 1, fitness: 1, beach: 1 },
  frost:       { agriculture: 3, commuter: 2, parents: 1, travel: 1, events: 1, health: 1, fitness: 1, beach: 1 },
  cold:        { health: 3, parents: 2, commuter: 2, agriculture: 1, travel: 1, events: 1, fitness: 1, beach: 1 },
  calm:        { commuter: 1, parents: 1, travel: 1, events: 1, health: 1, fitness: 1, beach: 1, agriculture: 1 },
  "gap-aqi":   { health: 3, fitness: 2, commuter: 1, parents: 1, travel: 1, events: 1, beach: 1, agriculture: 1 },
  "gap-pollen":{ health: 3, fitness: 1, commuter: 1, parents: 1, travel: 1, events: 1, beach: 1, agriculture: 1 },
  "gap-traffic":{ commuter: 3, travel: 2, events: 1, parents: 1, health: 1, fitness: 1, beach: 1, agriculture: 1 },
  "gap-soil":  { agriculture: 3, health: 1, fitness: 1, commuter: 1, parents: 1, travel: 1, events: 1, beach: 1 },
};

// Thunderstorm sigwx codes (IMD SYNOP present-weather). A storm card fires
// only when the held observation carries one — never from a warning feed.
const STORM_SIGWX = [17, 19, 27, 29, 91, 92, 93, 94, 95, 96, 97, 98, 99];

function fact(label, value, unit) {
  return { label, value: String(value), unit };
}

// "New Delhi-Safdarjung" → "Safdarjung": the hero's detail line names the
// station the observation came from, never a district we did not read.
function shortStation(station) {
  const s = String(station || "");
  return s.includes("-") ? s.split("-").slice(1).join("-") : s;
}

// The rule chain: the first rule that fires per signal wins. Facts are copied
// verbatim from IMD. `station` is the nearestStation() pick, `capture` the
// .capture.json sibling. Returns cards (values) only; gaps are separate.
function deriveCards(station, capturedAt, capture) {
  const p = station.p;
  const temp = p.dbtemp;
  const rh = p.rh;
  const visM = p.visibility;
  const rain = p["24hrlyrain"];
  const wind = p.windsp;

  const prov = {
    source: "IMD SYNOP",
    endpoint: capture ? capture.endpoint : "",
    layer: capture && capture.request ? capture.request.typename : "",
    station: p.station,
    issuedUtc: p.update_time,
    capturedAt,
  };

  const short = shortStation(p.station);
  const base = { prov, triggers: [] };
  const cards = [];

  if (visM != null && visM <= 1000) {
    const facts = [fact("Visibility", (visM / 1000).toFixed(visM < 1000 ? 1 : 0), "km")];
    if (temp != null) facts.push(fact("Temp", temp, "°C"));
    if (rh != null) facts.push(fact("Humidity", rh, "%"));
    cards.push({ ...base, id: "vis", sev: "high", category: "Dense fog",
      action: "Avoid driving if you can", facts,
      detail: `Fog observed at ${short}. Visibility at or below 1 km.`,
      triggers: ["visibility", "dbtemp", "rh"] });
  } else if (visM != null && visM <= 4000) {
    const facts = [fact("Visibility", (visM / 1000).toFixed(visM < 1000 ? 1 : 0), "km")];
    if (temp != null) facts.push(fact("Temp", temp, "°C"));
    if (rh != null) facts.push(fact("Humidity", rh, "%"));
    if (rain != null && rain > 0) facts.push(fact("Rain, 24 h", rain, "mm"));
    cards.push({ ...base, id: "vis", sev: "medium", category: "Reduced visibility",
      action: "Allow extra time on the road", facts,
      detail: `Fog reported at ${short}. Visibility below 4 km.`,
      triggers: ["visibility", "dbtemp", "rh", "24hrlyrain"] });
  }

  if (rain != null && rain > 0) {
    const facts = [fact("Rain, 24 h", rain, "mm")];
    if (temp != null) facts.push(fact("Temp", temp, "°C"));
    cards.push({ ...base, id: "rain", sev: "medium", category: "Rain",
      action: "Carry rain gear", facts,
      detail: `Rain observed at ${short} in the last 24 hours.`,
      triggers: ["24hrlyrain", "dbtemp"] });
  }

  // Thunderstorm is read from the held SYNOP sigwx, never from a warning
  // feed we do not hold. Copy names the observation, not a forecast.
  if (station.p.sigwx != null && STORM_SIGWX.includes(station.p.sigwx)) {
    const facts = [fact("Present weather", station.p.sigwx, "")];
    if (wind != null) facts.push(fact("Wind", wind, "m/s"));
    if (rain != null && rain > 0) facts.push(fact("Rain, 24 h", rain, "mm"));
    cards.push({ ...base, id: "storm", sev: "high", category: "Thunderstorm (observed)",
      action: "Stay indoors until it passes", facts,
      detail: `Thunderstorm observed at ${short}. This is a reading, not a forecast.`,
      triggers: ["sigwx", "windsp", "24hrlyrain"] });
  }

  // Ground frost and cold are read from the SYNOP observation, same honesty
  // rule as heat. Frost (≤2 °C) replaces the cold card, never doubles it.

  // Heat is read from the SYNOP observation, never from a warning code we do
  // not hold. Copy names the reading, not a heat-wave declaration.
  if (temp != null && temp >= 40) {
    const facts = [fact("Temp", temp, "°C")];
    if (rh != null) facts.push(fact("Humidity", rh, "%"));
    if (wind != null) facts.push(fact("Wind", wind, "m/s"));
    cards.push({ ...base, id: "heat", sev: "high", category: "Extreme heat (observed)",
      action: "Avoid outdoor exertion 12:00–16:00", facts,
      detail: `Extreme heat observed at ${short}. This is a reading, not a forecast.`,
      triggers: ["dbtemp", "rh", "windsp"] });
  } else if (temp != null && temp >= 37) {
    const facts = [fact("Temp", temp, "°C")];
    if (rh != null) facts.push(fact("Humidity", rh, "%"));
    cards.push({ ...base, id: "heat", sev: "medium", category: "Hot day (observed)",
      action: "Limit midday sun and drink water", facts,
      detail: `Hot conditions observed at ${short}.`,
      triggers: ["dbtemp", "rh"] });
  }

  if (temp != null && temp <= 2) {
    const facts = [fact("Temp", temp, "°C")];
    if (rh != null) facts.push(fact("Humidity", rh, "%"));
    cards.push({ ...base, id: "frost", sev: "high", category: "Ground frost (observed)",
      action: "Protect crops and allow extra time", facts,
      detail: `Ground frost observed at ${short}. This is a reading, not a forecast.`,
      triggers: ["dbtemp", "rh"] });
  } else if (temp != null && temp <= 5) {
    const facts = [fact("Temp", temp, "°C")];
    if (rh != null) facts.push(fact("Humidity", rh, "%"));
    cards.push({ ...base, id: "cold", sev: "high", category: "Cold snap (observed)",
      action: "Layer up and limit early-morning exposure", facts,
      detail: `Cold conditions observed at ${short}. This is a reading, not a forecast.`,
      triggers: ["dbtemp", "rh"] });
  } else if (temp != null && temp <= 10) {
    const facts = [fact("Temp", temp, "°C")];
    if (rh != null) facts.push(fact("Humidity", rh, "%"));
    cards.push({ ...base, id: "cold", sev: "medium", category: "Cold morning (observed)",
      action: "Carry a layer for the morning", facts,
      detail: `Cold morning observed at ${short}.`,
      triggers: ["dbtemp", "rh"] });
  }

  if (cards.length === 0) {
    const facts = [];
    if (temp != null) facts.push(fact("Temp", temp, "°C"));
    if (rh != null) facts.push(fact("Humidity", rh, "%"));
    if (visM != null) facts.push(fact("Visibility", (visM / 1000).toFixed(visM < 1000 ? 1 : 0), "km"));
    cards.push({ ...base, id: "calm", sev: "ok", category: "Clear",
      action: "No action needed today", facts,
      detail: `No action-level signal in the latest observation at ${short}.`,
      triggers: ["dbtemp", "rh", "visibility"] });
  }

  return cards.map((c) => ({ ...c, sevRank: SEV_RANK[c.sev] }));
}

// Gap descriptors: no numbers, ever. `adapters` names which labelled adapters
// produced a value in this bundle ({ aqi: 'cpcb'|'xkdr'|null, uv: 'cams'|null }).
// Null renders the adapter-outage gap (ADR-0002); pollen is always a gap.
function deriveGaps(adapters) {
  const gaps = [{
    id: "gap-pollen", kind: "gap", sev: "ok", sevRank: 0,
    category: "Not published by IMD",
    headline: "Pollen has no number here",
    reason: "IMD does not publish pollen, and no official Indian source exists.",
  }];
  if (!adapters || !adapters.aqi) {
    gaps.push({
      id: "gap-aqi", kind: "gap", sev: "ok", sevRank: 0,
      category: "Adapter unavailable",
      headline: "AQI is unavailable right now",
      reason: "CPCB feed unreachable and no labelled mirror responded, so no value is shown.",
    });
  }
  // Traffic and soil moisture have no IMD or labelled source in the mock —
  // gap cards until ticket 20 lands a labelled adapter.
  if (!adapters || !adapters.traffic) {
    gaps.push({
      id: "gap-traffic", kind: "gap", sev: "ok", sevRank: 0,
      category: "Not published by IMD",
      headline: "Traffic has no number here",
      reason: "IMD does not publish traffic, and no labelled adapter is wired yet.",
    });
  }
  if (!adapters || !adapters.soil) {
    gaps.push({
      id: "gap-soil", kind: "gap", sev: "ok", sevRank: 0,
      category: "Not published by IMD",
      headline: "Soil moisture has no number here",
      reason: "IMD does not publish soil moisture in the reachable feed.",
    });
  }
  return gaps;
}

// Hero selection (PRD Q18): severity → persona weight → recency → id.
function rankStack(items, personaKey) {
  const key = PERSONA_KEYS.includes(personaKey) ? personaKey : "commuter";
  return [...items].sort((a, b) => {
    if (b.sevRank !== a.sevRank) return b.sevRank - a.sevRank;
    const wb = (PERSONA_WEIGHTS[b.id] || {})[key] || 0;
    const wa = (PERSONA_WEIGHTS[a.id] || {})[key] || 0;
    if (wb !== wa) return wb - wa;
    const tb = Date.parse((b.prov && b.prov.issuedUtc) || "") || 0;
    const ta = Date.parse((a.prov && a.prov.issuedUtc) || "") || 0;
    if (tb !== ta) return tb - ta;
    return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
  });
}

// Canonical serialisation: sorted keys, fixed float rendering. Replay asserts
// byte identity on this string (ticket 02, PRD FR-10).
function canonicalize(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map((k) =>
      `${JSON.stringify(k)}:${canonicalize(value[k])}`).join(",")}}`;
  }
  if (typeof value === "number") return JSON.stringify(Math.round(value * 1e6) / 1e6);
  return JSON.stringify(value);
}

// Re-derive the stack from logged inputs and return the canonical string.
// `inputs` is { features, capture, adapters, personaKey, location }.
function replayStack(inputs) {
  const station = nearestStation(inputs.features, inputs.location);
  const cards = deriveCards(station, inputs.capture.captured_at_utc, inputs.capture);
  const gaps = deriveGaps(inputs.adapters);
  return canonicalize(rankStack([...cards, ...gaps], inputs.personaKey));
}

function distanceKm(a, b) {
  const toRad = (d) => (d * Math.PI) / 180;
  const R = 6371;
  const dLat = toRad(b.lat - a.lat);
  const dLon = toRad(b.lon - a.lon);
  const s = Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(a.lat)) * Math.cos(toRad(b.lat)) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(s));
}

function nearestStation(features, location) {
  let best = null;
  for (const f of features) {
    const [lon, lat] = f.geometry.coordinates;
    const d = distanceKm(location, { lat, lon });
    if (!best || d < best.d) best = { d, p: f.properties, lat, lon };
  }
  return best;
}

function ageLabel(issued, captured) {
  const ms = new Date(captured) - new Date(issued);
  if (!isFinite(ms) || ms < 0) return "age unknown";
  const m = Math.round(ms / 60000);
  return m < 60 ? `${m} min ago` : `${Math.floor(m / 60)} h ${m % 60} min ago`;
}

function istTime(iso) {
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  const ist = new Date(d.getTime() + 5.5 * 3600 * 1000);
  const hh = String(ist.getUTCHours()).padStart(2, "0");
  const mm = String(ist.getUTCMinutes()).padStart(2, "0");
  const day = ist.toLocaleDateString("en-IN", { day: "2-digit", month: "short", timeZone: "UTC" });
  return `${day}, ${hh}:${mm} IST`;
}

// Legacy single-card entry (ticket 01 contract): hero for the commuter home.
function deriveCard(station, capturedAt, capture) {
  const ranked = rankStack(deriveCards(station, capturedAt, capture), "commuter");
  const hero = ranked[0];
  return {
    sev: hero.sev, category: hero.category, action: hero.action, facts: hero.facts,
    station: hero.prov.station, issuedUtc: hero.prov.issuedUtc, capturedAt,
    endpoint: hero.prov.endpoint, layer: hero.prov.layer,
  };
}

const API = {
  SEV_RANK, PERSONAS, PERSONA_KEYS, PERSONA_WEIGHTS,
  deriveCards, deriveGaps, rankStack, canonicalize, replayStack,
  distanceKm, nearestStation, ageLabel, istTime, deriveCard,
};
if (typeof module !== "undefined") module.exports = API;
if (typeof window !== "undefined") window.MausamEngine = API;
