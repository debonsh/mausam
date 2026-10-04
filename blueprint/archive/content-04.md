
## 6. PS4 — SIH26138 — SEAWARD: the CII-Aware Green Fleet Optimizer

**One-line pitch:** A physics-grounded, quantum-inspired fleet optimiser that predicts fuel honestly, optimises for the regulation that actually bites — the IMO Carbon Intensity Indicator — and shows you the year your "optimal" fleet becomes illegal.

### 6.1 Problem, and why the obvious answer fails

Maritime fuel is a high-dimensional, non-linear, multi-objective problem: vessel type × capacity × speed × weather × fuel × schedule × regulation. The generic answer — "XGBoost predicts fuel, a genetic algorithm picks ships" — fails three ways: (1) a black-box fuel model cannot extrapolate to a vessel/speed it hasn't seen, which is precisely what fleet planning asks; (2) optimising fuel without the CII rating optimises the wrong objective — a D-rated "efficient" fleet is a compliance failure; (3) "quantum-inspired" without a classical baseline is marketing. Egreen Quanta already talks digital twins and scenario simulation publicly — so a twin alone is table stakes for *this* judge, not a differentiator.

### 6.2 What other teams will probably build

- An LSTM fuel predictor trained on a CSV of unknown provenance, evaluated with R² and no residuals analysis.
- A "quantum genetic algorithm" with no baseline comparison and no statement of what is quantum about it.
- A vessel-tracking dashboard with CO₂ totals — reporting, not optimisation.

### 6.3 How SEAWARD is different

Four mechanisms, each aimed at a real judge objection:

1. **Physics backbone + ML residuals.** Implement the propulsion power balance honestly: calm-water power from a fitted hull curve (cubic-dominated with documented residual term), plus added-resistance terms for wind/waves/fouling/trim, auxiliary loads, and fuel-specific conversion. Fit a *small* set of physically meaningful parameters per vessel class; gradient boosting learns **only the residuals**. Result: a model that extrapolates to unseen speeds/vessels (physics carries it), degrades gracefully, and is explainable parameter by parameter. **This is the technical heart of the solution.**
2. **CII-native optimisation.** Implement the actual regulation: attained CII = M/W with M = Σ fuel×CF and W = capacity×distance (DWT×nm proxy), A–E bands with tightening reduction factors as configurable inputs, E/D-triggered corrective-action logic, and the in-port vs underway + shore-power structure of the enhanced-granularity era. The optimiser maximises fleet utility subject to **rating constraints**, and the benchmark reports rating outcomes, not just tonnes saved.
3. **Honest quantum-inspired optimisation with an exact baseline.** Implement a real quantum-inspired metaheuristic (population with superposition-inspired state encoding and rotation-gate updates — stated plainly as classical code) for the fleet-mix/speed problem, formulated multi-objective (fuel, lifecycle CO₂e, cost, reliability, CII) with a Pareto front — and **solve small instances to optimality with MILP** to show the metaheuristic's gap. The benchmark table the PS demands (accuracy, convergence, quality, scalability) is then credible: conventional = MILP/GA/PSO, proposed = QI-metaheuristic, metrics measured on the same simulator.
4. **The Regulatory-Cliff Scenario Deck.** A timeline slider 2024→2035 with tightening CII factors: today's optimal mix visibly slides into D/E territory, and the system re-optimises — newbuild/retrofit, fuel switch (LNG/methanol/ammonia/hydrogen with lifecycle factors), shore-power berths, slow-steaming — showing capex vs compliance per scenario. **This is the WOW moment**: *"Your optimal 2026 fleet is non-compliant by 2030. Here is the cheapest compliant one."*

Data honesty is load-bearing: ship-level DCS data is anonymised and unavailable, so SEAWARD ships with a **documented physics-based voyage simulator** (public engine/fleet particulars, configurable weather, stated distributions) as the training and benchmark ground — and a data-request path to MPA's non-sensitive operational datasets under the July 2026 agreement. The simulator is a feature (reproducible benchmarks), not an embarrassment.

> **JUDGE NOTE (PS4):** "We don't predict fuel with a black box and we don't claim quantum magic. Physics predicts, ML corrects, MILP verifies, the regulation decides — and we can show you all four on one screen."

### 6.4 Objectives coverage (the PS's five, answered)

Prediction → physics+residual model per vessel class/condition. Fleet-mix/speed optimisation → QI-metaheuristic over vessel×capacity×speed with alternative-fuel and shore-power variables. Minimise fuel/cost/lifecycle GHG → Pareto front across all three, lifecycle factors explicit. Demand/reliability/compliance → hard constraints + CII-rating constraints + schedule buffers. Benchmarking → simulator-based harness: MILP (exact, small), GA, PSO vs QI method on accuracy/convergence/quality/scale.

### 6.5 AI/ML + optimisation components — with the "why" answered

