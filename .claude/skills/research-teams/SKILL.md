---
name: research-teams
description: Gather historical and recent performance statistics for World Cup 2026 teams to ground later score predictions. Use before predicting any round, or to refresh a team's profile.
---

# research-teams

Build an evidence base per team so predictions rest on statistics, not vibes. Output goes to `state/teams/<team>.md` and is read by [predict-round].

> **Runs on the mid tier (Sonnet).** When driven by [run-group-stage], this work is delegated to the **`team-researcher`** subagent (model: sonnet) — data-gathering with source judgment, but not the top-tier reasoning reserved for the value picks. The agent reads this file as its spec, so keep this skill the single source of truth.

## Filename convention (pin this — fan-out depends on it)

One file per team at `state/teams/<slug>.md`, where `<slug>` is the team name **lowercased, ASCII-folded, spaces → hyphens**: e.g. `bosnia-and-herzegovina.md`, `ivory-coast.md` (not "côte-d'ivoire"), `turkiye.md`, `curacao.md`, `dr-congo.md`, `south-korea.md`. Use the exact names in `state/groups.md` as the source of truth. This must be stable so parallel research agents and [predict-round] resolve the same path.

## What to gather (per team)

- **Recent form**: last ~10 competitive matches — results, goals for/against, opponent strength.
- **Tournament/qualifying record**: how they performed in qualifying for WC2026 and recent major tournaments.
- **Scoring & conceding profile**: goals per game, clean-sheet rate, whether they win tight or blow teams out. This drives *scoreline* shape, not just win/loss.
- **Goal threats** (feeds [predict-top-scorers]): the **1–2 players most likely to score**, each with **position** (GK/DEF/MID/ATT — load-bearing: Scorito pays a defender's goal 4× a striker's), **penalty + set-piece duty** (who actually takes them), recent **goals/90 or qualifying goal tally**, and roughly what **share of the team's goals** they account for. A set-piece centre-back or penalty-taking midfielder matters here even if he isn't the headline striker.
- **Squad signals**: key injuries, suspensions, form of main scorer/keeper at time of prediction.
- **Style/matchup notes**: high-press vs. counter, vulnerability to pace, set-piece strength.
- **Conditions fit**: how the team handles **heat/humidity, altitude, and long travel** — climate of their league/home, any record in hot or high-altitude venues, squad depth for a congested schedule. WC2026's US/Mexico venues make this a real, crowd-underrated factor (see [predict-round]'s venue step).
- **Market read**: where bookmakers/crowd rank them. Note this *specifically* — it is what we exploit. Flag any gap between their statistical profile and their market price.

## Method

1. Use `WebSearch` for current (June 2026) form, injuries, and odds. The tournament context is live, so prefer recent sources.
2. Record numbers *with their source and date* — predictions cite this later.
3. Explicitly call out **where the team looks mispriced** (better or worse than the market thinks). That note is the seed of an aggressive value pick.

## Output format

Write `state/teams/<team>.md`:

```
# <Team>  (group <X>)
## Form (last N): ...
## Scoring profile: GF/g, GA/g, clean-sheet %, typical winning margin
## Goal threats: <player> (POS, pens/set-pieces?, goals/90 or recent tally, ~% of team goals); 1–2 names
## Squad signals (as of <date>): ...
## Matchup notes: ...
## Market read: bookmaker rank / odds, and where it diverges from the stats
## Mispricing flag: <where the value is>
```

Keep it terse and quantitative. Refresh squad signals and market read right before each round, since they move.
