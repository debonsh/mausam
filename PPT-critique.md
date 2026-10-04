# SIH26076 Mausam Deck: Ruthless Evaluation

**Deck evaluated:** `mausam PPT/SIH26076-Mausam-FINAL.pdf` (6 pages, built by `mausam PPT/build_deck.py`)
**Template source:** `mausam PPT/SIH2026-IDEA-Presentation-Format.pptx`
**Evaluated against:** SIH 2026 six-slide rules, SIH26076 PRD, `blueprint/content-02.md`

---

## VERDICT

The deck is **structurally compliant and factually honest, but visually broken in three places and it never shows the product.** A judge spends 45 seconds on this. Right now they see: a glitched title page, a hand-drawn phone with a blank navy rectangle where the map should be, three grids of rounded boxes, and an empty top half on the references slide. Your actual work (30+ real screenshots, a green 32-test suite, a working offline PWA) is sitting in `Mausam/docs/evidence/` unused.

Two of the four visual defects are **bugs in `mausam PPT/build_deck.py`**, not taste problems. Verified by rendering and pixel-sampling the PDF.

---

## SIH COMPLIANCE CHECK

| Requirement | Status | Note |
|---|---|---|
| 6 slides max, instruction slide dropped | PASS | `drop_instruction_slide()` removes slide7; PDF is 6 pages |
| S1 = Title Page | PASS | |
| S2 = Idea / Proposed Solution | PASS | |
| S3 = Technical Approach | PASS | |
| S4 = Feasibility & Viability | PASS | |
| S5 = Impact & Benefits | PASS | |
| S6 = Research & References | PASS | |
| S1 pointers (PS ID / Title / Theme / Category / Team ID / Team Name) | **FAIL** | Title bullet collides with the amber bar; Team ID and Team Name overflow off the slide bottom |
| S2 pointers (Proposed Solution / Detailed explanation / How it addresses / Innovation) | PASS | exact wording preserved |
| S3 pointers (Technologies / Methodology) | PASS | |
| S4 pointers (Analysis / Challenges & risks / Strategies) | PASS | |
| S5 pointers (Potential impact / Benefits) | PASS | |
| S6 pointers (Details / Links of reference) | PASS | |
| "Avoid paragraphs, use points/diagrams" | PASS | |
| Save as PDF | PASS | |
| Team Name filled in | **FAIL** | `[Team Name]` placeholder still in the oval on slides 2-6; slide 1 Team ID/Team Name unfilled |

**Bottom line: do not upload until slide 1 renders correctly and the team fields are filled.**

---

## MAUSAM CHECK

| Ask | Verdict | Evidence in deck |
|---|---|---|
| Weather information discovery | Weak | "map on top, action cards below" is a sentence, not a picture |
| Warning visibility | **Good** | "District warning: fog after 22:00" shown in the mock |
| Forecast comprehension | **Missing** | No hourly/24h strip, no forecast anywhere |
| Map / data visualization | **Claimed, not shown** | The mock's "map" is a flat navy rectangle with no map |
| Accessibility | **Missing** | Zero mention. PRD NFRs cover it; judges ask about India-scale a11y |
| Multilingual | Underplayed | One "EN/HI" token in a tech box; one "in Hindi" on slide 5 |
| Location-based info | Missing | Onboarding / saved places never appear |
| User experience | Weak | The only product visual is a crude shape mock |
| Public platform, not generic weather app | **Partially** | The provenance/replay/gap thesis is the right answer, but stated in 9pt type, never demonstrated |

**Does it genuinely solve the problem?** The idea does. The deck does not communicate it. Your own blueprint has the line that should be on slide 2 verbatim:

> Every number on this screen can tell you where it came from, when it was issued, and how old it is, and every advisory can be re-derived by hand.

It appears nowhere in the deck.

**Persona mismatch across slides:** slide 2 shows `Commuter · Farmer · Health` (your three deep personas, correct). Slide 5 shows `Citizens · Farmers · Travellers · Fishermen · Emergency users`, none of which are PRD personas except Farmers. A judge who reads both slides sees two different products.

---

## PER-SLIDE SCORECARD (1-10)

