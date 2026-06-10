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
