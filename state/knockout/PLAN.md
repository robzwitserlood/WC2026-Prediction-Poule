# Knockout-phase pipeline — agreed plan & build order

Authoritative spec for extending the WC2026 poule workspace from the group stage to the
knockout stage (R32 → R16 → QF → SF → Final). Mirrors the group-stage architecture
(`run-group-stage` + advisors + decider + deterministic scripts) but adapted to knockout
scoring and a rerun-driven, single-stage-forward loop.

This file is the **resume point**: if a session starts mid-build, read this first, then check
which artifacts below already exist to see how far the build got.

## Strategy (unchanged)

Play for **value, not accuracy**: pick statistically defensible scorelines the bookmakers/crowd
underprice. Knockouts raise the stakes — stage multipliers make each correct call worth more, so
the value tilt matters *more* here, not less.

## Knockout scoring (from `state/poule-rules.md`)

- Match points score the **120-minute** result (extra time included). **Penalty shootouts do NOT
  count** toward the scoreline — they only decide who advances.
- Stage multipliers: **R16 1.5× / QF 2× / SF 2.5× / Final 3×** (group is the 1× base).
  Toto / exact: R16 90/135, QF 120/180, SF 150/225, Final 180/270.
- Advancement bonuses (country game): QF 30, SF 60, final 120, **champion 250**.
- Top-scorer game: **re-pick 4 per phase**, position-weighted (a defender's goal is worth 4× a
  striker's). Knockout phases multiply the same table up.

So each knockout match has **two prediction targets**: (1) the 120-min scoreline (match points)
and (2) who advances incl. penalties (advancement bonus). They can diverge — a 1-1 that's won on
pens still scores the 1-1 for match points but the shootout winner for the bonus.

## Locked design decisions

1. **Advisor panel grows to 4 — no hire/fire.** Keep the 3 group lenses
   (`stats`, `contrarian`, `conditions-market`) and add one new **`knockout-context`** lens
   (suspensions, fatigue + rest days, extra-time & penalty temperament, big-game tactics). The
   decider **reweights** lenses by judgment using a cumulative scorecard — it does not drop any.
2. **Grading = thin hit-rate / calibration tally, read as JUDGMENT (not a formula).** Track toto
   accuracy + confidence calibration per lens. Stage-weighted points are displayed but do NOT
   drive the panel. Knockout samples are tiny (16/8/4/2 matches), so calibration is informed
   mainly by a one-time **backfill-grade of the 72 group matches** (24 per round).
3. **Per-stage outputs:** (a) 120-min scoreline card, (b) top-scorer basket re-pick,
   (c) advancement calls including penalties. The **250-pt champion pick stays LOCKED** (not
   re-picked) but is **MONITORED** — the decider flags when a result eliminates it.
4. **Run model = rerun-driven, ONE invocation = ONE stage transition.** No internal look-ahead;
   the flow does NOT predict stage N+1 in the same run. The user reruns after each real stage
   completes and all next-round matchups are publicly known. Flow is **stateless / resumable** —
   it detects where it is from `state/results/` vs `state/knockout/predictions-*`.
5. **Bracket resolution = web search, not a script.** `scripts/knockout.py` is NOT extended; it
   stays the historical pre-tournament seeder. The `match-reporter` web-searches the actual
   next-round fixtures.
6. **Historical KO data, split into two value tiers:**
   - **Tier 1 — structural base rates (high transfer, whole panel):** from the **last 3 World
     Cups + recent Euros** (base rates only). E.g. how often the favorite advances per round, how
     often KO matches go to extra time / penalties, goal distributions, comeback rates. Lives in
     the method skill's cited reference so the **whole panel** uses it. R32 has no WC precedent —
     analogize from the 24-team Euro R16.
   - **Tier 2 — nation/team temperament priors (soft, alive-teams-only):** penalty record,
     big-game choke/clutch reputation, tournament-experience of the spine. Lives with the
     `knockout-context` specialist lens only; refreshed for still-alive teams each run.

## Run loop (`run-knockout-stage`, one invocation = one stage)

0. **First run only:** if `state/reference/knockout-history.md` is absent, spawn `match-reporter`
   to gather it (Tier 1 base rates + Tier 2 nation priors). Guard: skip if the file exists.
1. **Report actuals:** spawn `match-reporter` to (a) fetch the just-completed stage's real results
   into `state/results/<stage>.md`, (b) on the very first knockout run, also backfill the 72 group
   matches into `state/results/group-r1..r3.md`, (c) web-search and write the next round's fixtures
   to `state/knockout/fixtures-<next>.md`, and (d) refresh suspensions/injuries in `state/teams/`.
2. **Grade:** run `python3 scripts/grade.py` — deterministic tally + calibration of each lens's
   prior advice vs actuals. Regenerates `state/grades/scorecard.md` idempotently from every stage
   that has a results file, so the first run also backfills rounds 1–3.
3. **Advise:** spawn **four `round-advisor` subagents in parallel** (`stats`, `contrarian`,
   `conditions-market`, `knockout-context`), each predicting the full next stage through its lens,
   writing `state/advice/<stage>/<lens>.md`. Blind to each other.
4. **Decide:** spawn **one `round-decider`** — free value-tilted synthesis. Reads the four advices
   + the scorecard (as judgment) + champion.md + results. Writes:
   - `state/knockout/predictions-<stage>.md` — 120-min scoreline card + advancement call (3 claims
     per match: 120-min scoreline / who advances / bonus call) + a champion-elimination flag line.
5. **Top scorers:** spawn `top-scorer-picker` (re-runnable per phase) → `state/knockout/top-scorers-<stage>.md`,
   capped by each alive team's predicted goals.

## Build order (implement in this sequence — later steps depend on earlier ones)

1. **`.claude/skills/predict-knockout/SKILL.md`** — the knockout METHOD source. Encodes: stage
   multipliers, 120-min scoring, penalties-decide-but-don't-score, the two targets, NO standings/GD
   context (knockouts are one-off), the advancement call's 3 claims, and the value tilt for
   knockouts. Cites `state/reference/knockout-history.md` (Tier 1) and `state/poule-rules.md` **by
   pointer** (so it doesn't have to be rewritten when those change).
2. **`.claude/agents/match-reporter.md`** (Sonnet — mirror `team-researcher`'s pins exactly:
   `tools: WebSearch, WebFetch, Read, Write, Glob, Grep`, `model: sonnet`). Two jobs: one-time
   `state/reference/knockout-history.md`; per-run actuals + 72-match group backfill +
   `state/knockout/fixtures-<next>.md` + squad-signal refresh. **Built before grade.py** because
   the repo currently holds only predictions, not real group actuals — grade.py's backfill needs
   `match-reporter` to produce the actuals first.
3. **`scripts/grade.py`** — deterministic. Joins advice files + decider card + actuals on
   **normalized team names** (knockouts lack standings.py's group-membership safety net). REUSE
   standings.py's `## <Home> vs <Away> @ <venue>: <h>-<a>` header regex; FLAG-SKIP on mismatch
   (do NOT `sys.exit` like standings.py). Computes toto hit-rate + a calibration tally per lens;
   backfills rounds 1–3; appends to `state/grades/scorecard.md`.
4. **4th `knockout-context` lens + decider wiring.** Edit `.claude/agents/round-advisor.md` to add
   the lens and make agents read `predict-knockout/SKILL.md` for knockout runs (line ~12 currently
   hard-codes `predict-round/SKILL.md`). Edit `.claude/agents/round-decider.md` to consume the
   scorecard (judgment), emit the advancement call, and flag champion elimination. Add a
   **cold-start rule**: an unscored lens (the new one) gets panel-average weight until it has a
   real sample.
5. **`.claude/skills/run-knockout-stage/SKILL.md`** (Sonnet orchestrator) — drives the loop above;
   first run triggers the one-off history gather (guarded). Mirror `run-group-stage` structure.

## Data contracts (keep these stable — scripts and agents depend on them)

- **Advice file** (`state/advice/<stage>/<lens>.md`): per match, a header
  `## <Home> vs <Away> @ <venue>: <h>-<a>` followed by a `- Confidence: <low|med|high>` line.
  **Calibration data lives in the advice files**, not in the decider card.
- **Results file** (`state/results/<stage>.md`): reuse the standings.py header regex
  `## <Home> vs <Away> @ <venue>: <h>-<a>` for the 120-min score, plus an explicit
  `Advanced: <team> (pens|120)` marker per knockout match.
- **Decider card** (`state/knockout/predictions-<stage>.md`): same header regex for the scoreline
  (load-bearing), the 3-claim advancement block per match, and a champion-elimination flag line.
- **Scorecard** (`state/grades/scorecard.md`): per-lens cumulative toto hit-rate + calibration,
  one section per graded stage (rounds 1–3 backfilled first).

## What stays frozen / out of scope

- `scripts/knockout.py`, `state/knockout/bracket.md`, `state/knockout-bracket.md` — historical
  pre-tournament seeders, seeded from PREDICTED standings (now stale). Frozen as structure-only
  reference; the live run uses web-searched fixtures from `match-reporter`, NOT these.
- `state/predictions/champion.md` — the locked champion pick; read-only here (monitor, don't repick).
- Re-predicting the entire bracket in one shot — the loop only ever predicts the *next* stage.
