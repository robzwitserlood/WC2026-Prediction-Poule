#!/usr/bin/env python3
"""Deterministic World Cup 2026 knockout-bracket seeding.

Reads the *final* group results (predicted scorelines, rounds 1-3) the same way
scripts/standings.py does, works out the group winners / runners-up / 3rd-placed
teams, picks the 8 best 3rd-placed teams, assigns them to their Round-of-32 slots
by FIFA's Annex C eligibility sets, and writes state/knockout/bracket.md — the
seeded bracket [predict-champion] walks to reason a champion + path.

Zero model tokens, no slips. Like standings.py it never silently guesses: where a
3rd-place cutoff or a slot assignment is genuinely ambiguous it picks a canonical
option and FLAGS it provisional.

Usage:
    python3 scripts/knockout.py        # needs rounds 1-3 predicted for every group

The R32 slot map / eligibility sets below are FIFA's (see state/knockout-bracket.md).
"""

import sys
from pathlib import Path

# Reuse the standings engine — same parsing, same tiebreaks, no duplication.
from standings import (  # noqa: E402  (sibling script on sys.path[0])
    load_groups,
    parse_match,
    apply_match,
    new_stat,
    pts,
    gd,
    rank_group,
    PRED_DIR,
    ROOT,
)

KO_DIR = ROOT / "state" / "knockout"

# Round-of-32 slot map. Each entry: match -> (home_token, away_token).
# Tokens: ("W", X)=winner of group X, ("RU", X)=runner-up of X, ("3", None)=a 3rd-placed team.
R32 = [
    (73, ("RU", "A"), ("RU", "B")),
    (74, ("W", "E"), ("3", None)),
    (75, ("W", "F"), ("RU", "C")),
    (76, ("W", "C"), ("RU", "F")),
    (77, ("W", "I"), ("3", None)),
    (78, ("RU", "E"), ("RU", "I")),
    (79, ("W", "A"), ("3", None)),
    (80, ("W", "L"), ("3", None)),
    (81, ("W", "D"), ("3", None)),
    (82, ("W", "G"), ("3", None)),
    (83, ("RU", "K"), ("RU", "L")),
    (84, ("W", "H"), ("RU", "J")),
    (85, ("W", "B"), ("3", None)),
    (86, ("W", "J"), ("RU", "H")),
    (87, ("W", "K"), ("3", None)),
    (88, ("RU", "D"), ("RU", "G")),
]

# The 8 winner-vs-3rd slots and which groups' 3rd-placed team each may take (Annex C).
THIRD_SLOTS = {
    74: ("E", set("ABCDF")),
    77: ("I", set("CDFGH")),
    79: ("A", set("CEFHI")),
    80: ("L", set("EHIJK")),
    81: ("D", set("BEFIJ")),
    82: ("G", set("AEHIJ")),
    85: ("B", set("EFGIJ")),
    87: ("K", set("DEIJL")),
}

# Later rounds: pure structure (concrete teams unknown until matches are played).
LATER_ROUNDS = [
    ("Round of 16", [
        (89, 74, 77), (90, 73, 75), (91, 76, 78), (92, 79, 80),
        (93, 83, 84), (94, 81, 82), (95, 86, 88), (96, 85, 87),
    ]),
    ("Quarterfinals", [
        (97, 89, 90), (98, 93, 94), (99, 91, 92), (100, 95, 96),
    ]),
    ("Semifinals", [
        (101, 97, 98), (102, 99, 100),
    ]),
    ("Final", [
        (104, 101, 102),
    ]),
]


def collect_matches(group_of):
    """All parsed scorelines from rounds 1-3 (every group-stage match)."""
    matches = []
    for r in (1, 2, 3):
        f = PRED_DIR / f"round-{r}.md"
        if not f.exists():
            sys.exit(
                f"error: {f.relative_to(ROOT)} missing — the bracket needs all of "
                f"rounds 1-3 predicted before it can be seeded."
            )
        for line in f.read_text(encoding="utf-8").splitlines():
            parsed = parse_match(line, group_of)
            if parsed:
                matches.append(parsed)
    return matches


def assign_thirds(qual_groups):
    """Assign the 8 qualifying 3rd-place groups to the 8 winner-vs-3rd slots.

    Returns (assignment: match->group, unique: bool). Enumerates valid complete
    assignments over the Annex C eligibility sets; the first in (slot, group) order
    is canonical, and `unique` is False if more than one valid assignment exists.
    """
    slots = sorted(THIRD_SLOTS)
    solutions = []

    def bt(i, used, acc):
        if len(solutions) >= 2:  # two is enough to prove non-uniqueness
            return
        if i == len(slots):
            solutions.append(dict(acc))
            return
        slot = slots[i]
        _, elig = THIRD_SLOTS[slot]
        for g in sorted(qual_groups):
            if g in used or g not in elig:
                continue
            acc[slot] = g
            bt(i + 1, used | {g}, acc)
            del acc[slot]

    bt(0, set(), {})
    if not solutions:
        return None, False
    return solutions[0], len(solutions) == 1


