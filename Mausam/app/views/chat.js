"use strict";

(function () {
// views/chat.js — Mausam AI: the grounded help layer (PRD v1.2, FR-21–FR-27).
// A bottom-sheet chat over the personal bundle. The engine owns every word
// rule; this file owns the sheet, the quick chips, routine/persona actions,
// and the local-only history. Opened from the home FAB or any card's
// "Ask about this".

const { esc, store, $, $$ } = window.MausamCore;
const { icon } = window.MausamIcons;
const { t } = window.MausamI18n;
const Chat = window.MausamChat;
const Personal = window.MausamPersonal;

const QUICK = ["chat.q1", "chat.q2", "chat.q3"];

function history() { return store.get("chat", []); }
function push(role, text) {
  const h = [...history(), { role, text, at: new Date().toISOString() }].slice(-30);
  store.set("chat", h);
  return h;
}

// Fresh context every turn: cards, window, routines as they are now.
function buildCtx(state, api, seed) {
  const { cards, gaps, hero } = api.ranked();
  const w = api.todayWindow();
  return {
    persona: state.persona,
    hero, cards, gaps, seed: seed || null,
    window: w ? { activity: w.activity, start: w.start, end: w.end, score: w.score } : null,
    routines: store.get("routines", []),
    customs: state.customs,
  };
}

function msgHTML(m) {
  const me = m.role === "me";
  return `<div class="chat__msg${me ? " chat__msg--me" : ""}">
    ${me ? "" : `<span class="chat__avatar">${icon("mark", 16, { sw: 2 })}</span>`}
    <p>${esc(m.text)}</p>
  </div>`;
}

function sheetHTML(state, seed) {
  const T = (k) => t(state.lang, k);
  const log = history().map(msgHTML).join("") ||
    `<p class="mini__text" id="chat-empty">${esc(T("chat.empty"))}</p>`;
  return `<div class="modal__sheet" role="dialog" aria-modal="true" aria-label="${esc(T("chat.title"))}">
    <div class="modal__grab"><span></span></div>
    <div class="modal__head">
      <div>
        <h2 class="modal__title">${esc(T("chat.title"))}</h2>
        <p class="modal__sub">${esc(T("chat.sub"))}</p>
      </div>
      <button class="modal__close" type="button" id="chat-close" aria-label="${esc(T("close"))}">${icon("close", 16, { sw: 2.2 })}</button>
    </div>
    <div class="modal__body chat__log" id="chat-log" aria-live="polite">${log}</div>
    <div class="modal__foot chat__foot">
      <div class="chat__chips">${QUICK.map((k) =>
        `<button class="chip" type="button" data-quick="${esc(T(k))}">${esc(T(k))}</button>`).join("")}</div>
      <form class="chat__form" id="chat-form">
        <label class="sr-only" for="chat-input">${esc(T("chat.ph"))}</label>
        <input class="field" id="chat-input" autocomplete="off" maxlength="200"
          placeholder="${esc(T("chat.ph"))}" aria-label="${esc(T("chat.ph"))}" />
        <button class="btn btn--sm" type="submit" aria-label="${esc(T("chat.send"))}">${icon("send", 15)}</button>
      </form>
      <p class="caption" style="text-align:center">${esc(store.get("groq-key", "") ? T("chat.noteOnline") : T("chat.note"))}</p>
    </div>
  </div>`;
}

function scrollLog() {
  const log = $("#chat-log");
  if (log) log.scrollTop = log.scrollHeight;
}

// Online phrasing (PRD v1.2 FR-23/FR-27): Groq rephrases the grounded reply
// only. The request carries the user's question plus the grounded reply text
// — no bundle data, no location, no identity. The R12 gate runs on the
// result; a failed validation or any network error falls back to the
// template reply silently. Key is user-supplied (BYOK), stored on-device.
const GROQ_MODEL = "qwen/qwen3.8-27b";

async function rephraseOnline(question, grounded) {
  const key = store.get("groq-key", "");
  if (!key) return null;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 12000);
  try {
    const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST", signal: ctrl.signal,
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${key}` },
      body: JSON.stringify({
        model: GROQ_MODEL, temperature: 0, max_tokens: 120,
        messages: [
          { role: "system", content: "Rephrase the ASSISTANT facts briefly in the user's language. Repeat every number exactly. Add no new numbers, facts, or advice." },
          { role: "user", content: `User asked: ${question}\nASSISTANT facts: ${grounded}` },
        ],
      }),
    });
    if (!res.ok) return null;
    const data = await res.json();
    const text = data.choices?.[0]?.message?.content?.trim();
    if (!text) return null;
    return Chat.validateRephrase(grounded, text) ? text : null;
  } catch { return null; } finally { clearTimeout(timer); }
}

function appendMsg(m) {
  const empty = $("#chat-empty");
  if (empty) empty.remove();
  $("#chat-log")?.insertAdjacentHTML("beforeend", msgHTML(m));
  scrollLog();
}

async function runTurn(state, api, text, seed) {
  const clean = String(text || "").trim().slice(0, 200);
  if (!clean) return;
  push("me", clean);
  appendMsg({ role: "me", text: clean });
  const out = Chat.answer(clean, buildCtx(state, api, seed));
  if (out.action?.type === "routine") {
    try {
      const list = Personal.addRoutine(store.get("routines", []) || [],
        { activity: out.action.activity, days: out.action.days, departIST: out.action.departIST }, state.customs);
      store.set("routines", list);
      api.render();
    } catch {
      out.replies = [{ text: "That routine needs a known activity, at least one day, and a HH:MM time." }];
      out.action = null;
    }
  } else if (out.action?.type === "persona") {
    api.setPersona(out.action.key);
  }
  // Template reply first would flash; instead hold one pending bubble and
  // fill it with the online rephrase when it passes the gate, else template.
  const pending = { role: "bot", text: "…" };
  appendMsg(pending);
  const log = $("#chat-log");
  const node = log ? log.lastElementChild : null;
  let finals = out.replies.map((r) => r.text);
  if (store.get("groq-key", "")) {
    const better = await rephraseOnline(clean, out.replies[0].text);
    if (better) finals = [better, ...out.replies.slice(1).map((r) => r.text)];
  }
  if (node) node.querySelector("p").textContent = finals[0];
  push("bot", finals[0]);
  for (const f of finals.slice(1)) {
    push("bot", f);
    appendMsg({ role: "bot", text: f });
  }
  scrollLog();
}

function open(state, api, seed) {
  close();
  const T = (k) => t(state.lang, k);
  const wrap = document.createElement("div");
  wrap.id = "chat-wrap";
  wrap.className = "modal";
  wrap.innerHTML = sheetHTML(state, seed);
  document.body.appendChild(wrap);
  scrollLog();

  $("#chat-close").addEventListener("click", close);
  wrap.addEventListener("click", (e) => { if (e.target === wrap) close(); });
  document.addEventListener("keydown", escClose);
  $$("#chat-wrap [data-quick]").forEach((b) =>
    b.addEventListener("click", () => runTurn(state, api, b.dataset.quick, seed)));
  $("#chat-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const input = $("#chat-input");
    runTurn(state, api, input.value, seed);
    input.value = "";
    input.focus();
  });
  setTimeout(() => $("#chat-input")?.focus(), 60);
  return T;
}

function escClose(e) { if (e.key === "Escape") close(); }

function close() {
  document.getElementById("chat-wrap")?.remove();
  document.removeEventListener("keydown", escClose);
}

// Home FAB. Re-mounted on every home render; removed anywhere else.
function mountFab(state, api) {
  document.getElementById("chat-fab")?.remove();
  if (state.route !== "home") return;
  const T = (k) => t(state.lang, k);
  const fab = document.createElement("button");
  fab.id = "chat-fab";
  fab.className = "fab";
  fab.type = "button";
  fab.setAttribute("aria-label", T("chat.fab"));
  fab.innerHTML = `${icon("chat", 22)}<span>${esc(T("chat.fab"))}</span>`;
  fab.addEventListener("click", () => open(state, api, null));
  document.body.appendChild(fab);
}

const ChatView = { open, close, mountFab, buildCtx };
if (typeof window !== "undefined") window.MausamChatView = ChatView;
})();
