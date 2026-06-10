#!/usr/bin/env python3
"""Deterministic World Cup 2026 group standings.

Replaces the model-computed table (token-free, no tiebreak slips). Reads group
membership from state/groups.md and predicted scorelines from
state/predictions/round-*.md, then writes state/standings/round-<n>.md.

Usage:
    python3 scripts/standings.py [n]      # standings after round n
    python3 scripts/standings.py          # uses the highest round present

Prediction line format (written by predict-round):
    ## <Home> vs <Away> @ <venue>: <h>-<a>
Team names must match state/groups.md exactly (the source of truth).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GROUPS_MD = ROOT / "state" / "groups.md"
PRED_DIR = ROOT / "state" / "predictions"
STAND_DIR = ROOT / "state" / "standings"

GROUP_ROW = re.compile(r"^\|\s*([A-L])\s*\|\s*(.+?)\s*\|\s*$")
# "## Home vs Away @ venue: h-a"  — score captured from the end, tolerant of en-dash.
MATCH_LINE = re.compile(
    r"^\s*#{1,6}\s*(?P<teams>.+?)\s*@\s*(?P<venue>.+?)\s*:\s*"
    r"(?P<h>\d+)\s*[-–]\s*(?P<a>\d+)\s*$"
)


def load_groups():
    """Return (group_of: team->letter, teams_in: letter->[teams])."""
    group_of, teams_in = {}, {}
    for line in GROUPS_MD.read_text(encoding="utf-8").splitlines():
        m = GROUP_ROW.match(line)
        if not m or m.group(1) == "Group":  # skip header row
            continue
        letter = m.group(1)
        teams = [t.strip() for t in m.group(2).split(",") if t.strip()]
        teams_in[letter] = teams
        for t in teams:
            group_of[t] = letter
    if not teams_in:
        sys.exit("error: no groups parsed from state/groups.md")
    return group_of, teams_in


def parse_match(line, group_of):
    """Return (home, away, h, a) or None if the line is not a scored match."""
    m = MATCH_LINE.match(line)
    if not m:
        return None
    teams = m.group("teams").strip()
    if " vs " not in teams:
        return None
    home, away = (s.strip() for s in teams.split(" vs ", 1))
    for name in (home, away):
        if name not in group_of:
            sys.exit(f"error: team '{name}' (line: {line!r}) is not in state/groups.md")
    if group_of[home] != group_of[away]:
        sys.exit(f"error: {home} and {away} are not in the same group (line: {line!r})")
    return home, away, int(m.group("h")), int(m.group("a"))


def new_stat():
    return {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0}


def apply_match(stats, home, away, h, a):
    for team in (home, away):
        stats.setdefault(team, new_stat())
    sh, sa = stats[home], stats[away]
    sh["P"] += 1; sa["P"] += 1
    sh["GF"] += h; sh["GA"] += a
    sa["GF"] += a; sa["GA"] += h
    if h > a:
        sh["W"] += 1; sa["L"] += 1
    elif h < a:
        sa["W"] += 1; sh["L"] += 1
    else:
        sh["D"] += 1; sa["D"] += 1


def pts(s):
    return 3 * s["W"] + s["D"]


def gd(s):
    return s["GF"] - s["GA"]


def head_to_head(cluster, matches):
    """Mini-table (pts, gd, gf) restricted to matches among the tied cluster."""
    cset = set(cluster)
    h2h = {t: new_stat() for t in cluster}
    for home, away, h, a in matches:
        if home in cset and away in cset:
            apply_match(h2h, home, away, h, a)
    return h2h


def rank_group(teams, stats, matches):
    """Return (ordered_teams, tie_notes). Sound tiebreaks; never silently guesses."""
    present = [t for t in teams if stats[t]["P"] > 0 or True]  # keep all 4, even 0 games
    # Primary: pts -> gd -> gf (FIFA group-stage order).
    present.sort(key=lambda t: (-pts(stats[t]), -gd(stats[t]), -stats[t]["GF"], t))
    notes = []
    # Resolve clusters that are level on all three primary keys.
    i = 0
    ordered = []
    while i < len(present):
        j = i
        key = (pts(stats[present[i]]), gd(stats[present[i]]), stats[present[i]]["GF"])
        while j + 1 < len(present) and (
            pts(stats[present[j + 1]]),
            gd(stats[present[j + 1]]),
            stats[present[j + 1]]["GF"],
        ) == key:
            j += 1
        cluster = present[i : j + 1]
        if len(cluster) == 1 or all(stats[t]["P"] == 0 for t in cluster):
            # Single team, or a not-yet-played group — nothing to flag.
            ordered.extend(cluster)
        else:
            h2h = head_to_head(cluster, matches)
            resolved = sorted(
                cluster,
                key=lambda t: (-pts(h2h[t]), -gd(h2h[t]), -h2h[t]["GF"], t),
            )
            # Detect any sub-tie still unresolved after H2H.
            still = []
            for k in range(len(resolved) - 1):
                a, b = resolved[k], resolved[k + 1]
                if (pts(h2h[a]), gd(h2h[a]), h2h[a]["GF"]) == (
                    pts(h2h[b]),
                    gd(h2h[b]),
                    h2h[b]["GF"],
                ):
                    still.append((a, b))
            tied_names = ", ".join(cluster)
            if still:
                notes.append(
                    f"TIE among [{tied_names}] level on pts/GD/GF *and* head-to-head — "
                    f"order here is provisional; FIFA next applies fair-play points then "
                    f"drawing of lots. Resolve manually before this rank feeds the next round."
                )
            else:
                notes.append(
                    f"Tie among [{tied_names}] on pts/GD/GF broken by head-to-head "
                    f"(pts → GD → goals among them)."
                )
            ordered.extend(resolved)
        i = j + 1
    return ordered, notes


def status_note(team, stats, ordered, n_round):
    """Deterministic, never-overclaiming qualification status."""
    s = stats[team]
    left = 3 - s["P"]
    my_pts = pts(s)
    others = [t for t in ordered if t != team]
    if left == 0:
        pos = ordered.index(team) + 1
        if pos <= 2:
            return "through (top 2)"
        if pos == 3:
            return "3rd — into best-3rd-place pool"
        return "eliminated"
    max_reach = my_pts + 3 * left
    # Eliminated from top 2: >=2 others already strictly above what we can reach.
    locked_above = sum(1 for t in others if pts(stats[t]) > max_reach)
    if locked_above >= 2:
        return f"eliminated from top 2 ({my_pts} pts, {left} game(s) left)"
    # Clinched top 2: at most 1 other could still reach our points (sound, GD-safe).
    can_reach_us = sum(1 for t in others if pts(stats[t]) + 3 * (3 - stats[t]["P"]) >= my_pts)
    if can_reach_us <= 1:
        return f"clinched top 2 ({my_pts} pts)"
    pos = ordered.index(team) + 1
    return f"{my_pts} pts, pos {pos}, {left} game(s) left (max {max_reach})"


def render_group(letter, teams, stats, matches, n_round):
    ordered, tie_notes = rank_group(teams, stats, matches)
    lines = [f"# Group {letter} — after round {n_round}", ""]
    lines.append("| Pos | Team | P | W | D | L | GF | GA | GD | Pts |")
    lines.append("|----:|------|--:|--:|--:|--:|--:|--:|--:|----:|")
    for pos, t in enumerate(ordered, 1):
        s = stats[t]
        lines.append(
            f"| {pos} | {t} | {s['P']} | {s['W']} | {s['D']} | {s['L']} | "
            f"{s['GF']} | {s['GA']} | {gd(s):+d} | {pts(s)} |"
        )
    lines.append("")
    statuses = [f"{t}: {status_note(t, stats, ordered, n_round)}" for t in ordered]
    lines.append("Notes: " + "; ".join(statuses) + ".")
    for tn in tie_notes:
        lines.append(f"- {tn}")
    lines.append("")
    return "\n".join(lines)


def main():
    group_of, teams_in = load_groups()

    # Which rounds to include.
    if len(sys.argv) > 1:
        n_round = int(sys.argv[1])
    else:
        present = sorted(
            int(m.group(1))
            for p in PRED_DIR.glob("round-*.md")
            if (m := re.match(r"round-(\d+)\.md$", p.name))
        )
        if not present:
            sys.exit("error: no state/predictions/round-*.md files found")
        n_round = present[-1]

    # Read predicted matches for rounds 1..n_round.
    matches = []
    for r in range(1, n_round + 1):
        f = PRED_DIR / f"round-{r}.md"
        if not f.exists():
            print(f"warning: {f.name} missing — skipping round {r}", file=sys.stderr)
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            parsed = parse_match(line, group_of)
            if parsed:
                matches.append(parsed)
    if not matches:
        sys.exit(f"error: no scored matches parsed for rounds 1..{n_round}")

    # Per-group stats (all 4 teams seeded so 0-game teams still appear).
    by_group = {}
    for letter, teams in teams_in.items():
        stats = {t: new_stat() for t in teams}
        by_group[letter] = stats
    for home, away, h, a in matches:
        apply_match(by_group[group_of[home]], home, away, h, a)

    # Group matches by letter for head-to-head resolution.
    matches_by_group = {letter: [] for letter in teams_in}
    for home, away, h, a in matches:
        matches_by_group[group_of[home]].append((home, away, h, a))

    out = [f"# WC2026 standings — after round {n_round}", "",
           "_Generated by scripts/standings.py (deterministic). "
           "Notes never overclaim: 'clinched'/'eliminated' are mathematically locked._", ""]
    for letter in sorted(teams_in):
        out.append(render_group(letter, teams_in[letter],
                                by_group[letter], matches_by_group[letter], n_round))

    STAND_DIR.mkdir(parents=True, exist_ok=True)
    dest = STAND_DIR / f"round-{n_round}.md"
    dest.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {dest.relative_to(ROOT)} ({len(matches)} matches, rounds 1..{n_round})")


if __name__ == "__main__":
    main()
