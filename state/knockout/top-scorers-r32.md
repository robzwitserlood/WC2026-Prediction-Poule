# R32 top scorers — Scorito basket

Calibration: expected Scorito points = expected goals × **R32 position multiplier** (DEF/GK **64**, MID **32**, ATT **16** per goal — R32 is the 1× stage, same as the group, per `state/poule-rules.md`). Each alive team plays **one** match, so the goal ceiling is its predicted R32 goals from `state/knockout/predictions-r32.md`; expected goals = team R32 GF × player share of team goals, nudged for penalty/set-piece duty and current tournament form. Submit the top 4; 5–6 are reserves. Re-picked fresh from the 16 alive teams (no carry-forward of eliminated players — Wirtz/Raphinha from the group basket are gone; only Brazil among our group picks' teams is alive, and Raphinha is a doubt).

**The lever, sharper in a single-match knockout:** the realistic per-team ceiling is 0–2 goals, so a striker on the chalk can only bank ~1 goal (16 pts), while one set-piece header or a penalty from a defender/mid returns 64/32. Three of our four submitted picks are **high-multiplier** (one defender at 64, two midfielders at 32). Critically, the field over-picks the strikers; our top pick is a **defender who is literally his team's leading scorer at this tournament** — the single largest mispricing on the board.

> **Position sourcing note (load-bearing):** two of our picks are coded by the **actual group-stage scorers** in `state/results/`, which override the pre-tournament `## Goal threats` lines in the team files:
> - Colombia's group scorer logged as "Munoz 3 goals" / "Jhon Cordoba Munoz" in the team file is, per `state/results/group-r1.md` and `group-r2.md`, **Daniel Munoz** — Colombia's **right-back (DEF)**, scorer of the R1 (40') goal and the R2 (76') winner. Confirmed DEF → the **64×** multiplier applies. This is not an assumption; it is in the results log.
> - Spain's "Jorge Baena 3 goals" in the team file is, per `state/results/group-r3.md`, **Alex Baena** — an attacking **midfielder (MID)**, scorer of 2 vs Saudi Arabia and 1 vs Uruguay. Confirmed MID → the **32×** multiplier applies.

---

## 1. Daniel Munoz — Colombia (DEF) — SUBMIT
- Our sim: Colombia predicted **2** goals vs Ghana (M88, `predictions-r32.md` — decisive 2-0 home win).
- Expected goals: **~0.55** (≈ 45% of Colombia's goals — he scored **3 of their 4 group goals**: R1 40' and the R2 76' winner; an attacking right-back who arrives late in the box, on a tournament heater, vs a Ghana side with **0 clean sheets in 10 WC games** and missing Kudus).
- Expected points: **~35** (0.55 × 64).
- Value angle: the standout value of the entire R32 basket. A **defender worth 4× a striker per goal** who is, by the actual results log, his team's **leading scorer** — the crowd is chasing Luis Diaz (ATT, 16×) while Munoz banks the same team's goals at quadruple the multiplier against the weakest defence left in the round. Highest expected points on the board by a clear margin.

## 2. Alex Baena — Spain (MID) — SUBMIT
- Our sim: Spain predicted **2** goals vs Austria (M83 — Spain 2-1, advances).
- Expected goals: **~0.6** (≈ 40% of Spain's goals — Baena scored **3 of Spain's 5 group goals**, the breakout star; with **Nico Williams OUT** (adductor) and **Pino doubtful**, Spain's attacking creation funnels through Baena and Yamal even more, and Austria's high Rangnick press concedes transition lanes for a runner from deep).
- Expected points: **~19** (0.6 × 32).
- Value angle: a **midfielder at double the striker multiplier** who is Spain's actual top scorer, with two of Spain's other wide threats injured concentrating the goal load on him. The field pays for Yamal (ATT); Baena is the underpriced 32×-per-goal route into the same Spain attack.

## 3. Kevin De Bruyne — Belgium (MID) — SUBMIT
- Our sim: Belgium predicted **2** goals vs Senegal (M81 — Belgium 2-1, advances).
- Expected goals: **~0.5** (≈ 25% of Belgium's goals + a **dead-ball nudge**: primary penalty, free-kick and corner taker; scored vs New Zealand R3; Senegal shipped **8 GA in the group** and push their fullbacks high, exactly the rest-defence KDB's deliveries punish).
- Expected points: **~16** (0.5 × 32).
- Value angle: the textbook penalty-and-set-piece midfielder (32/goal) on a side our card has scoring two, against a leaky Senegal defence. The crowd files him as a creator, not a scorer; his dead-ball duty protects his floor even on a quiet open-play night.

## 4. Kylian Mbappe — France (ATT) — SUBMIT
- Our sim: France predicted **3** goals vs Sweden (M78 — France 3-1, the cleanest mismatch on the card and the **highest team goal ceiling** of any alive side alongside Argentina).
- Expected goals: **~1.0** (≈ 35% of France's goals; **primary penalty taker**; 4 goals in 3 group games, fully fit, the hamstring scare gone; Sweden's high line vs Mbappe's pace in behind is the goal-source our 3-1 is built on).
- Expected points: **~16** (1.0 × 16).
- Value angle: not contrarian, but the highest-ceiling nailed-on striker left, on the joint-top-scoring team in our R32 sim (3-goal ceiling) — passing him over to chase yet another multiplier would be value-for-its-own-sake. He anchors the basket's floor (his ~1.0 expected goals is the highest single-player figure in the pool) while picks 1–3 carry the multiplier upside, and he diversifies us into a fourth team and match.

## 5. Granit Xhaka — Switzerland (MID) — reserve
- Our sim: Switzerland predicted **2** goals vs Algeria (M85 — Switzerland 2-1, advances).
- Expected goals: **~0.45** (captain and **confirmed penalty + free-kick taker** — converted both pens in qualifying, scored vs Canada R3; Algeria shipped **7 GA** in the group, so Switzerland's set-piece volume is high).
- Expected points: **~14** (0.45 × 32).
- Value angle: another penalty-taking midfielder (the right 32× shape) on a side scoring two vs a sieve defence; sits just behind De Bruyne on share/ceiling. Strong swap-in if a submitted MID (Baena, KDB) picks up a knock or is rotated before lock.

## 6. Erling Haaland — Norway (ATT) — reserve
- Our sim: Norway predicted **2** goals vs Ivory Coast (M77 — Norway 2-1, advances).
- Expected goals: **~0.9** (≈ 43% of Norway's goals — **4 group goals** incl. two braces, primary penalty taker, elite volume; the highest pure expected-goal figure of any reserve).
- Expected points: **~14** (0.9 × 16).
- Value angle: the highest-floor striker outside the submitted four — held at reserve only because the 16× multiplier caps his ceiling below the high-multiplier picks above. Promote over Mbappe only if you want to swap one striker for another with marginally higher expected goals; otherwise the multiplier math keeps the MID/DEF picks ahead.

---
Submitted four — expected points: **Munoz ~35** (DEF, the value anchor), **Baena ~19** (MID), **De Bruyne ~16** (MID), **Mbappe ~16** (ATT, the floor). Basket total **~86 expected pts**, spread across four teams (Colombia, Spain, Belgium, France) and four R32 matches for variance control. The tilt is heavier than the group basket on purpose: in a single-match knockout the per-team ceiling is tiny, so one defender's set-piece/box-arrival goal (64×) outweighs any striker, and our top pick is a defender who is demonstrably his team's leading scorer this tournament.
