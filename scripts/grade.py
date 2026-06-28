#!/usr/bin/env python3
"""Deterministic grading for the WC2026 prediction pipeline.

Scores each advisor lens (and the decider's final card) against the actual
results, for every stage where results exist. Produces a thin hit-rate /
calibration tally — NOT a mechanical reweighting formula. The round-decider
reads state/grades/scorecard.md as *judgment* about which lens has earned
trust; the panel is never auto-pruned.

What it measures, per lens, per stage:
  - toto hit-rate   : predicted result direction (W/D/L) vs the actual
                      120-minute result (penalties never count toward the score)
  - exact-score rate: predicted scoreline == actual 120-minute scoreline
  - points          : stage-multiplier x (90 exact / 60 toto / 0), display only
  - calibration     : toto hit-rate bucketed by the advisor's own stated
                      Confidence (low/med/high) — are high-confidence calls
                      actually more accurate? (decider emits no confidence, so '-')
  - advance (KO)    : decider only — did the named advancing side actually go through

It joins three files per stage on NORMALISED team names (case/accent folded),
tolerant of home/away orientation differences. On any unmatched line it
FLAG-SKIPs and reports it (unlike scripts/standings.py, which sys.exits) —
knockouts have no group-membership safety net, so a name typo must not abort
the whole run.

The scorecard is REGENERATED from scratch each run (idempotent): every stage
with a results file is graded, so the first knockout run also backfills the 72
group matches once state/results/group-r{1,2,3}.md exist.

Usage:
    python3 scripts/grade.py        # grade every stage that has results
"""

import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
SCORECARD = STATE / "grades" / "scorecard.md"

# Same match-header shape as scripts/standings.py (load-bearing across the repo):
#   "## Home vs Away @ venue: h-a"  — score at the end, tolerant of en-dash.
MATCH_LINE = re.compile(
    r"^\s*#{1,6}\s*(?P<teams>.+?)\s*@\s*(?P<venue>.+?)\s*:\s*"
    r"(?P<h>\d+)\s*[-–]\s*(?P<a>\d+)\s*$"
)
CONF_LINE = re.compile(r"^\s*[-*]\s*Confidence\s*:\s*(low|med|high)\b", re.IGNORECASE)
ADVANCE_LINE = re.compile(r"^\s*[-*]\s*Advance[ds]\s*:\s*(?P<team>.+?)\s*(?:\(|$)", re.IGNORECASE)

GROUP_LENSES = ["stats", "contrarian", "conditions-market"]
KO_LENSES = GROUP_LENSES + ["knockout-context"]

# (label, advice_dir, decider_card, results_file, multiplier, lenses)
# multiplier None = unconfirmed (R32 row is absent from state/poule-rules.md).
STAGES = [
    ("Round 1", "round-1", "predictions/round-1.md", "results/group-r1.md", 1.0, GROUP_LENSES),
    ("Round 2", "round-2", "predictions/round-2.md", "results/group-r2.md", 1.0, GROUP_LENSES),
    ("Round 3", "round-3", "predictions/round-3.md", "results/group-r3.md", 1.0, GROUP_LENSES),
    ("R32", "r32", "knockout/predictions-r32.md", "results/r32.md", None, KO_LENSES),
    ("R16", "r16", "knockout/predictions-r16.md", "results/r16.md", 1.5, KO_LENSES),
    ("QF", "qf", "knockout/predictions-qf.md", "results/qf.md", 2.0, KO_LENSES),
    ("SF", "sf", "knockout/predictions-sf.md", "results/sf.md", 2.5, KO_LENSES),
    ("Final", "final", "knockout/predictions-final.md", "results/final.md", 3.0, KO_LENSES),
]


def norm(name):
    """Fold case + accents + punctuation so 'Türkiye' == 'turkiye'."""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9 ]", "", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def toto(h, a):
    return "H" if h > a else ("A" if a > h else "D")


def split_teams(teams):
    """'Home vs Away' -> (home, away) or None."""
    if " vs " not in teams:
        return None
    home, away = (s.strip() for s in teams.split(" vs ", 1))
    return home, away


