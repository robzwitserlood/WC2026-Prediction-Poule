---
name: predict-round
description: Predict every match scoreline for one group-stage round, using team stats and the current standings, with an aggressive value tilt. Use once per round during the group stage.
---

# predict-round

Predict the **exact scorelines** for one round of one (or all) groups. The goal is **poule points**, which reward defensible scorelines the market underrates — not raw accuracy.

> **Runs as an all-Fable 5 ensemble (the betting edge).** When driven by [run-group-stage], this is not one agent but a panel: three **`round-advisor`** subagents (model: claude-fable-5) each predict the full round through a distinct lens — `stats` (form purist), `contrarian` (value-hunter), `conditions-market` (venue/altitude/heat + mispricing) — and persist their opinion to `state/advice/round-<n>/<lens>.md`. Then one **`round-decider`** subagent (model: claude-fable-5) reads all three and makes the **final call by free, value-tilted synthesis**, writing the canonical `state/predictions/round-<n>.md`. The decider may pick a scoreline no advisor proposed. All four agents read **this file** as the shared method spec — so keep it the single source of truth; the lenses only change *where each leans within* this method.

## Inputs

- `state/teams/<team>.md` from [research-teams] — the statistical evidence.
- `state/standings/round-<n-1>.md` from [compute-standings] — standings *after the previous round*. For round 1 there are none.
- The fixture list for this round, **including venue + kickoff time** (`state/fixtures.md`).
- `state/poule-rules.md` — the scoring function the tilt is calibrated against.

## The tilt is calibrated to the scoring rules

Group-stage scoring (Scorito, see `state/poule-rules.md`): **correct result (toto) = 60, exact score = 90.** Getting the toto right keeps 60 even if the exact score misses; the exact-score bonus is only **+30**. Getting the *result* wrong costs the full 60.

So the correct shape of "aggressive value" here is: **conservative on the result direction, aggressive on the scoreline.**

1. **Lock the result first (protect the 60).** Pick the most defensible win/draw/loss direction from the stats. Do **not** choose a contrarian scoreline that flips the predicted winner unless the stats genuinely favour the flip — flipping the toto risks 60 to chase 30.
2. **Then go contrarian on the exact scoreline (chase the +30).** Within the locked direction, prefer the defensible scoreline the market underrates over the chalk scoreline. This is where variance is cheap: the toto is already banked.

## How to predict

1. **Start from the stats**, not the favorite. Derive each team's expected goals from its scoring/conceding profile and the specific matchup.
2. **Weight venue & conditions.** The first-named team is a label, not home advantage. Real home edge applies only to hosts (Mexico/USA/Canada) at home. For every match factor in **altitude** (Mexico City ~2240m, Guadalajara ~1560m sap visiting teams unused to it), **heat/humidity** at midday US/Mexico kickoffs, and **travel** across the host continent. Teams from cool climates or with thin altitude exposure are systematically *overrated by the crowd* in these spots — a real source of underpriced value. Note the condition angle in the rationale when it moved the score.
3. **Find the market gap.** Compare the statistically-supported scoreline to what bookmakers expect. Where a *defensible* scoreline is underpriced, prefer it — per the calibration above, on the **scoreline shape**, not by flipping the result.
4. **Apply standings context** (round 2+): factor in each team's current group rank and what they *need*. A side that must win pushes numbers; a side already through may rotate/coast. Teams chasing goal difference go for margin.
5. **Stay defensible.** Aggressive ≠ random. Every pick needs a one-line stats-based rationale. If you can't justify a contrarian score, take the plausible one.

## Output

Write `state/predictions/round-<n>.md`:

```
# Round <n> predictions
## <Home> vs <Away> @ <venue>: <h>-<a>
- Result locked (toto): <home win / draw / away win> — why this direction is the safe 60
- Rationale (stats): ...
- Value angle: why the market underrates this *scoreline* (the +30 bet)
- Venue/conditions: altitude/heat/travel effect, if it moved the score
- Standings context (r2+): what each side needs and how it shaped the score
```

After predicting a round, run [compute-standings] to update the table before predicting the next. Do not predict the whole group stage at once — go round by round so standings feed forward. This is driven by [run-group-stage].
