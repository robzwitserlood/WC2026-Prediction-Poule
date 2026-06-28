# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repo is a workspace for winning a **World Cup 2026 prediction poule** (a betting/score-prediction pool). It is **not a software project** — there is little or no code to build, lint, or test. The work happens through **agent reasoning**: researching teams, predicting match scores, and tracking standings. Skills (in `.claude/skills/`) encapsulate the reusable steps.

## Strategy

The edge we are playing for is **value, not accuracy**: pick the most plausible scoreline from team statistics that the bookmakers/crowd rank as *unlikely*. Concretely:

- Ground every prediction in **historical and recent team-performance statistics**, not gut feeling or favorites.
- Deliberately favor outcomes that are **statistically defensible but underpriced by bookmakers** (contrarian-but-reasoned), since those score the most poule points when they hit.
- Predict the group ("poule") phase **iteratively, round by round** — not all at once.
- After each round: compute the **group standings** (points, goal difference, goals scored) from the scores predicted so far.
- Feed each team's **current group rank into the next round's prediction** (e.g. a team needing points, or one already through, behaves differently).

## Workflow

1. Define/refine the skills needed for the pipeline (research → predict-round → compute-standings → feed-forward).
2. Run the simulation round by round, persisting predicted scores and standings between rounds so each round builds on the last.

When the user says the skills are ready, drive the prediction round by round rather than predicting the whole group stage in one shot.

## Conventions

- Prefer the **`AskUserQuestion`** tool for genuine strategy forks (e.g. how contrarian to be, which stat sources to trust); otherwise pick a defensible default and proceed.
- Persist intermediate state (predicted scores, standings per round) as plain files so a later round/session can pick up where the last left off.
- Treat statistics as evidence to cite in reasoning, not just numbers — record *why* a contrarian score is defensible, since that rationale drives the value bet.

## Model routing (token efficiency)

Route each task to the cheapest model that does it well; spend the top tier only where it earns its cost. Routing happens at the **subagent boundary** — skills run inline in the calling session, so the heavy steps are delegated to subagents in `.claude/agents/`, each pinned to a model:

| Task | Tier | Mechanism |
| --- | --- | --- |
| compute-standings | none — deterministic | `scripts/standings.py` (zero tokens) |
| research-teams | Sonnet | `team-researcher` subagent |
| predict-round | **Opus ensemble** (the betting edge) | 3× `round-advisor` (lenses: stats / contrarian / conditions-market) → 1× `round-decider`, all Opus |
| seed-bracket | none — deterministic | `scripts/knockout.py` (best-3rd selection + Annex C R32 seeding, zero tokens) |
| predict-champion | **Opus** (single pass) | `champion-picker` subagent — the 250-pt champion bonus |
| predict-top-scorers | **Opus** (single pass) | `top-scorer-picker` subagent — position-weighted scorer basket (re-picked each knockout phase) |
| grade-lenses | none — deterministic | `scripts/grade.py` (toto hit-rate + calibration tally, zero tokens) |
| report-actuals / fixtures / history | Sonnet | `match-reporter` subagent — results, web-searched fixtures, one-off knockout history |
| predict-knockout | **Opus ensemble** (the betting edge) | 4× `round-advisor` (+ `knockout-context` lens) → 1× `round-decider`, all Opus |
| orchestration (run-group-stage / run-knockout-stage) | Sonnet | main session — run it on Sonnet (`/model sonnet`) |

The agent files are the model pins; the SKILL.md files remain the single source of truth for *method* (each agent reads its skill). Keep the orchestrator lightweight and delegate — doing research or prediction inline defeats the routing.

**Prediction is an ensemble, not a single call.** Per round: three Opus `round-advisor`s each predict the full round through a distinct lens and persist `state/advice/round-<n>/<lens>.md`; one Opus `round-decider` then makes the final call by free, value-tilted synthesis (may pick a scoreline no advisor proposed) and writes the canonical `state/predictions/round-<n>.md`. predict-round stays all-Opus regardless: it is where poule points are won.

**The two bonus bets are Opus, but single-pass (not ensembles).** After the group stage, `champion-picker` (the 250-pt champion) and `top-scorer-picker` (the position-weighted scorer basket) each run as **one** Opus subagent — top tier because they're value picks, but no advisor panel since they're once-off bets, not the per-round card. Both build on the group-stage result: the champion walks the bracket `scripts/knockout.py` seeds from the final standings, and the scorer basket is capped by each team's predicted goals.

**The knockout phase (`run-knockout-stage`) is now in scope** — the full R32 → final match card, scored at the 1.5×–3× stage multipliers, plus advancement bonuses and a per-phase top-scorer re-pick. It mirrors the group pipeline but is **rerun-driven: one invocation = one stage transition** (report the just-finished stage's actuals → `grade.py` the panel → predict the next stage). Differences from the group stage: the prediction ensemble grows to **four** advisor lenses (the group three + a `knockout-context` specialist for suspensions / fatigue / penalty temperament / big-game tactics, reading the Tier 2 priors in `state/reference/knockout-history.md`); the decider reweights lenses by a deterministic **scorecard** (`scripts/grade.py`, read as judgment not a formula, with a cold-start rule for the new lens) and additionally calls **who advances** (penalties decide it but don't score) and **monitors the locked champion bet**. The live bracket comes from web-searched `state/knockout/fixtures-<stage>.md` (not the now-frozen `scripts/knockout.py` seeder). Full design + build order: `state/knockout/PLAN.md`.