def parse_matches(path):
    """Parse scored match lines -> list of dicts (raw + normalised + score + nearby meta).

    Returns the home/away orientation AS LISTED, plus the Confidence and
    Advance lines that follow each header (until the next header).
    """
    out = []
    cur = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = MATCH_LINE.match(line)
        if m:
            pair = split_teams(m.group("teams").strip())
            if pair is None:
                cur = None
                continue
            home, away = pair
            cur = {
                "home": home, "away": away,
                "nh": norm(home), "na": norm(away),
                "h": int(m.group("h")), "a": int(m.group("a")),
                "conf": None, "advance": None,
            }
            out.append(cur)
            continue
        if cur is None:
            continue
        cm = CONF_LINE.match(line)
        if cm:
            cur["conf"] = cm.group(1).lower()
            continue
        am = ADVANCE_LINE.match(line)
        if am:
            cur["advance"] = norm(am.group("team"))
    return out


def index_actuals(matches):
    """frozenset({nh,na}) -> actual record (for orientation-tolerant lookup)."""
    idx = {}
    for r in matches:
        idx[frozenset((r["nh"], r["na"]))] = r
    return idx


def oriented_actual(pred, actual):
    """Return (actual_h, actual_a, actual_advance) in the prediction's orientation."""
    if pred["nh"] == actual["nh"]:
        return actual["h"], actual["a"], actual["advance"]
    # listed the other way round in the results file -> flip the score
    return actual["a"], actual["h"], actual["advance"]


def grade_file(pred_matches, actuals_idx, mult, want_advance):
    """Grade one prediction set against the actuals. Returns a stats dict."""
    g = {
        "n": 0, "toto": 0, "exact": 0, "points": 0.0, "skipped": [],
        "calib": {"low": [0, 0], "med": [0, 0], "high": [0, 0]},
        "adv_n": 0, "adv_hit": 0,
    }
    for p in pred_matches:
        key = frozenset((p["nh"], p["na"]))
        actual = actuals_idx.get(key)
        if actual is None:
            g["skipped"].append(f"{p['home']} vs {p['away']}")
            continue
        ah, aa, a_adv = oriented_actual(p, actual)
        g["n"] += 1
        is_toto = toto(p["h"], p["a"]) == toto(ah, aa)
        is_exact = (p["h"], p["a"]) == (ah, aa)
        if is_toto:
            g["toto"] += 1
        if is_exact:
            g["exact"] += 1
        if mult is not None:
            g["points"] += mult * (90 if is_exact else (60 if is_toto else 0))
        if p["conf"] in g["calib"]:
            g["calib"][p["conf"]][1] += 1
            if is_toto:
                g["calib"][p["conf"]][0] += 1
        if want_advance and p["advance"] and a_adv:
            g["adv_n"] += 1
            if p["advance"] == a_adv:
                g["adv_hit"] += 1
    return g


def pct(hit, tot):
    return f"{100 * hit / tot:.0f}%" if tot else "—"


def calib_str(calib):
    parts = []
    for level in ("high", "med", "low"):
        hit, tot = calib[level]
        if tot:
            parts.append(f"{level} {hit}/{tot} ({pct(hit, tot)})")
    return ", ".join(parts) if parts else "—"


def calib_flag(calib):
    """Flag inversion: low-confidence calls hitting at least as often as high."""
    lo_h, lo_t = calib["low"]
    hi_h, hi_t = calib["high"]
    if lo_t and hi_t and (lo_h / lo_t) >= (hi_h / hi_t):
        return " ⚠ low ≥ high (miscalibrated)"
    return ""


def points_cell(g, mult):
    return "TBD" if mult is None else f"{g['points']:.0f}"


