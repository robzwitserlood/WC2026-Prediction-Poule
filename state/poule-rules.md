# Poule scoring rules — Scorito WK 2026

Source: https://pouletips.nl/blog/scorito-wk-2026-uitgelegd/ (fetched 2026-06-09).
This is the scoring function the **value tilt** in [predict-round] must be calibrated against.

## Match predictions (the part our pipeline predicts)

Points scale by stage via a multiplier; the group stage is the 1× base.

| Stage        | Mult. | Correct result (toto) | Exact score |
|--------------|-------|-----------------------|-------------|
| Group        | 1×    | 60                    | 90          |
| Round of 32  | 1×    | 60                    | 90          |
| Round of 16  | 1.5×  | 90                    | 135         |
| Quarterfinal | 2×    | 120                   | 180         |
| Semifinal    | 2.5×  | 150                   | 225         |
| Final        | 3×    | 180                   | 270         |

- Knockouts score the **120-minute** result (incl. extra time). Penalty shootouts do **not** count toward the result.
- Advancement bonuses (the country game): correct group qualifier 50, correct group position 75, QF 30, SF 60, final 120, **champion 250**.

## Bonus predictions (top scorer & champion) — now part of our outputs

Two tournament-level bonus bets the pipeline also produces (see [predict-top-scorers] and
[predict-champion]). They reuse the same **value tilt**, calibrated to the payouts below.

### Top-scorer game — goals are scored by **position** (the value lever)

You pick **4 top scorers per phase** (you may re-pick each phase). A picked player banks points
each time he scores, and the points **scale by his position** — a defender's goal is worth **4× a
striker's**. Group-stage values (knockout phases multiply up the same way):

| Position          | Group | R16 |  QF |  SF | Final |
|-------------------|------:|----:|----:|----:|------:|
| Keeper / Defender |    64 |  96 | 128 | 160 |   192 |
| Midfielder        |    32 |  48 |  64 |  80 |    96 |
| Attacker          |    16 |  24 |  32 |  40 |    48 |

- **Calibration for [predict-top-scorers]:** maximise **expected goals × position multiplier**, not
  raw goals. A set-piece/penalty centre-back or attacking full-back who nets 1–2 in the group stage
  (64–128 pts) beats a striker who nets 3 (48 pts). The crowd over-picks strikers, so high-multiplier
  defenders/mids on free-scoring sides are the **underpriced value** — pick a mix, not all forwards.
- Our requested deliverable is a ranked **6**; Scorito only submits **4 per phase**, so the basket
  marks the top 4 as the picks and 5–6 as reserves.

### Champion — single 250-pt bonus

The biggest single payout. Per the chosen tilt, [predict-champion] names the **most underrated
genuine contender** (value among real title sides), not a wild long-shot and not the chalk favorite.
Scored on the actual world champion only.

## What this means for the tilt (group stage)

- **Exact score = 90, correct result = 60.** The exact-score *bonus over* getting the toto right is only **30 pts (+50%)**. You do **not** forfeit the 60 toto points by missing the exact score — you keep them as long as the result direction (win/draw/loss) is correct.
- So the value math per match is: an aggressive contrarian *exact* scoreline is worth chasing **only when it does not jeopardize the toto**. Getting the toto wrong costs the full 60; the exact-score upside is just +30.
- **Practical rule for [predict-round]:** lock the most defensible **result direction** first (protect the 60), then within that direction pick the contrarian-but-defensible *exact* scoreline for the +30. Be aggressive on the *scoreline shape*, conservative on the *result*. Do not pick a contrarian scoreline that flips the predicted winner unless the stats genuinely favor that flip.
- A draw is its own toto bucket — predicting a draw scoreline only banks the 60 if the match actually draws.

Recorded so a later session/knockout extension reuses the same calibration.