| Criterion | S1 | S2 | S3 | S4 | S5 | S6 |
|---|---|---|---|---|---|---|
| Immediate clarity | 2 | 7 | 8 | 7 | 6 | 4 |
| Problem understanding | 3 | 7 | 6 | 6 | 5 | 5 |
| Solution clarity | 1 | 7 | 8 | 6 | 4 | 3 |
| Innovation | 1 | 6 | 7 | 5 | 4 | 4 |
| Technical credibility | 1 | 6 | 8 | 7 | 4 | 7 |
| Feasibility | 1 | 6 | 7 | **8** | 5 | 6 |
| Impact | 1 | 6 | 5 | 5 | **5** | 3 |
| Research credibility | 1 | 5 | 6 | 6 | 5 | **7** |
| Visual hierarchy | 2 | 7 | 7 | 7 | 6 | 3 |
| Readability | 2 | 7 | **4** | 8 | **5** | 6 |
| Judge appeal | 2 | 7 | 7 | 7 | 5 | 4 |

---

## VISUAL CRITIQUE

### SLIDE 1 (Title Page): the worst slide in the deck

**WHAT WORKS:** Official SIH branding intact. All six required fields present in the source.

**WHAT IS WEAK:** The stock brain/lightbulb graphic owns 40% of the canvas. Your own idea title is 20pt while the template bullet is 24pt. Hierarchy is inverted: the template's filler beats your pitch.

**WHAT IS CONFUSING:** Three simultaneous layout failures:

1. `Personalised homepage for the` renders with justified rivers of whitespace, wraps to `Mausam mobile application`, and the amber accent bar lands **directly on top of it**. It reads as a strikethrough.
2. `Team ID – [as registered on the` is cut mid-sentence at the slide edge.
3. `Team Name – [to be filled before upload]` is pushed entirely off-slide (visible as a clipped fragment bottom-left).

Root cause: `slide1()` places the accent bar at fixed `y=4.80` assuming the template's PS Title field ends at y=4.6. It does not. The field wraps to a second line at y~4.8.

**WHAT SHOULD BE REMOVED:** The stock brain hexagon. The standalone "TITLE PAGE" heading (template scaffolding, not content).

**WHAT SHOULD BE EMPHASIZED:** Your idea name. It should be the single largest element after "SMART INDIA HACKATHON 2026".

**WHAT SHOULD BECOME A UI/MOCKUP:** The right 40% should hold **one real product screenshot**. `docs/evidence/mobile-home.png` or `ticket-01-home.png` already exists at 1280px.

---

### SLIDE 2 (Idea): strongest slide, biggest missed opportunity

**WHAT WORKS:** Three-column structure (pointers | product | differentiators) is correct. The "WHAT IS DIFFERENT" cards are the right idea. Pointer wording is exact. Content is genuinely specific ("Leave 20 min early", "visibility 400 m", "IMD · stn 573 · 2 h old").

**WHAT IS WEAK:**

- The phone's map is a **flat navy rectangle**. You claim "map on top" and show no map. That single gap undermines the whole slide.
- The white action card is 2.72in tall with 4 lines of text: **~60% of it is empty white.**
- The green ellipse pill `Ask · routine help · card explainer` floats below the cards, attached to nothing.
- Left column: the 10pt bold navy pointer labels and the 12pt body are too close in weight. Labels read as body text.

**WHAT IS CONFUSING:** The four "different" cards are visually identical, so nothing is *the* differentiator. The hook (provenance toggle) and the depth (replay) are given the same weight as a chatbot feature.

**WHAT SHOULD BE REMOVED:** The floating green pill. The empty white space in the phone card.

**WHAT SHOULD BE EMPHASIZED:** **Source on every number.** Make it 2x the size of the other three, put it first, and give it a visual.

**WHAT SHOULD BECOME A UI/MOCKUP:** The entire center column. Replace the shape mock with two real screenshots side by side:

- `ticket-01-home.png` (home, provenance visible)
- `ticket-04-provenance.png` (provenance sheet expanded)

**WHAT SHOULD BECOME A DIAGRAM:** A three-beat before/after strip: `number on screen → tap ⓘ → source · station · issue time · age`. Three tiny frames. This is your 10-second demo in a still image.

**WHAT SHOULD BE REARRANGED:** Put the hook card full-width across the bottom third, under all three columns, with a 20pt headline. Right now the hook is card #1 of 4, at 11pt.

---

### SLIDE 3 (Technical Approach): best diagram, broken text

