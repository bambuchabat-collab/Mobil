# Red team: run_2311 claims and the final EV tickets for Monday 23.11.2026

The red team tried to refute P1–P6 and to find errors in the tickets, odds and returns. Every script was written from scratch. It is in `scripts/redteam_*.py` and runs with `python3 -I` under fixed seeds. The script outputs are `redteam_{a,b,c,d,e,f,g,p5}.json`, and the summary is `redteam.json`.

Data checked: `data/ev.json` (sha256 d2aff931…f7f43e) and `data/van.json` (8d367f7d…ef58c3f). Both match `SHA256SUMS`.

In this document, "gain" means the % increase of the tier 3–5 return over a uniformly random field. 1 % of gain ≈ 0.003 € per 1 € staked.

## Verdicts

| Claim | Verdict | Key evidence |
|---|---|---|
| P1 per-number popularity | **SURVIVES** (main numbers); extra-number part **WEAKENED** | No leakage found. A minimal walk-forward from past draws only gives corr 0.68 / 0.38 / 0.21 for 3/4/5 matches, or 0.70 / 0.54 / 0.28 with a pair covariate (p ≤ 0.015). The claim's 0.81/0.64/0.42 comes from a more efficient model. The pooled extra shares are slightly contaminated by the 1–4 era. |
| P2 consecutive pairs | **SURVIVES** | Effect per pair with all 27 number dummies (OLS, no shrinkage): −1.2 % / −6.1 % / −14.1 %. Pairs of unpopular numbers behave like other pairs. Out of sample, adding the pair term cuts the error (MSE) by 12 / 43 / 33 %. A 3-pair field is not an extrapolation. |
| P3 +13.2 % for the recommended pair | **WEAKENED** | Independent model: +12.8 % with the claim's extra shares, **+11.4 %** with 2026 extras (CI 10.0–12.4), +10.4 % when fitted on the post era only. Honest split-half: +8.5 % / +9.9 %. The extra-number bonus is about 1.7 %, not 3.5 %. Best estimate **≈ +10 %** (range 8.5–12). Return ≈ **0.52–0.55** per 1 €. |
| P4 extra taken from own 6 | **SURVIVES** (statistically), negligible in money | Independent test (permutation that reassigns the main-number sets across draws): p = 0.004. The +1 share rises +1.9 % / +7.4 % / +9.2 % when the drawn extra is also a drawn main number. Only 30 draws carry the effect. Worth 0.17 pp. The tickets already comply. |
| P5 VAN odd/even, fixed tiers | **SURVIVES** | 0 of 410 draws break the fixed tiers 200/20/3 €. The cells where odd/even tickets land show mean z = 10.2, against a null 99 % quantile of 2.1 (p = 0.0002). |
| P6 exact odds and returns | **SURVIVES** | Brute-force enumeration gives 29677/148005 = 20.051 %, 1/148 005 and 1/1 036 035. Returns: 0.4909 (3 % PV), 0.5113 (0 %), 0.4796 (5 %). The herný plán text confirms the 6+1 and 6+0 sharing rules. |
| **Final tickets** | **KEEP** | All constraints pass. No alternative is better beyond noise. |

## (a) Leakage and an independent walk-forward (P1) — `redteam_a_walkforward.py`

**Leakage audit of `popularity.py`:**
- log(bets) is centred on the full-sample mean. The intercept is unpenalised, so this shift is absorbed exactly and leaks nothing.
- λ (LOO), τ² and the extra shares are all fitted inside each training window.
- The premium dummy comes from calendar months (decisions are published in advance).
- The era dummy is known in advance.

Nothing in the walk-forward is fitted on future draws. One minor item: `ideas_ev.py` uses ridge λ = 2 taken from the earlier C1 fit (data up to 12.11), a tiny hyper-parameter look-ahead. My own walk-forward makes it moot.

**Minimal estimator.** For each draw t, using only draws before t:
- fit an OLS covariate baseline;
- β_i = (26/21)·(mean residual of past draws containing i − mean residual);
- predict p_t = Σ_{i∈D_t} β_i.

There is no ridge and no tuning. The p-values come from 20 000 label permutations.

