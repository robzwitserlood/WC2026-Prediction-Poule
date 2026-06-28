---
name: run-knockout-stage
description: Orchestrate ONE knockout stage transition of the WC2026 poule — report the just-finished stage's actuals, grade the lenses, then predict the next stage (R32 → R16 → QF → SF → Final) as a 4-lens Opus ensemble. Rerun once per real stage; the flow detects where it is. Use to drive the knockout phase.
---

# run-knockout-stage

Drives the knockout phase, the sequel to [run-group-stage]. It is **rerun-driven**: **one invocation =
one stage transition.** It does NOT look ahead — it reports the stage that just finished in reality,
grades the panel on it, and predicts the **next** stage. The user reruns the skill after each real
stage completes and the next round's fixtures are publicly known. The flow is **stateless / resumable**:
it works out where it is from the files in `state/`, so a later session can pick up mid-phase.

Stage order: **`r32` → `r16` → `qf` → `sf` → `final`** (the group rounds are `r1`/`r2`/`r3`).

## Model routing (token efficiency)

Same discipline as [run-group-stage]: cheapest model that does each job well; the top tier only on
the value picks. You are the **orchestrator** — stay lightweight and **delegate**.

| Step | Tier | How it runs |
| --- | --- | --- |
| grade lenses | none (script) | `python3 scripts/grade.py` — deterministic, zero tokens |
| report actuals / fixtures / history | Sonnet | the **`match-reporter`** subagent |
| predict-knockout | **Opus ensemble** | 4× **`round-advisor`** (lenses) + 1× **`round-decider`**, all Opus — the betting edge |
| predict-top-scorers (re-pick) | **Opus** (single pass) | one **`top-scorer-picker`** subagent |
| orchestration (this skill) | Sonnet | runs in the main session — **set it to Sonnet** (`/model sonnet`) |

Delegate with the `Agent` tool naming the subagent in `subagent_type` (`match-reporter`,
`round-advisor`, `round-decider`, `top-scorer-picker`); each agent pins its own model. The subagents
read their skill/method files as the spec, so the skills stay the single source of truth. **Don't** do
reporting or prediction inline — that defeats the routing.

## Step 0 — work out where you are (do this first, every run)

1. List `state/knockout/predictions-*.md` and `state/results/*.md`.
2. **`next_stage`** = the first of `r32, r16, qf, sf, final` with **no** `predictions-<stage>.md`.
   - If all five exist → the phase is fully predicted; on a rerun just report + grade the final
     (below) and stop.
3. **`done_stage`** = the stage just before `next_stage` (the **group stage / round 3** if
   `next_stage` is `r32`; otherwise the previous knockout stage). The user only reruns once `done_stage`
   has actually been played, so its results are now available to fetch.
4. **Resume safety:** if a previous run half-finished, skip sub-steps whose outputs already exist
   (advice files written but no decider card → just run the decider; etc.). Never overwrite a
   completed stage's prediction on a rerun.

## First-run setup (only when `next_stage` is `r32` — guard each)

- **History reference:** if `state/reference/knockout-history.md` is absent, spawn **`match-reporter`**
  to build it once (Tier 1 base rates from the last 3 WCs + recent Euros; Tier 2 nation/penalty
  temperament priors). Skip if it exists.
- **R32 multiplier:** `state/poule-rules.md` has **no Round-of-32 row** (its table starts at R16).
  Verify the R32 match multiplier (web search Scorito WK 2026) and **patch `state/poule-rules.md`**
  before predicting R32. If you cannot confirm it, leave it flagged — `scripts/grade.py` already shows
  R32 points as "TBD" rather than guessing.
- **Group backfill:** the group `state/results/` files do not exist yet — `match-reporter` writes the
  72 real group results (`group-r1..r3.md`) in the actuals step below, which is what lets
  `scripts/grade.py` backfill-grade rounds 1–3.

## The one-stage loop

1. **Report actuals** — spawn **`match-reporter`**, telling it `done_stage` and `next_stage`. It:
   (a) fetches `done_stage`'s real results → `state/results/<done_stage>.md` (first run: also the 72
   group results); (b) web-searches `next_stage`'s **actual** fixtures → `state/knockout/fixtures-<next_stage>.md`
   (these supersede the stale, prediction-seeded `state/knockout/bracket.md`); (c) refreshes
   suspensions/injuries in `state/teams/` for the still-alive teams.
2. **Grade** — run `python3 scripts/grade.py`. Deterministic; regenerates `state/grades/scorecard.md`
   across every stage that now has results (first run backfills rounds 1–3). This is the trust read
   the decider will weigh.
3. **Advise** — spawn **four `round-advisor` subagents in parallel**, one per lens (`stats`,
   `contrarian`, `conditions-market`, `knockout-context`), passing `next_stage`. Each writes
   `state/advice/<next_stage>/<lens>.md`. Keep them blind to each other.
4. **Decide** — once all four advices exist, spawn **one `round-decider`** for `next_stage`. It reads
   the four advices + the scorecard (as judgment, with the cold-start rule) + inputs, makes the final
   call by free value-tilted synthesis, calls **who advances** per tie, writes the canonical
   `state/knockout/predictions-<next_stage>.md`, and adds a **`## Champion watch`** flag if the locked
   champion bet (`state/predictions/champion.md`) is affected.
5. **Top scorers (re-pick for the phase)** — spawn **`top-scorer-picker`** → `state/knockout/top-scorers-<next_stage>.md`:
   the 4 picks for this phase by expected goals × Scorito position multiplier (defenders/mids on
   free-scoring alive sides are the value), **capped by each alive team's predicted goals** in the
   stage card. The basket is re-picked each phase, so this runs every stage.

Then stop. The user reruns once `next_stage` has been played in reality, and the same logic advances
to the stage after it.

## End of phase

When `next_stage` is `final`, the loop predicts the final as above. On the **next** rerun (after the
final is played) Step 0 finds all five stages predicted: spawn `match-reporter` for the final results,
run `scripts/grade.py` one last time, and report whether the locked **champion** bet (250 pts) and the
final-opponent guess came in. The full knockout card is then complete.

## Persistence & scope

- State lives under `state/` — `results/`, `advice/<stage>/`, `knockout/predictions-<stage>.md`,
  `knockout/top-scorers-<stage>.md`, `grades/scorecard.md`, `reference/knockout-history.md`. A later
  session resumes from whatever is present (Step 0).
- **Frozen / not used for live fixtures:** `scripts/knockout.py`, `state/knockout/bracket.md`,
  `state/knockout-bracket.md` — pre-tournament seeders built from *predicted* standings. The live run
  uses the web-searched `fixtures-<stage>.md` instead.
- **Locked:** the champion pick is monitored, never re-picked.
- **In scope now:** the full R32 → final match card (the 1.5×–3× per-match points) + advancement bonuses
  + the per-phase top-scorer re-pick — the work [run-group-stage] left as future.