def main():
    if not SCORECARD.parent.exists():
        SCORECARD.parent.mkdir(parents=True, exist_ok=True)

    out = [
        "# Lens scorecard — toto hit-rate & calibration",
        "",
        "_Generated by scripts/grade.py (deterministic). Read by round-decider as **judgment** "
        "about which lens to trust — not a reweighting formula. Toto = correct 120-minute result "
        "(penalties never count). Points scale by stage multiplier and are display-only._",
        "",
    ]

    # cumulative[lens] = aggregate across all graded stages
    cumulative = {}
    graded_any = False
    all_skipped = []

    for label, advice_dir, decider_rel, results_rel, mult, lenses in STAGES:
        results_path = STATE / results_rel
        if not results_path.exists():
            continue
        actuals = index_actuals(parse_matches(results_path))
        if not actuals:
            continue
        graded_any = True

        rows = []  # (name, grade_dict, is_decider)
        # advisor lenses
        for lens in lenses:
            apath = STATE / "advice" / advice_dir / f"{lens}.md"
            if not apath.exists():
                continue
            g = grade_file(parse_matches(apath), actuals, mult, want_advance=False)
            rows.append((lens, g, False))
        # decider final card
        dpath = STATE / decider_rel
        if dpath.exists():
            g = grade_file(parse_matches(dpath), actuals, mult, want_advance=True)
            rows.append(("decider", g, True))

        if not rows:
            continue

        out.append(f"## {label}"
                   + ("  (multiplier TBD — R32 row missing from poule-rules.md)" if mult is None
                      else f"  (×{mult:g})"))
        out.append("")
        out.append("| Lens | N | Toto | Exact | Points | Advance | Calibration (toto hit by confidence) |")
        out.append("|------|--:|-----:|------:|-------:|--------:|--------------------------------------|")
        for name, g, is_dec in rows:
            adv = pct(g["adv_hit"], g["adv_n"]) if is_dec and g["adv_n"] else "—"
            toto_cell = f"{g['toto']}/{g['n']} ({pct(g['toto'], g['n'])})" if g["n"] else "—"
            calib = "—" if is_dec else (calib_str(g["calib"]) + calib_flag(g["calib"]))
            out.append(
                f"| {name} | {g['n']} | {toto_cell} | {g['exact']} | "
                f"{points_cell(g, mult)} | {adv} | {calib} |"
            )
            # accumulate (advisor lenses only; the decider is reported but not a 'lens')
            if not is_dec:
                c = cumulative.setdefault(
                    name, {"n": 0, "toto": 0, "exact": 0,
                           "calib": {"low": [0, 0], "med": [0, 0], "high": [0, 0]}})
                c["n"] += g["n"]; c["toto"] += g["toto"]; c["exact"] += g["exact"]
                for lvl in ("low", "med", "high"):
                    c["calib"][lvl][0] += g["calib"][lvl][0]
                    c["calib"][lvl][1] += g["calib"][lvl][1]
        out.append("")
        skipped = sorted({s for _, g, _ in rows for s in g["skipped"]})
        if skipped:
            all_skipped.extend(f"{label}: {s}" for s in skipped)
            out.append(f"_Unmatched (flag-skipped — check team-name spelling vs results): "
                       f"{'; '.join(skipped)}._")
            out.append("")

    if not graded_any:
        out.append("_No results yet — nothing to grade. (Run match-reporter to write "
                   "state/results/*.md first.)_")
        SCORECARD.write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"wrote {SCORECARD.relative_to(ROOT)} (no results to grade yet)")
        return

    # cumulative summary — the line the decider weighs
    out.append("## Cumulative (all graded stages) — the decider's trust read")
    out.append("")
    out.append("| Lens | N | Toto hit-rate | Exact | Calibration |")
    out.append("|------|--:|--------------:|------:|-------------|")
    for lens in KO_LENSES:
        c = cumulative.get(lens)
        if not c:
            out.append(f"| {lens} | 0 | — (no sample yet) | — | cold-start: panel-average weight |")
            continue
        out.append(
            f"| {lens} | {c['n']} | {pct(c['toto'], c['n'])} | {c['exact']} | "
            f"{calib_str(c['calib'])}{calib_flag(c['calib'])} |"
        )
    out.append("")
    out.append("_Cold-start rule: a lens with no graded sample (e.g. knockout-context before its "
               "first KO stage) gets panel-average weight until it has a real sample._")
    out.append("")

    SCORECARD.write_text("\n".join(out) + "\n", encoding="utf-8")
    msg = f"wrote {SCORECARD.relative_to(ROOT)}"
    if all_skipped:
        msg += f"  ({len(all_skipped)} unmatched line(s) flag-skipped)"
    print(msg)


if __name__ == "__main__":
    main()