def main():
    group_of, teams_in = load_groups()
    matches = collect_matches(group_of)

    # Build per-group stats and the match list per group (for head-to-head).
    by_group = {letter: {t: new_stat() for t in teams} for letter, teams in teams_in.items()}
    matches_by_group = {letter: [] for letter in teams_in}
    for home, away, h, a in matches:
        g = group_of[home]
        apply_match(by_group[g], home, away, h, a)
        matches_by_group[g].append((home, away, h, a))

    # Every team must have played its 3 group games, or the bracket is premature.
    stat_of = {}
    incomplete = []
    for letter, teams in teams_in.items():
        for t in teams:
            stat_of[t] = by_group[letter][t]
            if by_group[letter][t]["P"] != 3:
                incomplete.append(f"{t} ({by_group[letter][t]['P']}/3)")
    if incomplete:
        sys.exit(
            "error: group stage not complete — these teams have not played 3 games: "
            + ", ".join(incomplete)
            + ". Predict rounds 1-3 for all groups first."
        )

    # Rank each group; pull winner / runner-up / 3rd.
    winners, runners, thirds_by_group, group_notes = {}, {}, {}, []
    for letter in sorted(teams_in):
        ordered, notes = rank_group(teams_in[letter], by_group[letter], matches_by_group[letter])
        winners[letter] = ordered[0]
        runners[letter] = ordered[1]
        thirds_by_group[letter] = ordered[2]
        for nt in notes:
            group_notes.append(f"Group {letter}: {nt}")

    # Rank the twelve 3rd-placed teams: pts -> GD -> GF (FIFA order); top 8 qualify.
    thirds = sorted(
        teams_in,
        key=lambda L: (
            -pts(stat_of[thirds_by_group[L]]),
            -gd(stat_of[thirds_by_group[L]]),
            -stat_of[thirds_by_group[L]]["GF"],
            thirds_by_group[L],
        ),
    )
    qual_letters = thirds[:8]
    out_letters = thirds[8:]

    boundary_flag = None
    if out_letters:
        a, b = thirds_by_group[thirds[7]], thirds_by_group[thirds[8]]
        if (pts(stat_of[a]), gd(stat_of[a]), stat_of[a]["GF"]) == (
            pts(stat_of[b]), gd(stat_of[b]), stat_of[b]["GF"]
        ):
            boundary_flag = (
                f"8th vs 9th best 3rd ([{thirds[7]}: {a}] vs [{thirds[8]}: {b}]) are level on "
                f"pts/GD/GF — who qualifies is provisional (FIFA then applies fair-play points, "
                f"then drawing of lots). Resolve by hand before trusting the bracket."
            )

    assignment, unique = assign_thirds(set(qual_letters))
    if assignment is None:
        sys.exit(
            "error: no valid Annex C assignment for qualifying 3rd-place groups "
            f"{sorted(qual_letters)} — check the predicted standings."
        )

    def resolve(token, match_no):
        kind, grp = token
        if kind == "W":
            return f"{winners[grp]} (1{grp})"
        if kind == "RU":
            return f"{runners[grp]} (2{grp})"
        grp3 = assignment[match_no]
        return f"{thirds_by_group[grp3]} (3{grp3})"

    # ---- Render ----
    out = [
        "# WC2026 knockout bracket — seeded from predicted final group standings",
        "",
        "_Generated by scripts/knockout.py (deterministic) from state/predictions/round-1..3.md._",
        "_Slot map + Annex C eligibility: state/knockout-bracket.md. Concrete teams shown for the_",
        "_Round of 32; later rounds stay structural (winners unknown until played)._",
        "",
        "## Qualified 3rd-placed teams (ranked)",
        "",
        "| Rank | Group | Team | Pts | GD | GF |",
        "|-----:|:-----:|------|----:|---:|---:|",
    ]
    for i, L in enumerate(thirds, 1):
        t = thirds_by_group[L]
        s = stat_of[t]
        mark = "✓" if L in qual_letters else "—"
        out.append(f"| {i} {mark} | {L} | {t} | {pts(s)} | {gd(s):+d} | {s['GF']} |")
    out.append("")
    out.append(f"Qualifying 3rd-place groups: {', '.join(sorted(qual_letters))}.")
    if not unique:
        out.append(
            "- NOTE: more than one valid Annex C slot assignment exists for these groups; "
            "the bracket below uses the canonical one — treat the 3rd-place pairings as provisional."
        )
    if boundary_flag:
        out.append(f"- NOTE: {boundary_flag}")
    for gn in group_notes:
        out.append(f"- {gn}")
    out.append("")

    out.append("## Round of 32")
    out.append("")
    out.append("| Match | Home | Away |")
    out.append("|------:|------|------|")
    for match_no, home_tok, away_tok in R32:
        out.append(
            f"| {match_no} | {resolve(home_tok, match_no)} | {resolve(away_tok, match_no)} |"
        )
    out.append("")

    for title, pairs in LATER_ROUNDS:
        out.append(f"## {title}")
        out.append("")
        out.append("| Match | Home | Away |")
        out.append("|------:|------|------|")
        for row in pairs:
            match_no, hm, am = row
            out.append(f"| {match_no} | Winner M{hm} | Winner M{am} |")
        out.append("")

    KO_DIR.mkdir(parents=True, exist_ok=True)
    dest = KO_DIR / "bracket.md"
    dest.write_text("\n".join(out), encoding="utf-8")
    print(
        f"wrote {dest.relative_to(ROOT)} — qualifiers: 24 group top-2 + 8 best 3rds "
        f"({', '.join(sorted(qual_letters))})"
        + ("" if unique else "; 3rd-place assignment PROVISIONAL (non-unique)")
        + ("; 3rd-place CUTOFF tie flagged" if boundary_flag else "")
    )


if __name__ == "__main__":
    main()