**WHAT WORKS:** The 6-stage pipeline (IMD DATA → GATEWAY → FUSION → INTELLIGENCE → BACKEND → HOMEPAGE) is exactly the right shape. The green "AI only where justified" callout answers the judge's "why is AI here" question before they ask. "32 tests green" is verifiable: the suite runs 6+4+3+3+2+6+8 = **32 passing**. Tech stack line is concrete.

**WHAT IS WEAK / CONFUSING:**

- **The pipeline box text renders BLACK, not white.** Pixel-sampled from the rendered PDF: box 1 fill is `#003366`, glyph pixels are `#000A14`. Contrast ≈ **1.5:1 against a 4.5:1 requirement.** "IMD DATA / 28 keyed APIs / WFS · CAP feed" is effectively unreadable on the two navy boxes. Boxes 2-5 sit at ~5.2:1, legible but muddy.
- **All text is left-aligned despite `alg="ctr"`.** Every box has a dead right half.
- The AI callout is centered in an 8.15in box but the tech line above it is left-aligned. Two competing alignments in one column.
- The methodology sentence is a single 27-word line. The template asks for a flow chart; you have prose where a flow chart belongs.

**WHAT SHOULD BE REMOVED:** The methodology paragraph as prose. The stray vertical gap between the AI callout (ends y=5.30) and the Methodology pointer (y=5.62).

**WHAT SHOULD BE EMPHASIZED:** The two things that are actually hard: **static-IP gateway with hourly JWT** (your critical path) and **replay** (your differentiator). Neither is visually flagged. Mark them with an accent border or a star.

**WHAT SHOULD BECOME A DIAGRAM:**

1. The methodology line becomes a **3-node timeline**: `Mock (today, 32 tests on captured payloads) → Live keyed pipeline → Finale (3 deep personas, push, labelled adapters)`.
2. Add a small **replay loop diagram**: `logged inputs → rule chain → byte-identical card ↺`. This is the claim you make twice and never draw.

**WHAT SHOULD BECOME A UI/MOCKUP:** The template explicitly permits "working prototype" under the Methodology pointer. Put `ticket-02-engine-hero.png` in the empty band at y 4.0-5.5, right side.

**WHAT SHOULD BE REARRANGED:** Pipeline stays at top. Tech stack becomes chips directly under the pipeline (not a floating line). AI callout moves to the right of the replay diagram as a paired "what AI does / what AI never does" two-up.

---

### SLIDE 4 (Feasibility): clean but incomplete and half-empty

**WHAT WORKS:** Risk → arrow → strategy is the correct pattern and it is executed consistently. Red border = risk, green border = fix, semantically right. Every claim is concrete and defensible. "32 tests green" repeated with the offline claim.

**WHAT IS WEAK:** The bottom **~28% of the slide is empty**, and each 0.90in-tall box holds one line of 11pt text, so the boxes themselves are ~50% air.

**WHAT IS CONFUSING:** The header says "FEASIBILITY **AND VIABILITY**" but there is **zero viability content**: no hosting model, no cost, no data licence, no who-runs-it, no rollout. The pointer "Analysis of the feasibility of the idea" is answered; "viability" is not.

**WHAT SHOULD BE REMOVED:** Nothing. This is the slide with the least waste, apart from the empty band.

**WHAT SHOULD BE EMPHASIZED:** "Each risk below has a working fallback" is your thesis here. Bold it.

**WHAT SHOULD BE A DIAGRAM:** A **feasibility timeline** in the empty bottom band: `Day 1: static-IP host + key registration` (the critical path, per your own blueprint) → `Week 1: captured-payload mock (done)` → `Week 3: live keyed pipeline` → `Finale: demo`. Judges reward knowing the critical path.

**WHAT SHOULD BECOME CONTENT (new):** A fourth row or a small "Viability" strip: single container + static host, one IMD API account (2 DEV + 2 PROD keys, per the portal guide), no user behavioural tracking, maintained by the team with an attribution ledger.

---

### SLIDE 5 (Impact): the weakest content slide

**WHAT WORKS:** Clean left → right structure. Amber arrows carry the template's accent colour. "No invented statistics" is honest and matches your no-fabrication principle.

**WHAT IS WEAK:**

