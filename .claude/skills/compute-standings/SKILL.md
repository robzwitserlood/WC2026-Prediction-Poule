---
name: compute-standings
description: Compute group standings from the scorelines predicted so far, ranking teams by World Cup tiebreak rules. Run after each predicted round so the next round can use current ranks.
---

# compute-standings

Turn predicted scorelines into a group table. Output feeds [predict-round]'s standings context for the next round.

## How to run (do not compute by hand)

This step is pure arithmetic, so it runs as a **deterministic script — zero model tokens, no tiebreak slips**:

```
python3 scripts/standings.py <n>     # standings after round n
python3 scripts/standings.py         # uses the highest round present
```

It reads group membership from `state/groups.md` and predicted scorelines from `state/predictions/round-1.md … round-<n>.md`, and writes `state/standings/round-<n>.md`. The rules below are the **spec the script implements** — they are here so you can audit its output, not so you redo the math by hand. If a prediction line can't be parsed (unknown team name, cross-group match), the script exits with an error rather than guessing; fix the prediction file and re-run.

## Inputs

- All `state/predictions/round-1.md` … `round-<n>.md` predicted so far.

## Rules (the script's spec — audit against these)

- Win = 3 pts, draw = 1, loss = 0.
- Rank by: **points → goal difference → goals scored** (FIFA group-stage order).
- **Detect ties — do not silently break them.** If two teams are level on all three of pts/GD/GF, flag it in the Notes line and apply the next FIFA tiebreakers in order: head-to-head points → H2H goal difference → H2H goals → (then disciplinary/fair-play, then drawing of lots — note if it comes to that). A wrongly-broken tie corrupts the rank that feeds the next round, so surface the tie and the tiebreaker used rather than guessing. The script does exactly this: it breaks ties by head-to-head, and where even H2H is level it **flags the cluster as provisional** (fair-play points and drawing of lots aren't derivable from scorelines) — resolve those by hand before the rank feeds the next round.
- One table per group.

## Output (produced by the script)

The script writes `state/standings/round-<n>.md` — the table *after* round n:

```
# Group <X> — after round <n>
| Pos | Team | P | W | D | L | GF | GA | GD | Pts |
... rows sorted by rank ...
Notes: per-team status — through / eliminated / clinched / "N pts, pos P, K games left".
```

The "Notes" line is the hook [predict-round] uses for the next round. The script computes it **deterministically and never overclaims**: it only says "clinched top 2" or "eliminated from top 2" when that is mathematically locked given points and games remaining; otherwise it reports current points, position, and games left. Tallies are cumulative across all rounds predicted so far. If you want a richer qualitative read ("must chase goals", "may rotate"), the **predictor** infers that from this factual status — the standings step stays deterministic.
