---
name: predict-knockout
description: Predict one knockout stage (R32 / R16 / QF / SF / Final) of the WC2026 poule — the 120-minute scoreline plus who advances — with the value tilt, calibrated to the stage multiplier. Use once per stage during the knockouts, driven by run-knockout-stage.
---

# predict-knockout

Predict one **knockout stage** of WC2026: for every tie in the stage, the **120-minute scoreline**
(the match points) **and** who advances (the advancement bonus). The goal is **poule points** —
defensible scorelines the market underrates, now worth more because they scale by stage multiplier.

This is the knockout sibling of [predict-round]. It uses the same value philosophy but a different
scoring function (multipliers, 120-minute result, penalties-decide-but-don't-score) and a different
context model (one-off ties, no standings — fatigue/suspensions/temperament instead).

> **Runs as an all-Fable 5 ensemble (the betting edge), now a panel of four.** When driven by
> [run-knockout-stage], this is not one agent: **four `round-advisor` subagents** (model: claude-fable-5) each
> predict the full stage through a distinct lens — `stats`, `contrarian`, `conditions-market`, and
> the knockout-only **`knockout-context`** (suspensions / fatigue+rest / extra-time & penalty
> temperament / big-game tactics) — and persist to `state/advice/<stage>/<lens>.md`. Then one
> `round-decider` subagent (model: claude-fable-5) reads all four **plus the running scorecard**
> (`state/grades/scorecard.md`, read as *judgment* about which lens has earned trust — not a formula)
> and makes the final call by free, value-tilted synthesis, writing the canonical
> `state/knockout/predictions-<stage>.md`. The decider may pick a scoreline no advisor proposed. All
> five agents read **this file** as the shared method spec — keep it the single source of truth.

## Stage codes

`<stage>` is one of `r32`, `r16`, `qf`, `sf`, `final` (used in every filename below).

## Inputs

- `state/knockout/fixtures-<stage>.md` — the **actual** ties for this stage, web-searched by
  `match-reporter` (NOT the pre-tournament `state/knockout/bracket.md`, which was seeded from
  *predicted* group standings and is now stale — see [run-knockout-stage]). Includes venue + kickoff.
- `state/teams/<team>.md` — statistical profiles, **refreshed** by `match-reporter` for the still-alive
  teams (current suspensions, injuries, minutes load).
- `state/results/<prev-stage>.md` — what actually happened last round: momentum, who needed ET/pens
  (a fatigue tell), injuries picked up. **There are no standings in the knockouts** — each tie is
  one-off, so do not carry group goal-difference logic forward.
- `state/reference/knockout-history.md` — **Tier 1** structural base rates (last 3 WCs + recent Euros):
  how often the favourite advances per round, how often ties go to ET / penalties, 120-minute goal
  distributions, comeback rates. The whole panel uses these. **Tier 2** (nation/team penalty &
  big-game temperament priors) is for the `knockout-context` lens specifically.
- `state/poule-rules.md` — the scoring function the tilt is calibrated against (by pointer; do not
  restate the numbers, read them).
- `state/predictions/champion.md` — the locked 250-pt champion pick, for the elimination check below.
- `state/grades/scorecard.md` — per-lens hit-rate/calibration so far (decider input; see above).

## The scoring function (read `state/poule-rules.md`; key points)

- Knockouts score the **120-minute result** (extra time included). **Penalty shootouts do NOT count**
  toward the scoreline — a tie level after 120 is a *draw* for match points, and the shootout only
  decides who advances.
- Match points scale by **stage multiplier**: R16 1.5×, QF 2×, SF 2.5×, Final 3× (toto : exact still
  ≈ 2 : 3 at every stage, exactly as in the group stage). The *ratio* is unchanged, so the
  "lock the toto, then chase the exact shape" logic from [predict-round] carries over — but the
  **absolute stakes rise each round**, so protecting the toto matters *more* the deeper you go.
- **⚠ Round of 32 multiplier is not in `state/poule-rules.md`** (the source table starts at R16).
  Before the `r32` run, verify the R32 match multiplier (web search Scorito WK 2026) and patch
  `state/poule-rules.md`. Until confirmed, flag it — do not silently assume a value. [run-knockout-stage]
  owns this first-run check.
- **Advancement bonuses (separate currency):** reaching QF 30, SF 60, final 120, **champion 250**.
  Reaching R32 / R16 banks no advancement bonus (the group-qualifier 50 / position 75 already paid
  out). So who-advances only starts earning bonus points from the QF onward — but you still predict it
  every round because the bracket is path-dependent and the champion pick must be monitored.

## The two targets (call BOTH, every tie)

1. **120-minute scoreline** → the match points (multiplier × toto/exact). Predicted as a normal
   scoreline; a draw here is a real, scoreable outcome.
2. **Who advances** → the advancement bonus. If your 120-minute scoreline is decisive, the winner
   advances. If it is a **draw**, you must additionally name the **shootout winner** (this does not
   change the scoreline points — it only decides the bonus). This is where Tier 2 penalty temperament
   earns its keep.

These two can and should diverge: predicting "1-1, advances on penalties: Team A" is a single
coherent call that banks the draw toto/exact *and* the advancement bonus.

## The tilt (calibrated to the rules above)

Same backbone as [predict-round] — **conservative on the result, aggressive on the scoreline** — with
three knockout-specific adjustments:

1. **Lock the 120-minute toto first, and lock it harder each round.** The multiplier makes a toto
   miss expensive (a wrong SF toto forfeits 150; a wrong final toto forfeits 180). Only take a
   contrarian *result direction* when the stats genuinely compel it — and raise that bar as the
   multiplier climbs.
2. **The 120-minute DRAW is the underpriced knockout bucket.** The crowd instinctively predicts a
   winner in normal time and forgets penalties don't score. Knockout ties are cagier and lower-scoring
   than group games (use the Tier 1 ET/penalty base rates), so a defensible **1-1 / 0-0 that goes to
   penalties** banks both the draw toto and a clean exact score the field misses. Prefer it wherever
   two well-matched sides or two strong defences meet — then name the shootout winner for the bonus.
3. **Then chase the exact shape within the locked direction** (the +50% exact bonus), favouring the
   defensible market-underrated scoreline over the chalk — exactly as in the group stage.

## How to predict

1. **Start from the stats and the matchup**, not the bracket seeding or the name. Derive each side's
   expected 120-minute goals from scoring/conceding profiles and the head-to-head shape.
2. **Apply knockout context (no standings here):**
   - **Fatigue / rest:** days between matches, travel, and whether a side played 120 min + a shootout
     last round (a real legs tell — see `state/results/<prev-stage>.md`).
   - **Suspensions / injuries:** yellow-card accumulation and knocks from the refreshed team files.
   - **Extra-time & penalty temperament (Tier 2):** for any tie you call as a draw, the shootout
     winner is driven by penalty record and big-game composure, not by the 120-min favourite.
   - **Big-game tactics:** sides that tighten up in elimination football (lower-scoring than their
     group output) vs sides that keep their shape.
3. **Find the market gap.** Compare the defensible scoreline to the bookmaker line; prefer the
   underrated *shape* (and especially the underrated *draw*) where the stats back it.
4. **Weight venue & conditions** as in [predict-round] (altitude, heat/humidity, travel, true host
   edge for Mexico/USA/Canada only) — these still move scorelines.
5. **Stay defensible.** Every pick — scoreline and shootout winner — needs a one-line stats/temperament
   rationale grounded in the team files or the history reference. Aggressive ≠ random.

## Output

The decider writes `state/knockout/predictions-<stage>.md`:

```
# <STAGE> predictions  (multiplier <m>×)
## <Home> vs <Away> @ <venue>: <h>-<a>
- Result locked (toto): <home win / draw / away win> — why this direction is the safe (×mult) toto
- Rationale (stats): ...
- Value angle: why the market underrates this *scoreline* (the exact bonus); note if it's the underpriced draw
- Advances: <team> (<120 | pens>) — who goes through; if the 120-min line is a draw, name the shootout winner + why (Tier 2)
- Bonus: <which advancement bonus this banks, if any> — "none (R32/R16)" / "QF 30 to <team>" / "SF 60" / "final 120" / "+champion 250"
- Context: fatigue/rest, suspensions, ET/penalty temperament, conditions — whichever moved the call
```

- Keep the `## <Home> vs <Away> @ <venue>: <h>-<a>` header in **exactly** that shape — `scripts/grade.py`
  parses it (same regex as `scripts/standings.py`), so it is load-bearing. Use exact team names from
  `state/knockout/fixtures-<stage>.md`.
- Where the decider diverged from all four advisors or broke a split, add an `- Audit:` line: what the
  advisors said, what was chosen, why. That trail is the point of the panel.

## Champion monitoring (the decider owns this)

The 250-pt champion pick (`state/predictions/champion.md`) is **locked, not re-picked** — but it must
be **monitored**. After deciding the stage, cross-check the actual results (`state/results/<prev-stage>.md`)
and this stage's calls against the champion's seeded path. If the champion has been eliminated, or this
stage eliminates a team on its path, add a **`## Champion watch`** section at the top of the predictions
file flagging it (and whether the final-opponent guess is still alive). Do not change the champion bet;
just surface the status so the user sees it.

## Out of scope

- Re-picking the champion (locked) and predicting more than the *current* stage (the loop is
  rerun-driven, one stage per invocation — see [run-knockout-stage]).
- The top-scorer basket re-pick is a separate Fable 5 pass (`top-scorer-picker`), not part of this file.
