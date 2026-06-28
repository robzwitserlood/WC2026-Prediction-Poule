---
name: predict-top-scorers
description: Pick the top-scorer basket (ranked 6, top 4 submitted) by maximising expected goals × Scorito position multiplier, grounded in our own predicted scorelines. Run once after the group stage, then re-pick once per knockout phase (Scorito allows a fresh 4 each phase).
---

# predict-top-scorers

Produce a **top-scorer basket**: a ranked **6**, of which the **top 4** are the Scorito submission
(Scorito takes 4 per phase) and 5–6 are reserves. This is a **bonus value bet**.

> **Runs as a single Opus pass (the `top-scorer-picker` agent).** This is a value pick, so it gets the
> top tier — but it's a bonus bet, not the per-round match card, so it does **not** use the advisor
> ensemble. One Opus agent reads this file as spec and writes the basket.

## Two modes (Scorito lets you re-pick 4 every phase)

The orchestrator passes either **group** (once, after round 3) or a **knockout stage code**
(`r32`/`r16`/`qf`/`sf`/`final`, re-picked each phase). The method is identical; only the inputs,
the **position multipliers** (they scale up by stage), and the output path change:

| | Group (once) | Knockout `<stage>` (per phase) |
|---|---|---|
| Goal ceiling | `state/standings/round-3.md` (each team's GF) | each **alive** team's predicted goals in `state/knockout/predictions-<stage>.md` |
| Eligible players | all teams | **only teams still alive** in `<stage>` |
| Multipliers | DEF/GK 64, MID 32, ATT 16 | the `<stage>` column of the position table in `state/poule-rules.md` (R16 96/48/24, QF 128/64/32, SF 160/80/40, Final 192/96/48) |
| Output | `state/predictions/top-scorers.md` | `state/knockout/top-scorers-<stage>.md` |

A knockout phase is usually a single match per team, so the realistic ceiling is small (0–2 goals) —
which makes the **high-multiplier defender/penalty-mid value even sharper**: one set-piece header in a
QF is 128 pts. Re-pick fresh each phase from the alive teams; do not carry forward eliminated players.

## The scoring lever: goals are weighted by **position** (read this first)

Per `state/poule-rules.md`, a *picked* player banks points each time he scores, scaled by position
(group stage): **GK/Defender 64, Midfielder 32, Attacker 16** per goal. A defender's goal is worth
**4×** a striker's. So the target is **not "who scores the most goals"** — it is:

> **expected Scorito points = expected goals × position multiplier**

The crowd over-picks marquee strikers (16/goal). A set-piece centre-back or penalty-taking midfielder
on a free-scoring side is the **underpriced value** — that is the contrarian edge here. Pick a **mix**,
not all forwards.

## Inputs

Group mode (knockout mode swaps in the right-hand column of the mode table above):

- `state/standings/round-3.md` — each team's **predicted group goals = its GF column**. This is the
  **ceiling**: a player can't score more than his team scored in our sim. *(Knockout: the alive
  team's predicted goals in `state/knockout/predictions-<stage>.md`.)*
- `state/teams/<team>.md` → the **`## Goal threats`** line: each team's 1–2 likely scorers, their
  **position**, **penalty/set-piece duty**, and **share of team goals**. (Refresh squad/injury first.)
- `state/predictions/round-1.md … round-3.md` — to sanity-check *which* matches a team's goals came in.
  *(Knockout: the stage card.)*
- `state/poule-rules.md` — the position multipliers (the calibration; use the column for your stage).

## Method (hybrid: our sim sets the ceiling, research picks within it)

1. **Ceiling from our own scorelines.** Start from each team's predicted group GF (round-3 standings).
   Only consider scorers on teams we actually predicted to score — never pick a striker from a side our
   card has scoring 1 goal all group. The basket must be **consistent with our own predictions**.
2. **Estimate each candidate's expected goals** = `team predicted GF × player's share of team goals`
   (from `## Goal threats`), nudged up for **penalty + set-piece duty** (those goals concentrate on one
   player and are matchup-independent). Be realistic over 3 games.
3. **Convert to expected points** = expected goals × position multiplier (64 DEF/GK, 32 MID, 16 ATT).
   This is the ranking key — a DEF at 1.2 expected goals (~77 pts) beats an ATT at 2.5 (~40 pts).
4. **Apply the value tilt.** Where two candidates are close on expected points, prefer the one the crowd
   **underrates** (a defender/mid over a household-name striker). Stay defensible: a nailed-on striker
   with a high ceiling is still a strong pick — don't pass over real value to be contrarian for its own
   sake.
5. **Diversify the basket.** Avoid stacking all 4 submitted picks on one team or one match; spread the
   variance across teams we have scoring freely.

## Output

Write `state/predictions/top-scorers.md` (group) or `state/knockout/top-scorers-<stage>.md` (knockout):

```
# <Group-stage | STAGE> top scorers — Scorito basket
Calibration: expected goals × position multiplier (use the stage's column from poule-rules.md).
Submit the top 4; 5–6 are reserves.

## 1. <Player> — <Team> (POS) — SUBMIT
- Our sim: <Team> predicted <G> goals (group: round-3 GF; knockout: this stage's card)
- Expected goals: <e>  (≈ <share>% of team goals; pens/set-pieces: <yes/no>)
- Expected points: <e × mult>  (<e> × <mult>)
- Value angle: why this is underrated vs the crowd's striker-heavy picks
... 2, 3, 4 (SUBMIT) ...
## 5. <Player> — <Team> (POS) — reserve
## 6. <Player> — <Team> (POS) — reserve
```

Run after the full group stage is predicted and `scripts/standings.py 3` has written
`state/standings/round-3.md`. Driven by [run-group-stage].
