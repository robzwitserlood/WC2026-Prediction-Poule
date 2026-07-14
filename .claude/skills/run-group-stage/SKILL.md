---
name: run-group-stage
description: Orchestrate the full World Cup 2026 group-stage prediction round by round, feeding standings forward into each next round. Use to run the whole simulation.
---

# run-group-stage

Drives the round-by-round loop that is the core of the strategy. Predicts the group stage iteratively, never all at once.

## Model routing (token efficiency)

This pipeline routes each task to the cheapest model that can do it well — cheap models for low-skill work, the most capable model only where it earns its cost (the value picks). You are the **orchestrator**: keep yourself lightweight and **delegate** the heavy steps.

| Step | Tier | How it runs |
| --- | --- | --- |
| compute-standings | none (script) | `python3 scripts/standings.py <n>` — deterministic, zero tokens |
| research-teams | Sonnet | delegate to the **`team-researcher`** subagent |
| predict-round | **Fable 5 ensemble** | 3× **`round-advisor`** (lenses) + 1× **`round-decider`**, all Fable 5 — the betting edge |
| seed bracket | none (script) | `python3 scripts/knockout.py` — best-3rd selection + Annex C R32 seeding, deterministic, zero tokens |
| predict-champion | **Opus** (single pass) | one **`champion-picker`** subagent — the 250-pt bonus |
| predict-top-scorers | **Fable 5** (single pass) | one **`top-scorer-picker`** subagent — position-weighted scorer basket |
| orchestration (this skill) | Sonnet | runs in the main session — **set it to Sonnet** (`/model sonnet`) before driving the loop |

Delegate with the `Agent` tool, naming the subagent in `subagent_type` (`team-researcher`, `round-advisor`, `round-decider`); each agent definition in `.claude/agents/` pins its own model, so you don't pass a model yourself. The subagents read their skill file as the spec, so the skills stay the single source of truth. **Don't** do research or prediction inline in the orchestrator — that defeats the routing.

## Loop

1. **Research** (once up front, refresh per round): spawn **`team-researcher`** subagents to populate `state/teams/` for all teams (batch teams across a few agents to parallelise). Refresh squad signals + market read before each round.
2. **For each round 1 → 3:**
   a. **Advise:** spawn **three `round-advisor` subagents in parallel**, one per lens (`stats`, `contrarian`, `conditions-market`), passing the round number. Each writes `state/advice/round-<n>/<lens>.md`. Keep them blind to each other — independent opinions are the point.
   b. **Decide:** once all three advices exist, spawn **one `round-decider` subagent** for that round. It reads the three advices + inputs and writes the canonical `state/predictions/round-<n>.md` by free, value-tilted synthesis.
   c. **Standings:** run `python3 scripts/standings.py <n>` to update the table (this *is* [compute-standings]).
   d. The updated standings + status notes feed into the next round's prediction.
3. After round 3, the final group tables determine who advances. Summarize qualifiers per group.
4. **Tournament-level bonus bets (once, after round 3 + its standings are written):**
   a. **Seed the bracket:** run `python3 scripts/knockout.py` — it picks the 8 best 3rd-placed teams and seeds the R32 → final bracket from the final standings into `state/knockout/bracket.md` (deterministic, zero tokens; flags any provisional 3rd-place cutoff or Annex C assignment). This *is* the seed step in the routing table.
   b. **Spawn the two bonus-bet pickers in parallel** (each a single subagent, no ensemble — `champion-picker` on Opus, `top-scorer-picker` on Fable 5):
      - **`champion-picker`** → `state/predictions/champion.md`: the most underrated genuine contender + path (the 250-pt bonus). Needs the seeded bracket from 4a.
      - **`top-scorer-picker`** → `state/predictions/top-scorers.md`: ranked 6 (top 4 submitted) by expected goals × Scorito position multiplier, grounded in our predicted scorelines. Needs `state/standings/round-3.md`.

**Scope:** the round-by-round group-stage match card is the core; on top of it the pipeline now also produces the two **tournament-level bonus bets** — the **champion** (250 pts) and the **top-scorer basket** — plus a deterministically **seeded knockout bracket** (`scripts/knockout.py` handles best-3rd selection + Annex C slotting, no longer ad hoc). Still out of scope: predicting *every* knockout scoreline (the full R32 → final match card, which would also bank the 1.5×–3× per-match points recorded in `state/poule-rules.md`) — that remains future work.

## Why round-by-round

Each round's standings change what teams need, which changes their likely scoreline (chase a result, protect a lead, coast). Predicting all rounds at once throws away that signal. Always finish [compute-standings] for round n before running [predict-round] for round n+1.

## Persistence

State lives under `state/` (teams, predictions, standings). A later session can resume from whatever rounds already exist there — check `state/predictions/` and `state/standings/` first to see where the simulation stands before continuing.

## Tilt

Predictions use the **aggressive value tilt** (see [predict-round]): prefer defensible, market-underrated scorelines for maximum poule upside.
