# WC2026 Prediction Poule

An agent-driven workspace for winning a World Cup 2026 score-prediction pool. The edge is **value, not accuracy**: pick the most plausible scoreline that bookmakers/crowd rank as unlikely. The group stage is predicted **round by round**, feeding each round's standings into the next; once it's complete the pipeline adds two **tournament-level bonus bets** — a **world champion** (the 250-pt bonus, the most underrated genuine contender) and a **group-stage top-scorer basket** (6 ranked, 4 submitted, weighted by Scorito's by-position goal scoring) — both built on the group-stage result. Then the **knockout phase** (R32 → final) runs as a **rerun-driven** loop — one stage per invocation — that reports the just-finished stage's real results, grades the advisor panel on them, and predicts the next stage's 120-minute card, who advances, and a fresh top-scorer basket, while monitoring the locked champion bet. See [CLAUDE.md](CLAUDE.md) for the full strategy and [state/README.md](state/README.md) for the persisted state.

## Prerequisites

You'll need these installed and accessible on your `PATH`:

- **Python 3** — for the deterministic standings, bracket, and grading scripts. If you don't have it, you probably got lost on the way to a different repo.
- **[Claude Code](https://claude.ai/code)** CLI — the whole thing runs inside it. Install via `npm i -g @anthropic/claude-code` or the desktop app.
- **An Anthropic API key** — set `ANTHROPIC_API_KEY` in your environment. The pipeline burns Opus tokens on prediction (intentionally — that's where the poule edge lives), so make sure your account has capacity.
- **Git** — for the obvious reason that you're reading this in a git repo.

No package manager, no build step, no `npm install`. It's agents and three small Python scripts. That's it.

## Getting started

Set the session to the orchestrator tier, then drive the simulation:

```text
/model sonnet
```

and invoke **run-group-stage** to drive it.

The orchestrator (Sonnet) then delegates each step to the right model automatically: research → `team-researcher` (Sonnet), prediction → the all-Opus `round-advisor` ensemble + `round-decider`, and standings → the deterministic `scripts/standings.py` (zero tokens). After round 3 it seeds the knockout bracket with `scripts/knockout.py` (best-3rd selection + Annex C slotting, zero tokens) and spawns two single-pass Opus pickers — `champion-picker` and `top-scorer-picker` — for the bonus bets. State persists under `state/`, so a later session can resume from wherever the last round left off.

Once the real group stage finishes, drive the knockouts by invoking **run-knockout-stage** (still on Sonnet). It's **rerun-driven — one invocation per real stage**: it detects where it is from `state/`, has `match-reporter` (Sonnet) fetch the just-finished stage's actual results and web-search the next round's fixtures, grades the panel with the deterministic `scripts/grade.py` (zero tokens), then predicts the next stage as a **four-lens** Opus ensemble (the group three plus a `knockout-context` specialist) whose `round-decider` reweights the lenses by the running scorecard, calls who advances, and re-picks the top-scorer basket. The first run also gathers a one-off historical-knockout reference and backfills/grades the group rounds. Rerun it after each stage is played; the full design and build order live in [state/knockout/PLAN.md](state/knockout/PLAN.md).