- **The outcomes are filler.** "Faster discovery", "Better understanding", "Earlier action", "Public safety" are generic, interchangeable, and could be pasted onto any app. "Fishermen → Works offline + in Hindi" is a feature, not an impact. "Emergency users → Public safety" is a tautology.
- **Persona list contradicts slide 2.** Citizens/Fishermen/Emergency users are not PRD personas.
- Every left box renders **black text on navy (1.7:1 contrast)** and left-aligned inside a box designed for centered text, so the right 70% of each navy bar is empty.
- Right side of the slide beyond x=12.65in is empty; the "Benefits" pointer answer is two lines jammed at the bottom.

**WHAT IS CONFUSING:** Whether the audience is the Mausam app's eight personas or a generic Indian population.

**WHAT SHOULD BE REMOVED:** "Better understanding". "Faster discovery". Both say nothing. "Citizens" and "Emergency users".

**WHAT SHOULD BE EMPHASIZED:** Make this the **measurable impact** slide, because your own line is the strongest sentence on it: *"can users state the action, how fast, does every card replay."* That is a testable claim. Elevate it.

**WHAT SHOULD BECOME A DIAGRAM:** Replace the 5-row arrow grid with a **persona → action → measurable outcome matrix**, three rows matching your deep personas:

| Persona | Sees first | We measure |
|---|---|---|
| Commuter | Fog window + "leave 20 min early" | time to state the action |
| Farmer | Agromet + sowing window | card opened → action recalled |
| Health | Heat + AQI gap card | % who notice "no pollen" is a gap, not a zero |

No invented numbers, only named measurements. That is stronger than five vague arrows and it answers "Benefits of the solution" honestly.

**WHAT SHOULD BECOME A UI/MOCKUP:** One screenshot of the **offline + Hindi state** (`ticket-21-onboarding-language-hi.png` or `ticket-01-home-offline.png`) to back the "Works offline + in Hindi" claim visually.

---

### SLIDE 6 (References): visually broken, content thin

**WHAT WORKS:** Six references, five external, one internal. Sources are real and verifiable: `api.imd.gov.in`, `data.gov.in`, `ads.atmosphere.copernicus.eu`, `ux4g.gov.in`, `pib.gov.in`, Pai et al. 2014. All check out against the blueprint.

**WHAT IS WEAK:** The entire **top ~50% of the slide is blank**. The template's pointer bullet sits at y≈3.3in because `slide6()` only appends rows starting at y=3.85 and never repositions the inherited bullet. The bullet itself renders at roughly 24pt, larger than your reference text, so the loudest thing on the slide is template scaffolding.

**WHAT IS CONFUSING:** Reference 6 points at `Mausam/app · docs/evidence`, a local folder. A judge cannot open it. It reads as "trust us".

**WHAT SHOULD BE REMOVED:** The oversized template bullet as a visual anchor (keep the exact wording, shrink and reposition it).

**WHAT SHOULD BE EMPHASIZED:** Reference 6. Your working mock is your strongest credibility asset and it is the last, smallest, least clickable item.

**WHAT SHOULD BECOME A DIAGRAM:** A **4-tile source map** at the top: `IMD (official, keyed)` · `CPCB (official, labelled adapter)` · `Copernicus (official, labelled)` · `MeitY UX4G (design standard)`, with a fifth tile `Our work (mock · 32 tests · replay)`. Instantly answers "is this research-backed or invented".

**WHAT SHOULD BECOME NEW CONTENT:** A **QR code to the running mock** plus a public URL. Also add: the Mausam app itself and its existing Damini/Meghdoot modules (proves you know what already ships), and the IMD CAP/public warning feed.

---

## BENCHMARK vs STRONG SIH DECKS

| Strong-deck pattern | This deck |
|---|---|
| One large product screenshot per key slide | **0 real screenshots used** |
| Architecture as a labelled diagram | Yes, slide 3, but text is unreadable on 2 of 6 boxes |
| Innovation shown, not described | Described in 9-11pt text only |
| Concrete, checkable numbers | **Yes**: 28 APIs, 32 tests, 15 KB bundle, hourly JWT (verified) |
| Visible prototype + QR to live demo | Missing |
| One memorable sentence a judge repeats | Missing (your blueprint already wrote it) |
| Concise, no paragraph walls | Passes |
| Consistent persona story across slides | **Fails**: slide 2 vs slide 5 disagree |

