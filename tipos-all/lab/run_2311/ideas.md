# New prize-side ideas (subagent 5), pre-registered

The plan is in `ideas_prereg.md`, written 2026-11-22T23:32:15Z before any test was run. There are 10 hypotheses, corrected with Holm at α = 0.05. A hypothesis counts as practically relevant only if it adds at least 0.5 pp of expected return per 1 € **and** changes the ticket.
Scripts are in `scripts/ideas_*.py` (run with `python3 -I`, fixed seeds). Results are in `ideas.json`, with details in `ideas_ev_results.json`, `ideas_van_results.json`, `ideas_rules_results.json` and `ideas_h1_stability.json`.

## Rules (herný plán čl. 29/34), confirmed in the data
- **EV, 5+1 … 3+0:** pure pari-mutuel. The prize is a share of the prize fund (57.9 % of stakes) split equally among winners, with **no minimum**. The realised shares match the rules: 3+0 is 15.4 % against 15.6 % in the rules, and 4+0 is 6.22 % against 6.25 %. In premium months the shares are exactly ×2. So ticket popularity matters for every lower tier, and no floor or cap protects you.
- **EV, 6+0 (30 000 €) and 6+1 (480 000 €):** these are *shared* pools. 6+0 had 2–3 winners in 13 of 142 draws, against 9.2 expected under uniform play, and 71 winners in total against 57 expected.
- **VAN, 10/1, 9/2 and 8/3:** fixed at 200, 20 and 3 € in all 410 draws, whatever the number of winners. Only the 100 000 € is shared. For a random-looking ticket the expected number of co-winners is 0.13, so the most that unpopularity can add is **1.2 pp** of stake.
- **Extra number (EV):** it never changes P(any prize), because 3+0 already pays. For 3 € on a Monday, P(any prize) is: 2 EV fields with no common numbers **20.05 %**, 1 EV + 1 VAN 17.84 %, 2 VAN 16.71 %. Nothing found here improves on the 20.05 %.

## Tests (walk-forward, Freedman–Lane permutation R = 1999; VAN H9 against random 11-number sets, R = 9999)
| | idea | p | p Holm | effect, pp per 1 € | verdict |
|---|---|---|---|---|---|
| H1 | EV: players avoid consecutive pairs | 0.0005 | **0.0045** | 1.00 pre-registered / **0.31** post hoc within the data range | see below |
| H2 | EV: bet-slip rows/columns (generic grids 5–10) | 0.124 | 0.74 | 0.29 | no |
| H3 | EV: clustering in 1–12 | 0.92 | 1 | 0.05 | no |
| H4 | EV: copying the previous draw, the last jackpot combo or hot numbers | 0.71 | 1 | 0.05 | no |
| H5 | EV: spread (SD) of the numbers | 0.010 | 0.07 | 0.26 | no |
| H6 | EV: arithmetic progressions / multiples of 5 | 0.72 | 1 | 0.01 | no |
| H7 | EV: Thursday players have their own popularity profile | 0.44 | 1 | 0.00 | no |
| H8 | EV: premium-month players have their own popularity profile | 0.58 | 1 | 0.00 | no |
| H9 | VAN: pattern tickets are over-played | 0.0001 | **0.001** | 0 for the recommended ticket | significant, no money effect |
| H10 | EV: extra number chosen from your own main numbers | 0.002 | **0.016** | 0.18 | significant, below the threshold |

**H1 (new for EV, robust).** Each consecutive pair in the draw lowers the number of winners:
- 3-hit winners by **1.2 %** (SE 0.2 %);
- 4-hit winners by **6.2 %** (SE 0.55 %).

Out of sample, adding the pair term cuts the 4-hit prediction error (MSE) by 44 %. The effect holds in 2024–25 and in 2025–26, on Mondays and on Thursdays, and is roughly linear across 0–3 pairs.

The pre-registered money step gave **+1.0 pp per €**, which formally passes the threshold. That value, however, comes from extreme fields such as 18-19-20-21-22-23. A field like that has 5 pairs, while the draws only show 0–3 pairs, and VAN shows that pattern tickets are heavily played. Restricted to at most 2 pairs per field and no run of 3, the gain is **+0.31 pp**. That is below the threshold and works out to about 1 cent per 3 €.

**My verdict:** the statistics are solid and the money is marginal. The practical rule is that 1–2 consecutive pairs per field are good (players avoid them), but long runs are not. This replaces the wording "no three in a row"; the rule itself stays.

Example field pair within the data range, from the full-sample model: {1 2 14 19 20 23} and {10 15 16 18 21 22}. It is worth 33.7 % in the lower tiers, against 31.4 % for a random ticket.

**H9.** Odd/even VAN tickets are played by hundreds of people:
- 10.10.2025: 1 144 winners in the 2-hit tier against 358 expected;
- 2026: still +190 to +320 extra winners whenever odd or even had 9 of the 11 drawn numbers.

This only confirms the existing advice ("no odd/even/half tickets or their complements"). The recommended ticket does not change.

**H10.** When the drawn extra number is also among the 6 main numbers, the share of "+1" winners is 8 % higher among 4-hit winners. In practice: pick an extra number that is not among your own 6 numbers. It costs nothing, but it is worth only 0.18 pp.

## Bottom line
- **Chance of any prize:** nothing new raises it above 20.05 % per 3 €.
- **Prize size:** the only new lever is consecutive pairs in EV, worth about +0.3 pp within the data range (+1.0 pp under the pre-registered extrapolation).
- **Unchanged:** day of week, premium-month population, slip geometry, birthday numbers and copying recent draws change nothing.