| subset (train + evaluate) | n | 3-match | 4-match | 5-match |
|---|---|---|---|---|
| all draws | 130 | **0.68** (p 5e-5) | **0.38** (3e-4) | 0.21 (0.015) |
| all, pair covariate in baseline | 130 | 0.70 | 0.54 | 0.28 (0.005) |
| no covariates, local baseline | 112–140 | 0.70 | 0.38 | 0.19 (0.02) |
| drop 2024 | 99 | 0.62 (4e-4) | 0.31 (0.012) | 0.10 (0.18, n.s.) |
| drop premium months | 113 | 0.73 | 0.41 | 0.23 (0.013) |
| Monday only | 99 | 0.70 | 0.37 (0.002) | 0.23 (0.02) |
| 2026 only (training 25–76 draws) | 52 | 0.55 (0.002) | 0.08 (n.s.) | 0.03 (n.s.) |

- The OOS correlation is clearly positive for 3 and 4 matches in every subset with enough training draws. After Holm over 15 tests, the 3-match results are significant in every subset and the 4-match results in all but drop-2024 and 2026-only.
- 5 matches is weak, and not significant after Holm.
- My post-era ranking correlates 0.87 with the claimed ranking. Number effects estimated on the two halves of the post era correlate 0.54 (3-match) and 0.41 (4-match): stable, but noisy.

**Extra numbers.** The claimed relative popularity of 5/6/7 = 0.86 pools the 2024 draws, when the extra was 1–4 and its share was ~0.25, into extras 1–4. Estimates without that contamination:

| period | relative popularity of 5/6/7 |
|---|---|
| post era (from Oct 2024) | 0.88 |
| 2026 | 0.90–0.91 |
| 2026 H2 | 0.91–0.92 |

The "drift" is partly real (2025 0.87–0.89, 2026 0.91) and partly the artefact. The extra walk-forward calibration slope of 0.51 is consistent with the artefact.

## (b) Pairs vs per-number popularity (P2) — `redteam_b_pairs.py`

All fits include the 27 number dummies without shrinkage, so popularity cannot leak into the pair term.

**Effect per pair:**

| fit | 3-match | 4-match | 5-match |
|---|---|---|---|
| all draws (SE in log units) | −1.2 % (0.002) | −6.1 % (0.006) | −14.1 % (0.017) |
| post era only | −1.3 % | −6.0 % | −14.0 % |

**Confounding with unpopular numbers: none.**

| pair type | 3-match | 4-match | 5-match |
|---|---|---|---|
| both numbers among the 13 least popular | −0.8 % | −4.5 % | −14.3 % |
| all other pairs | −1.3 % | −6.6 % | −14.0 % |

Pairs of unpopular numbers do not carry more of the effect.

**Related "spread" preference.** Numbers two apart are also slightly avoided: −0.3 / −2.3 / −4.3 %. Gap-3 shows nothing. This is consistent with players spreading their numbers.

**Past-only walk-forward.** Adding the pair term cuts OOS MSE by 12 / 43 / 33 % (paired t 1.6 / 4.2 / 3.7). The coefficient never changes sign over time.

**Support:**
- Draws with 0/1/2/3 pairs: 52 / 60 / 51 / 7. Uniform play would give 25 / 44 / 25 / 5 %.
- Dummy fits match the linear model up to 3 pairs. For example, at 4 matches the dummies give −0.05 / −0.12 / −0.19 against linear −0.06 / −0.12 / −0.19.
- Field 1 (3 pairs) wins 5-match only in draws with 2 pairs (80 %) or 3 pairs (20 %). Its 4-match draws have ≤ 2 pairs in 90 % of cases. That is inside the observed range.
- A saturating (dummy) model values the tickets at +11.44 %, against +11.40 % for the linear model. **No extrapolation penalty.**

**≤ 2 pairs per field** (red-team model, bootstrap with 200 refits). Each difference is gain(FINAL) − gain(best pair of that class), in % of tier 3–5 value:
- The best ≤ 2-pair alternative is 0.5 % lower (CI −0.7…+1.8; P(final better) = 0.79). That is noise either way, about 0.002 € per 1 €.
- Restricting to ≤ 1 pair costs 2.5 % (CI 1.3–3.7). Restricting to no pairs costs 4.4 % (CI 3.3–5.7).
- So pairs matter, but 2 vs 3 pairs does not.

## (c) Money (P3) — `redteam_model.py`, `redteam_c_money.py`, `redteam_g_interaction.py`

