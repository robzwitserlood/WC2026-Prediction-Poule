# WC2026 Knockout Bracket (structure)

The fixed slot structure of the 32-team knockout stage (Round of 32 → Final). This is the
**reference map** `scripts/knockout.py` seeds with concrete teams from the final group standings,
and that [predict-champion] walks to reason a champion + path. Analogous to `state/fixtures.md`,
but for the knockouts.

Format reminder (from `state/groups.md`): 12 groups of 4. **Top 2 of each group + the 8 best
3rd-placed teams** advance → 32 teams. Knockout score is the **120-minute** result (extra time
counts, penalties do not — see `state/poule-rules.md`).

Sources: Wikipedia "2026 FIFA World Cup knockout stage" (R32 slot map + Annex C reference);
FIFA tournament regulations Annex C (495 third-place combinations). Fetched 2026-06-09.

## How the third-placed teams are slotted (Annex C)

8 of the 16 R32 matches pair a **group winner vs a 3rd-placed team**; the other 8 pair
winner-vs-runner-up (4) or runner-up-vs-runner-up (4). Group winners never meet other winners in
the R32, and no team meets a side from its own group.

*Which* of the 8 qualifying 3rds goes to *which* winner is fixed by FIFA's Annex C table (495
combinations, one per possible set of 8 qualifying 3rd-place groups). Each winner-vs-3rd slot only
accepts a 3rd from a fixed set of 5 groups (below). `scripts/knockout.py` reads the 8 qualifying
3rd-place groups from the standings and assigns them to these slots by constraint satisfaction over
those eligible sets; if more than one valid assignment exists it picks a canonical one and **flags
it provisional** (same "flag, don't silently guess" discipline as `scripts/standings.py`).

## Round of 32 (matches 73–88)

| Match | Home slot | Away slot | 3rd eligible from |
|-------|-----------|-----------|-------------------|
| 73 | Runner-up A | Runner-up B | — |
| 74 | Winner E | 3rd place | A / B / C / D / F |
| 75 | Winner F | Runner-up C | — |
| 76 | Winner C | Runner-up F | — |
| 77 | Winner I | 3rd place | C / D / F / G / H |
| 78 | Runner-up E | Runner-up I | — |
| 79 | Winner A | 3rd place | C / E / F / H / I |
| 80 | Winner L | 3rd place | E / H / I / J / K |
| 81 | Winner D | 3rd place | B / E / F / I / J |
| 82 | Winner G | 3rd place | A / E / H / I / J |
| 83 | Runner-up K | Runner-up L | — |
| 84 | Winner H | Runner-up J | — |
| 85 | Winner B | 3rd place | E / F / G / I / J |
| 86 | Winner J | Runner-up H | — |
| 87 | Winner K | 3rd place | D / E / I / J / L |
| 88 | Runner-up D | Runner-up G | — |

## Round of 16 (matches 89–96)

| Match | From | From |
|-------|------|------|
| 89 | Winner M74 | Winner M77 |
| 90 | Winner M73 | Winner M75 |
| 91 | Winner M76 | Winner M78 |
| 92 | Winner M79 | Winner M80 |
| 93 | Winner M83 | Winner M84 |
| 94 | Winner M81 | Winner M82 |
| 95 | Winner M86 | Winner M88 |
| 96 | Winner M85 | Winner M87 |

## Quarterfinals (matches 97–100)

| Match | From | From |
|-------|------|------|
| 97 | Winner M89 | Winner M90 |
| 98 | Winner M93 | Winner M94 |
| 99 | Winner M91 | Winner M92 |
| 100 | Winner M95 | Winner M96 |

## Semifinals (matches 101–102)

| Match | From | From |
|-------|------|------|
| 101 | Winner M97 | Winner M98 |
| 102 | Winner M99 | Winner M100 |

## Final (match 104) & 3rd-place (match 103)

| Match | From | From |
|-------|------|------|
| 103 (3rd place) | Loser M101 | Loser M102 |
| 104 (Final) | Winner M101 | Winner M102 |

## Bracket halves (for path reasoning)

- **Top half → SF M101:** QF M97 = {M89=(M74,M77), M90=(M73,M75)} and QF M98 = {M93=(M83,M84), M94=(M81,M82)}.
- **Bottom half → SF M102:** QF M99 = {M91=(M76,M78), M92=(M79,M80)} and QF M100 = {M95=(M86,M88), M96=(M85,M87)}.

A champion must win its R32 → R16 → QF → SF → Final path; [predict-champion] reasons the most
*underrated genuine contender* whose seeded path is survivable, not the chalk favorite.