You beat the field on **honesty and verifiability**. You lose on **showing**. Strong SIH decks are remembered because the judge saw the product; this one is read.

---

## CRITICAL FIXES

### 1. Fix the two rendering bugs in `build_deck.py` before anything else

- **SLIDE:** 3, 5 (and anywhere `WHITE`/`NAVY`/`GREY`/`alg="ctr"` is used)
- **PROBLEM:** `run()` emits `<a:solidFill>` **after** `<a:latin>/<a:ea>/<a:cs>`. ECMA-376 requires fill before latin. The renderer drops the fill and falls back to black. Separately, `para()` writes `alg="ctr"` but the DrawingML attribute is **`algn`**, and `spc` is not a valid `pPr` attribute. Every centred, non-black run in the deck silently loses its formatting. Black on `#003366` = **1.7:1 contrast, WCAG AA fail**. Invalid `rPr` child order also risks PowerPoint flagging the file as needing repair.
- **CHANGE:** In `run()`, emit `<a:solidFill>` immediately after the attributes and before `<a:latin>`. In `para()`, rename `alg=` to `algn=` and drop `spc=`.
- **NEW VISUAL:** Pipeline boxes and persona boxes render white-on-navy as designed, centred, readable from the back of the room.
- **NEW CONTENT:** none (pure fix).

### 2. Slide 1: stop the collision and the overflow

- **SLIDE:** 1
- **PROBLEM:** The PS Title field wraps to a second line; the amber bar at `y=4.80` strikes through it. Team ID truncates at the slide edge; Team Name is pushed off-slide entirely. First impression is a broken document.
- **CHANGE:** Measure the actual rendered extent of the template field block after the text substitution, then place the accent bar and idea title below it (or delete the bar and put the idea title in the right column). Reduce the PS Title run size so it fits one line. Move Team ID / Team Name into a compact single row that fits inside the canvas.
- **NEW VISUAL:** Right 40% = one real product screenshot instead of the stock brain hexagon. Left column = fields in a tight vertical stack.
- **NEW CONTENT:** `Idea: Mausam home: actions with proof` set at 28-32pt, larger than every template bullet, plus the one-liner: *"Every number shows its source, station, issue time and age. Every advisory can be re-derived by hand."*

### 3. Slide 2: replace the fake phone with real screenshots

- **SLIDE:** 2
- **PROBLEM:** The "map on top" claim is rendered as an empty navy rectangle. The action card is 60% white space. A judge who sees no map stops believing the sentence above it. Meanwhile 30 real PNGs sit in `Mausam/docs/evidence/`.
- **CHANGE:** Delete the shape-built phone entirely. Insert `ticket-01-home.png` and `ticket-04-provenance.png` as two framed screenshots with a `before → tap ⓘ → after` caption strip.
- **NEW VISUAL:** Two real 1280px screenshots in phone-shaped frames, plus a 3-frame provenance micro-diagram (`34°C` → tap → `IMD SYNOP · New Delhi-Safdarjung · issued 02 Oct 23:38 IST · 2 h 38 min old`).
- **NEW CONTENT:** Left column stays as-is (pointer wording is correct). Right column collapses from 4 equal cards to **1 hero + 2 support**: hero = `Source on every number` at 16pt with a screenshot thumbnail; support = `Replayable advice` and `Honest gaps`. Move `Grounded chatbot` to slide 3 next to the AI callout.

### 4. Slide 6: fill the top half

- **SLIDE:** 6
- **PROBLEM:** Content starts at y=3.85 of a 5.0in canvas. The top 50% is blank and the loudest element is the template's own 24pt bullet. It looks unfinished.
- **CHANGE:** Reposition the inherited bullet to y=1.22 (matching slides 2-5) and start the reference rows at y=1.85. Rows at 0.44in pitch fill to y≈4.5.
- **NEW VISUAL:** Four source-category tiles across the top (IMD / CPCB / Copernicus / MeitY), reference list beneath, **QR code bottom-right** pointing at the running mock.
- **NEW CONTENT:** `7. Mausam app: existing Damini lightning + Meghdoot crop modules (what already ships, not our novelty): mausam.imd.gov.in`. Replace `Mausam/app · docs/evidence` with a public URL plus the QR.

---

## HIGH-IMPACT FIXES

### 5. Slide 5: rewrite the outcomes, fix the persona contradiction

