---
name: predict-champion
description: Name the WC2026 world champion (the 250-pt bonus) by walking the bracket seeded from the predicted final group standings, picking the most underrated genuine contender. Champion + path only — no per-match knockout card. Run once after the group stage.
---

# predict-champion

Name the **world champion** — Scorito's single biggest bonus (**250 pts**, see `state/poule-rules.md`).
Run **once**, after the group stage is predicted and the bracket is seeded. This produces the champion
**and the likely path**; it deliberately does **not** predict every knockout scoreline (that full
knockout card is out of scope).

> **Runs as a single Opus pass (the `champion-picker` agent).** Value pick → top tier, but a once-off
> bonus, so no advisor ensemble. One Opus agent reads this file as spec and writes the call.

## The tilt: most underrated **genuine contender** (not chalk, not a long-shot)

The chosen calibration (per the user) is **value among real title sides**: pick the contender the
market/crowd **underprices**, *not* the single chalk favorite and *not* a wild dark horse. At 250 pts
all-or-nothing, the play is the best **P(win) × underpricing** trade-off — a side good enough to win
that the crowd ranks a notch too low, often because it landed in the **weaker bracket half**.

## Inputs

- `state/knockout/bracket.md` — the bracket **seeded by `scripts/knockout.py`** from our predicted final
  standings: who qualified, each contender's R32 opponent, and the two halves. Re-run the script first if
  it's missing or stale.
- `state/standings/round-3.md` — final group tables (who won their group, margins, form into the KOs).
- `state/teams/<team>.md` — the statistical profiles (squad strength, conditions fit, mispricing flags).
- `state/poule-rules.md` — the 250-pt champion payout and the advancement-bonus context.

## Method

1. **Read the seeded bracket and split it into the two halves** (`state/knockout-bracket.md` lists them:
   top half → SF M101, bottom half → SF M102). A title needs to win R32 → R16 → QF → SF → Final.
2. **List the genuine contenders** — group winners / strong sides with a title-level profile in the team
   files. Note which half each is in and how loaded that half is.
3. **Trace each contender's seeded path**: likely R32, R16, QF, SF opponents (by bracket position +
   our standings). A favourable quadrant is itself a source of value the crowd underrates.
4. **Apply the tilt.** Among genuine contenders, pick the one whose **combination of profile + path is
   underpriced** — strong enough to win, ranked too low by the market (lean on the team files'
   *mispricing flags* and the venue/conditions edges this project already tracks). Avoid the chalk
   favourite unless it is *itself* the best value; avoid a long-shot with no real title profile.
5. **Name the pivotal tie**: the one match most likely to end the run, and why you back them through it.
   Also name your **best-guess final opponent** (the bottom/top-half mirror).

## Output

Write `state/predictions/champion.md`:

```
# Predicted world champion — Scorito 250-pt bonus

## Champion: <Team>  (winner of group <X>)
- Why a genuine contender: title-level profile (stats/form/squad)
- Why underrated: where the market ranks them and why that's a notch too low (the value)
- Seeded path: R32 <opp> → R16 <likely opp> → QF <likely> → SF <half mirror> → Final <likely opp>
- Pivotal tie: the match most likely to end it, and why we back them through
- Bracket-half read: their half vs the other half (who they dodge / must beat)

## Best-guess final opponent: <Team>  (one line: why they emerge from the other half)

## Contenders considered & passed: <2–4 sides>, one line each on why the champion is better value
```

Run after `scripts/knockout.py` has written `state/knockout/bracket.md`. Driven by [run-group-stage].
