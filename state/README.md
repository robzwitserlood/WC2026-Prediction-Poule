# state/

Persisted simulation state. Skills read and write here so the round-by-round prediction can resume across sessions.

- `teams/<team>.md` — statistical profile per team (written by **research-teams** / `team-researcher`).
- `advice/round-<n>/<lens>.md` — one advisor's opinion for round n, per strategy lens (`stats`, `contrarian`, `conditions-market`), written by the three `round-advisor` subagents. Input to the decider; not parsed downstream.
- `predictions/round-<n>.md` — the **final** predicted scorelines per round, written by `round-decider` from the three advices. This is the canonical card that `scripts/standings.py` parses.
- `standings/round-<n>.md` — group table after round n (written by `scripts/standings.py`, i.e. **compute-standings**).
- `knockout/bracket.md` — the R32 → final bracket **seeded** from the final group standings (written by `scripts/knockout.py`: best-3rd selection + Annex C slotting). Read by **predict-champion**. Structure reference: `knockout-bracket.md`.
- `predictions/champion.md` — the predicted world champion + path (written by `champion-picker`, **predict-champion**). The 250-pt bonus bet.
- `predictions/top-scorers.md` — the group-stage top-scorer basket, ranked 6 / top 4 submitted (written by `top-scorer-picker`, **predict-top-scorers**).

The two bonus bets and the bracket are **tournament-level**, produced once after round 3 — not per round.

To see where the simulation stands, list `predictions/` and `standings/` — the highest round present is the last completed group-stage step; `champion.md` / `top-scorers.md` / `knockout/bracket.md` appear once the group stage is complete.

## Knockout phase (driven by **run-knockout-stage**, one stage per rerun)

The knockout pipeline mirrors the group one but is **rerun-driven**: each invocation reports the stage
that just finished, grades the panel, and predicts the next stage. Stage codes: `r32 r16 qf sf final`.
See `knockout/PLAN.md` for the full design.

- `knockout/PLAN.md` — the agreed knockout design + build order (the resume point for this phase).
- `reference/knockout-history.md` — one-off historical reference (written by **match-reporter**):
  **Tier 1** structural base rates (last 3 WCs + recent Euros — favourite-advances / ET / penalty
  rates, 120-min goal distributions) used by the whole panel, and **Tier 2** nation/penalty temperament
  priors used by the `knockout-context` lens.
- `results/<stage>.md` and `results/group-r<n>.md` — **actual** results (written by **match-reporter**):
  the 120-minute score in the standings-style header + an `Advanced: <team> (120|pens)` marker per
  knockout tie. The group-r1..r3 files are a one-time backfill so `grade.py` can score rounds 1–3.
- `knockout/fixtures-<stage>.md` — the **actual** web-searched matchups for a stage (written by
  **match-reporter**). These supersede `knockout/bracket.md` (which was seeded from *predicted*
  standings and is now frozen as structure-only).
- `advice/<stage>/<lens>.md` — the four knockout advisor lenses (`stats`, `contrarian`,
  `conditions-market`, `knockout-context`), written by the `round-advisor` subagents.
- `knockout/predictions-<stage>.md` — the **final** knockout card (written by `round-decider`): the
  120-minute scoreline + an `Advances:` line per tie + a `## Champion watch` flag. Parsed by `grade.py`.
- `knockout/top-scorers-<stage>.md` — the per-phase top-scorer re-pick (written by `top-scorer-picker`).
- `grades/scorecard.md` — per-lens toto hit-rate + calibration (written by `scripts/grade.py`,
  regenerated each run). The decider reads it as *judgment*, not a formula.