**Model, written independently:**
- per tier, a ridge regression on [era, Thursday, premium, log bets, #pairs, 27 numbers], λ chosen by LOO (1 / 3 / 10);
- exact enumeration over all 296 010 draws;
- extra factors from the pool shares of 2026 normal months;
- the DP and the brute force agree.

| FINAL (1 2 14 15 20 21 + 6 / 10 16 18 19 23 24 + 7) | gain vs random |
|---|---|
| claim (subagent 4) | +13.2 % (CI 12.2–14.3) |
| red-team model, the claim's pooled extra shares | +12.8 % |
| red-team model, post-era extra shares | +12.3 % |
| red-team model, **2026 extra shares** | **+11.4 %** (bootstrap 400×: mean 11.2, CI 10.0–12.4) |
| red-team model, 2026-H2 extra shares | +11.2 % |
| model fitted on the post era only / on 2025–26 only | +10.4 % / +10.5 % |
| honest selection: pair chosen on one half, scored on the other half's model | +8.5 % and +9.9 % |
| FINAL scored on each half's model | +9.9 % and +11.3 % |

The gain breaks down as follows:
- **Main numbers:** +8.9 % (CI 7.6–10.0); +5.1 % without the pair term.
- **Extra numbers:** +2.3 % with 2026 shares; the claim says +3.5 %.
- **Tier factors:** 3-match ×1.037, 4-match ×1.11, 5-match ×1.32 (CI 1.25–1.38).

**New finding: a main–extra interaction.** Players who share unpopular main numbers have more uniform extra numbers (quick-pick-like):
- In draws whose main numbers are in the unpopular third, 5/6/7 are at 0.90–0.92. In the popular third they are at 0.85–0.87.
- The interaction coefficient is δ = 0.147 (null SD 0.037, p = 0.00015). It is still p = 0.00015 without draws where the extra is also a main number, and p = 0.003 in 2026 alone.
- Applied at the winning draws of the final fields, the extra bonus falls from 2.4 % / 2.1 % to **1.8 % / 1.7 %**.

So the claimed +13.2 % is overstated by roughly 2–4 points:
- about 1.4 points from the extra-share era contamination and drift (+12.8 % → +11.4 %);
- about 0.5 from the interaction;
- about 1–2 from selection and model choice.

The claimed CI is too narrow because it covers only sampling noise. **Best estimate: +10 % (plausible 8.5–12 %).**

**Return per 1 € (normal month):**

| | 3 % PV | 0 % PV |
|---|---|---|
| population average (low tiers 0.3107 + top tiers) | 0.491 | 0.511 |
| FINAL, red-team model (+11.4 %) | 0.529 | 0.549 |
| FINAL, best estimate (+10 %, plus ~0.003 from 6+0/6+1 sharing) | ≈ 0.528 | ≈ 0.548 |
| FINAL, plausible range (+8.5 … +12 %) | 0.523 | 0.554 |

The claim says 0.53–0.55. That is only slightly optimistic: **0.52–0.55** is the honest range. The percentage gain is overstated more than the return, because 3 points of gain are only about 0.01 € per 1 €. The stake still loses about 45–48 %.

## (d) Extra number among own 6 (P4) — `redteam_d_extra.py`

**Identifiable from aggregates.** If a ticket's extra were independent of its main numbers, the share of m-hit winners holding the drawn extra could not depend on whether that extra is also a drawn main number. A coupling makes it depend.

**Independent test.**
- Data: the 142 post-era draws, with drawn-extra fixed effects.
- Null: the main-number sets are reassigned across draws, 20 000 times.
- Result: p = 0.004 (0.0035 including 5-match).
- Effect when the drawn extra is a drawn main number: +1.9 % / +7.4 % / +9.2 % at 3/4/5 matches.
- Implied share of tickets that take their extra from their own six numbers: 4 % (from 3-match) to 10 % (from 4-match).
- The 3- and 4-match implied shares are only loosely consistent, and the effect rests on 30 draws.

**Money:** 0.17 pp per 1 € (extra outside your own field minus inside).

**Final tickets:** extra 6 ∉ {1 2 14 15 20 21} and 7 ∉ {10 16 18 19 23 24}, and neither extra is in the other field. No change is needed.

## (e) Odds and returns (P6) — `redteam_e_odds.py`, herný plán

Brute force over 296 010 × 7 outcomes for the final tickets:

| quantity | value |
|---|---|
| P(any prize) | 29677/148005 = 20.051 % |
| P(6 main on either field) | 1/148 005 |
| P(6+1 on either field) | 1/1 036 035 |
| P(both fields win) | 0.135 % |

Per-field tier probabilities: 3+0 7.70 %, 3+1 1.28 %, 4+0 0.912 %, 4+1 0.152 %, 5+0 0.0365 %, 5+1 0.0061 %.

**Returns.** Inputs:
- low tiers: realised 0.3107 in 2026 normal months (0.3138 by the rules, minus rounding);
- November 2026 draws: 0.309–0.314, i.e. not a premium month;
- Monday bets: 104 818;
- 6+1 as 120 monthly instalments, discounted;
- Poisson sharing.

Results: 0.4909 / 0.5113 / 0.4796 at 3 / 0 / 5 % PV. This reproduces `returns.md`.

**Herný plán** (fetched 23.11.2026; plan 000191/2026, effective 18.03.2026):
- 6+1: 480 000 € fixed; 2 winners get 480 000/2 each; ≥ 3 winners share 720 000 €; ≥ 7 winners are paid as a lump sum;
- 6+0: 30 000 € shared;
- tiers 3–8: 1.5 / 4.3 / 4.4 / 10.8 / 6.2 / 27.0 % of 57.90 %, rounded down to 0.10 €.

All confirmed. The premium check in `premiums.md` was not re-fetched, but the data agree with it: November draws are normal.

## (f) Final tickets — `redteam_f_tickets.py`, `redteam_c_money.py`

**Constraints, all pass:**
- 6 distinct numbers of 1–27 per field;
- the fields are disjoint;
- no run of 3;
- no 3-term arithmetic progression (none found in either field);
- extras 6 and 7 are in {5,6,7} and differ.
- Consecutive pairs: field 1 has 3, field 2 has 2.

**Popularity ranks** (claimed order, 1 = least popular):
- field 1: 20 → 1, 14 → 2, 15 → 3, 1 → 4, 2 → 7, 21 → 15;
- field 2: 16 → 5, 18 → 6, 10 → 8, 23 → 9, 19 → 12, 24 → 14.

**Caveats (none is a failure):**
1. **21 and 24 are of average popularity** (relative frequency 1.00) and are there for the pair value. A pair built only from the 12 least popular numbers (10 14 19 20 22 23 + 5 / 1 2 15 16 18 26 + 6) is 0.7 % lower (CI −0.5…+1.8): no real difference.
2. **"No equal steps."** Read as "no 3-term AP" (the stated definition), it passes. Read as "all gaps distinct", both fields fail: the gaps are 1,12,1,5,1 and 6,2,1,4,1. So would every field with ≥ 2 pairs.
3. **Grid alignment.** Field 2 has 18 19 23 24 on one row of an 8-wide grid. 15 % of random fields have ≥ 4 numbers on some line of that grid, and bet-slip geometry (H2) was not significant. Field 1 has at most 3 numbers on any line for every grid width tested.
4. **Overlap with earlier project tickets.** The final fields share 4 + 4 numbers with the earlier project tickets (1 2 14 20 22 23 + 6 / 8 10 15 16 18 19 + 5). This is irrelevant for co-winners, since others cannot see the repository. Under the red-team model, the earlier pair is the best "≤ 2 pairs" pair, 0.5 % below FINAL (n.s.).

**Comparison** (red-team model, 2026 extras; FINAL +11.40 %):

| alternative | gain | FINAL − alternative (bootstrap) |
|---|---|---|
| runner-up 1 2 15 16 18 19 + 6 / 10 14 20 21 23 24 + 7 | +11.42 % | −0.02 (CI −0.14…+0.09) |
| best under user constraints (= runner-up fields, extras 5/6) | +11.53 % | −0.13 (CI −0.9…+0.7) |
| best with ≤ 2 pairs per field | +10.90 % | +0.5 (CI −0.7…+1.8) |
| best from the 12 least popular numbers only | +10.77 % | +0.7 (CI −0.5…+1.8) |
| best with ≤ 1 pair per field | +8.96 % | +2.5 (CI 1.3–3.7) |
| best with no pairs | +7.03 % | +4.4 (CI 3.3–5.7) |

**Decision: KEEP**
- Field 1: `1 2 14 15 20 21` + extra **6**
- Field 2: `10 16 18 19 23 24` + extra **7**

No constraint fails, and no alternative is better beyond noise. The runner-up is exactly equivalent. Any assignment of two different extras from 5/6/7 is equivalent too.

**Corrections to carry into the write-up:**
- The gain is about +10 %, not +13 %.
- The return is about 0.52–0.55 per 1 €.
- Extras 5/6/7 are about 0.91 of average popularity in 2026, and the extra bonus for unpopular fields is about 1.7 %.
- The chance of a prize is unchanged at 20.05 %.