- **SLIDE:** 5
- **PROBLEM:** "Faster discovery / Better understanding / Earlier action / Public safety" are interchangeable filler. Fishermen gets a feature as an impact. The audience list contradicts slide 2's Commuter/Farmer/Health chips, so the deck tells two different stories.
- **CHANGE:** Rebuild as a 3-row matrix using your deep personas, each row = persona | what they see first | what we measure in the pilot.
- **NEW VISUAL:** 3 wide rows instead of 5 thin ones, plus one screenshot (`ticket-21-onboarding-language-hi.png`) proving offline + Hindi.
- **NEW CONTENT:** Commuter → `Leave 20 min early` → *time to state the action*. Farmer → `Sowing window, rainfall vs normal` → *action recalled after 5 min*. Health → `Heat card + "IMD does not publish pollen"` → *% who read the gap as a gap, not a zero*. Footer keeps your best line: `No invented statistics. Impact is measured in the pilot.`

### 6. Slide 3: make the methodology a diagram and flag the critical path

- **SLIDE:** 3
- **PROBLEM:** The template literally asks for "Flow Charts / Images / working prototype" and you answered with one 27-word sentence. Your critical path (static-IP gateway, hourly JWT) and your differentiator (replay) are drawn with the same weight as everything else.
- **CHANGE:** Convert the methodology line into a horizontal 3-stage timeline. Add a compact `logged inputs → rules → identical card ↺` loop. Star the GATEWAY box. Place a real prototype screenshot in the empty band.
- **NEW VISUAL:** Timeline diagram + replay loop + `ticket-02-engine-hero.png` thumbnail with caption `replay reproduces this card byte-identically`.
- **NEW CONTENT:** `Day 1 (critical path): register key, bind static IP, refresh JWT hourly.` Judges reward teams that name their own risk.

### 7. Slide 4: answer "viability", not just feasibility

- **SLIDE:** 4
- **PROBLEM:** Header promises VIABILITY. Slide delivers only risk register. Bottom 28% is empty.
- **CHANGE:** Keep the 4 risk rows (they are good), tighten box heights to 0.70in, and use the freed space for a timeline + a 3-item viability strip.
- **NEW VISUAL:** `Day 1 → Week 1 → Week 3 → Finale` timeline across the bottom.
- **NEW CONTENT:** `Host: one container on a static-IP VM. Data: IMD keyed API (2 DEV + 2 PROD keys, attribution ledger on request). Cost: no paid services. Licence: IMD data with attribution; CPCB/CAMS labelled adapters.`

### 8. Put the memorability hook in writing

- **SLIDE:** 2 (primary), 1 (secondary)
- **PROBLEM:** Your blueprint's JUDGE NOTE is the sentence you want repeated in the judging room. It is not in the deck.
- **CHANGE:** Add it as the closing band of slide 2, 14-16pt, navy on light, full width.
- **NEW VISUAL:** A full-width banner under the three columns, visually distinct from the cards.
- **NEW CONTENT:** `Every number on this screen can tell you where it came from, when it was issued, and how old it is. Every advisory can be re-derived by hand. No weather app in India does that, including the current one.`

### 9. Add accessibility and multilingual evidence

- **SLIDE:** 3 (tech) or 5 (impact)
- **PROBLEM:** For an India-scale public weather platform, a11y and multilingual are the two things an IMD/MeitY judge will ask about, and the deck has one "EN/HI" token and zero a11y mentions.
- **CHANGE:** Add two chips to the HOMEPAGE pipeline box and one line to the benefits block.
- **NEW VISUAL:** Two chips under the pipeline: `WCAG AA · keyboard · forced-colors` and `EN · HI · Noto Indic`.
- **NEW CONTENT:** `Warning text is human-reviewed, never raw machine translation.` (You already decided this in the PRD; it is a strong, non-obvious claim.)

---

## POLISH

**10.** **SLIDE:** 2 · **PROBLEM:** floating green pill `Ask · routine help · card explainer` is attached to nothing · **CHANGE:** delete it, or dock it to the bottom edge of the phone frame as a real bottom bar · **NEW VISUAL:** pill becomes part of the device chrome · **NEW CONTENT:** none.