| Component | Method | Why this / metric |
|---|---|---|
| Fuel model (backbone) | Parametric propulsion balance, fitted per class | Extrapolation + explainability; metric: RMSE + residual bias by speed bin |
| Residual corrector | Gradient boosting on residuals | Captures fouling/weather/trim effects physics misses; metric: residual RMSE, ablation vs backbone-only |
| Fleet optimiser | QI population metaheuristic (rotation-gate updates), multi-objective NSGA-style ranking | Global search on non-convex mix problem; metric: hypervolume + gap-to-MILP on small instances |
| Baselines | MILP (exact), GA, PSO | Credibility; metric: same harness, same seeds |
| Speed/policy layer | Per-voyage speed optimisation under CII budget | Operationalises the rating; metric: rating attainment per scenario |
| Shore-power/fuel-switch | Scenario variables with lifecycle CO₂e + cost | Decision support; metric: ₹/tonne-CO₂e- avoided per scenario |

### 6.6 System architecture

<div class="arch">
<div class="abox">Voyage simulator<br><span>physics ground truth · documented distributions</span></div>
<div class="aarrow">→</div>
<div class="abox">Fuel model<br><span>parametric backbone + residual ML</span></div>
<div class="aarrow">→</div>
<div class="abox">CII engine<br><span>M/W · A–E · tightening factors</span></div>
<div class="aarrow">→</div>
<div class="abox">QI optimiser<br><span>mix × speed × fuel · Pareto front</span></div>
<div class="aarrow">→</div>
<div class="abox">Scenario deck<br><span>cliff slider · capex vs compliance</span></div>
</div>

**Frontend:** React + Leaflet voyage/risk maps (no token), Pareto scatter, Gantt-style schedules, cliff-timeline visualisation. **Backend:** Python (NumPy/SciPy) optimisation service + FastAPI; Postgres for fleet/scenario store; job queue for long optimisations with progress streaming. **Data:** simulator-first; public particulars where citable; MPA-request path documented. **Infra:** containerised; deterministic seeds everywhere (every benchmark reproducible); results export for the case-study writeup the PS asks for.

### 6.7 Demo script + WOW + PPT

0:00–0:20 problem (fuel = cost + emissions + compliance risk); 0:20–0:40 why black-box + dashboard fail (show an LSTM confidently wrong outside its speed range — physics carries ours); 0:40–1:00 SEAWARD + physics→ML→MILP→CII chain; 1:00–3:30 live: load fleet, run optimisation, Pareto front appears, benchmark table fills (QI vs GA/PSO/MILP-gap); **WOW: drag the regulatory-cliff slider to 2030 — the fleet's ratings collapse to D/E, then hit re-optimise and watch the compliant mix (fuel switch + slow-steam + shore power) emerge with capex and ₹/tCO₂e**; 3:30–4:00 CII engine internals (the actual formula, configurable factors); 4:00–4:30 impact (pilot metrics: fuel, rating attainment, cost per tonne avoided); 4:30–5:00 path to MPA pilot (data ask, SEEMP integration, MTM-2027 readiness).

**PPT (≤10):** 1. The maritime trilemma. 2. Why black boxes fail at sea. 3. Physics backbone + residuals (one diagram). 4. CII-native optimisation. 5. Honest quantum-inspired + MILP proof. 6. Scenario deck + cliff. 7. Benchmarks (measured). 8. Architecture + simulator. 9. Pilot metrics + MPA path. 10. Demo + ask.

### 6.8 KPIs, risks, judge Q&A (highlights)

KPIs: fuel RMSE by speed bin, residual ablation gain, hypervolume, MILP gap %, rating attainment per scenario, cost per tonne-CO₂e avoided, optimiser wall-clock vs fleet size. All measured on the documented simulator.

Top risks: (1) "quantum" scepticism → mitigation: classical code, stated plainly, MILP-verified; (2) no real data → mitigation: simulator-first is the design, MPA path is the ask; (3) CII factor uncertainty → mitigation: configurable inputs, sensitivity bands shown; (4) physics-model accuracy challenged → mitigation: residual analysis on screen, bias-by-bin reported, never a single R²; (5) scope (lifecycle analysis depth) → mitigation: lifecycle factors as explicit, sourced parameters, not a full LCA claim.

Judge Q&A highlights: *What is quantum about this?* — Nothing runs on quantum hardware; "inspired" refers to specific mechanisms (superposition-encoded populations, rotation-gate updates), benchmarked against classical baselines on identical grounds. *Why not just use MILP?* — We do — for verification at small scale; the metaheuristic is for scale where MILP times out, and we show you the crossover. *Where is your training data?* — There is no public ship-level dataset (DCS is anonymised); our ground truth is a documented simulator, and here are its equations and distributions. *Why optimise CII instead of fuel?* — Because the regulation prices the rating, not the tonne; a fuel-optimal D-rated fleet is a commercial failure. *(12 more in the appendix.)*