**11.** **SLIDE:** 2 · **PROBLEM:** pointer labels at 10pt bold navy vs body at 12pt: hierarchy too close · **CHANGE:** labels to 9pt uppercase navy with 0.06in gap; body to 12.5pt · **NEW VISUAL:** clear label/body rhythm down the left column · **NEW CONTENT:** none.

**12.** **SLIDE:** 3 · **PROBLEM:** tech stack is a floating centred line with no owner · **CHANGE:** turn into 5 chips directly beneath the pipeline, each under its stage where it applies · **NEW VISUAL:** chip row aligned to the boxes above · **NEW CONTENT:** none.

**13.** **SLIDE:** 4 · **PROBLEM:** boxes are 0.90in tall for one 11pt line · **CHANGE:** 0.66in, tighten pitch from 1.02 to 0.78 · **NEW VISUAL:** tighter grid, more room for the timeline · **NEW CONTENT:** none.

**14.** **SLIDE:** 6 · **PROBLEM:** "published dataset" and "PIB Mausam note" are vague · **CHANGE:** give full titles and years · **NEW VISUAL:** two-line refs with the URL in accent colour · **NEW CONTENT:** `Pai, N. et al. (2014), IMD Pune gridded rainfall 0.25°, 1901-2010`. `PIB (2023), Mausam mobile application press note`.

**15.** **SLIDE:** all · **PROBLEM:** `[Team Name]` placeholder in the oval on 2-6; Team ID/Team Name unfilled on 1 · **CHANGE:** fill both before export · **NEW VISUAL:** real team identity · **NEW CONTENT:** registered team name and portal ID.

**16.** **SLIDE:** 1 · **PROBLEM:** "TITLE PAGE" heading is template scaffolding competing with your idea · **CHANGE:** if the template allows, replace the heading text with the idea name; otherwise leave it but make your idea title 2x its size · **NEW VISUAL:** idea name dominates the left column · **NEW CONTENT:** none.

**17.** **SLIDE:** 3 · **PROBLEM:** two competing alignments in one column (centred AI box, left tech line) · **CHANGE:** once bug #1 is fixed, centre both, or left-align both · **NEW VISUAL:** single alignment axis · **NEW CONTENT:** none.

---

## FIX ORDER (highest judge impact per unit effort)

1. **Bug fix in `run()`/`para()`** (fixes contrast on slides 3 + 5 and every alignment in the deck; ~6 lines)
2. **Slide 1 collision + overflow** (your first impression is currently broken)
3. **Real screenshots on slide 2** (the single biggest credibility gain; assets already exist)
4. **Slide 6 top-half fill + demo QR**
5. **Slide 5 persona rewrite**
6. **Slide 3 methodology diagram + critical-path flag**
7. **Slide 4 viability strip**
8. **The hook banner**
9. Polish items 10-17

Fixes 1-4 take an afternoon and move you from "reads like a text submission" to "shows a working product". Fixes 5-8 are what separate a top-5 finish from the middle of the pack.

---

## APPENDIX: VERIFIED CLAIMS IN THE DECK

| Claim | Status | How checked |
|---|---|---|
| "32 tests green" | **TRUE** | Ran `node tests/*.test.js`: deep-personas 6, engine 4, i18n 3, offline 3, onboarding 2, personal 6, windows 8 = 32 |
| "28 keyed APIs" | **TRUE** | Matches `blueprint/content-02.md` IMD portal guide |
| Key = static IP + hourly JWT | **TRUE** | Matches `blueprint/content-02.md` §4.6 (verified from portal user guide) |
| Pai et al. 2014 gridded rainfall | **TRUE** | Real IMD Pune dataset, cited in PRD references |
| `api.imd.gov.in`, `data.gov.in`, `ads.atmosphere.copernicus.eu`, `ux4g.gov.in`, `pib.gov.in` | **TRUE** | All real, all cited in the blueprint |
| Pipeline text contrast | **FAIL** | Pixel-sampled PDF: fill `#003366`, glyphs `#000A14` = ~1.5:1 (needs 4.5:1) |
| Centered text in boxes | **FAIL** | Pixel-sampled slide 5: "Citizens" left-aligned in a box coded `alg="ctr"` |
| White text on navy boxes | **FAIL** | Pixel-sampled slide 5: "Citizens" renders black on `#003366` |
| Real screenshots available | **TRUE** | 30+ PNGs in `Mausam/docs/evidence/`, zero used in the deck |
