# Red team: the anti-hit study of 25.11.2026 (VAN, 30 rules)

Scope: `harness.py`, `aggregate.py`/`aggregate.json`, all `agents/A*_prereg.md`, `agents/A*.py`, `agents/A*.json`, plus the
ticket the lead plans to give the user. Everything was re-run independently with fixed seeds (`python3 -I -B`, numpy only).
The scripts are `redteam_harness_mc.py`, `redteam_leak.py`, `redteam_prereg.py`, `redteam_stats.py`,
`redteam_ticket.py` and `redteam_build.py`. Their outputs are `redteam_*.json`, and `redteam.json` holds all verdicts.

## Verdicts

| Check | Verdict |
|---|---|
| Harness (exact null, p calibration) | **HARNESS OK** |
| Leakage | **none** for A1 through A10. All 30 rules pass a dynamic future-poisoning test, and both positive controls are caught. |
| Pre-registration | **ok, with minor deviations** (listed in section 3). None of them changes the conclusion. |
| Holm survivors (30 rules) | **none**. The smallest p is 0.0141 (Holm 0.42). The smallest p_le3 is 0.0266 (Holm 0.80). BH also gives none. |
| Ticket 1 4 7 8 10 11 14 16 18 20 21 | **TICKET OK**. There is one optional note on prize sharing in section 5. |

I tried to overturn the result and could not. All 30 reported results reproduce bit-exactly from the agents' code, and no rule
sees its target draw. The best rule, A7 R2, fades in the second half of the data. The 30 p-values, taken together, are
consistent with chance.

## 1. Harness correctness

- **Hit pmf.** I simulated 1 000 000 pairs of random ticket and random draw *as sets*, so the check does not use the closed
  form. The counts match the hypergeometric 11-of-22 pmf: chi2 = 7.06 with df = 9, mean 5.4999 (exact 5.5), variance 1.437
  (exact 1.4405).
- **20 000 random-ticket runs through the real `harness.evaluate`** (seed 2511, real 412 draws, n = 382):
  - The mean of the mean hits is 5.4995. Its sd is 0.0613, against 0.0614 expected.
  - p_mean_lower: P(p ≤ α) is 0.0012 / 0.0099 / 0.0137 / 0.0468 / 0.096 / 0.494 at α = 0.001 / 0.01 / 0.014 / 0.05 /
    0.1 / 0.5.
  - KS in the anti-conservative direction gives D+ = 0.0058, below the 5 % critical value of 0.0096. The test is only very
    slightly conservative, because P(S ≤ s) includes equality. It is valid.
  - p_le3 is clearly conservative because the binomial is discrete: 0.043 at α = 0.05 and 0.0675 at α = 0.10. It is valid
    but has low power.
  - Among groups of 30 independent random rules, the smallest p was ≤ 0.0141 in 36 % of the groups (theory: 34.6 %). The
    observed best p is therefore what you expect from 30 rules that do nothing.
- **Convolution tail at the A7 R2 sum** S = 2049:
  - exact harness value 0.014059
  - independent MC, 2·10⁶ sums drawn with numpy's hypergeometric sampler: 0.014183 ± 0.000084, within 1.5 SE
  - normal approximation with continuity correction: 0.014066
- **Exact null for past-dependent rules.** I ran 5 000 synthetic i.i.d. histories.
  - A7 R2 (mirror, with its direction frozen on draws 0..29): P(p ≤ 0.05) = 0.050.
  - A7 R1 (adaptive arg-min over 88 transform candidates): P(p ≤ 0.05) = 0.041, KS D+ = 0.0096, below the critical value
    of 0.019.
  - So walk-forward selection does not inflate the p-values. My re-implementation reproduces the reported A7 R1 and R2
    means exactly on the real draws.

## 2. Leakage (per agent)

The test runs for every rule and every evaluated t = 30..411; A4 uses 30 values of t, with a fresh model refit each time.
At each t it overwrites, in place, every data source a rule could reach, from draw t onwards:

- the `main`/`order` of `harness.DRAWS[t:]` become random draws (the dates are kept, because the draw date is public);
- A6's Extra výplata and Loto 5 z 35 rows dated on or after the VAN date get random numbers;
- A10's tier-data rows ≥ t get random values.

Then it calls the rule again on `DRAWS[:t]`. If the ticket changes, the rule read something it should not.

- **Result: 0 changed tickets out of all 30 × 382 calls (30 for A4).** The leakage verdict is "none" for every agent.
  `DRAWS` was never mutated by a rule.
- **Positive controls.** A rule that reads `DRAWS[t]` was flagged at 382/382 values of t. A rule that also uses same-day EV
  draws was flagged at 86/382.
- **Reproduction.** All 30 evaluate() results (mean, p, p_le3, n_zero, €) and all ten 25.11 tickets reproduce exactly. No
  fixed numbers are needed.
- **Declared, benign accesses:**
  - A5, A6 and A8 read only `DRAWS[t]['date']` to get the target date. This is stated in their preregs.
  - A7 fixes the R2/R3 orientation from draws 0..29 when the module is imported. This is pre-registered, and those draws
    are all before t ≥ 30.
  - A10 uses tier rows below t only, up to row 409.
  - A6 uses other-game rows with a date strictly earlier than the VAN date. Its EV file matches `run_2311/data/ev.json` on
    170 of 171 draws with 0 mismatches; the extra draw is 23.11. EV draws fall on Mondays and Thursdays only. Loto 5 z 35
    draws fall on Wednesday, Friday and Sunday, plus one Tuesday (23.12.2025, a holiday shift). Loto 5 z 35 is another game
    and cannot carry VAN outcomes.
- `van412.json` draws 0..409 match `run_2311/data/van.json`. The sha256 of the data and of the harness match the preregs.

## 3. Pre-registration

| Agent | Prereg written (UTC) | Result file mtime | Seconds between | Prereg changed later? | Code changed later? |
|---|---|---|---|---|---|
| A1 | 05:55:51 | 05:56:45 | 55 | no | **yes** (see below) |
| A2 | 05:56:01 | 05:57:30 | 90 | no | no |
| A3 | 05:55:18 | 05:55:57 | 40 | no | no |
| A4 | 05:55:33 | 05:57:29 | 116 | no | no |
| A5 | 05:55:40 | 05:56:29 | 50 | no | no |
| A6 | 05:57:23 | 05:58:07 | 44 | no | no |
| A7 | 05:55:36 | 05:56:25 | 49 | no | no |
| A8 | 05:56:07 | 05:57:06 | 60 | no | no |
| A9 | 05:55:13 | 05:56:15 | 63 | no | no |
| A10 | 05:56:18 | 05:56:52 | 34 | no | no |

- Every prereg was written, saved and committed no later than its result file. The preregs and the code were checked against
  the git history (`git log --name-status`).
- **Bytecode forensics.** The `.pyc` files of A4, A5, A9, A10 and the harness that were briefly committed are code-identical
  to the final sources, so no other version of that code was imported.
- **Code vs prereg.** I read all 30 rules line by line. Every parameter, window, seed, tie-break and orientation matches its
  prereg. For example, A7 R2 has m0 = 5.4828 and therefore uses the "image"; A7 R3 has a0 = 5.6552 and uses the "highest"
  side.
- **Deviations and notes:**
  1. **A1.py was edited after its first commit.** The change is in the R3 sampler: `u = rng.random()*T` became
     `u = (1-rng.random())*T`. No parameter changed, but the Monte-Carlo realisation did. With the pre-change code, R3 has
     mean 5.508 and p 0.559, against the reported 5.437 and p 0.158. R3 is therefore dominated by simulation noise. It is
     unknown whether the old version was ever run. Either way the result is non-significant.
  2. **A8 R1 is the same rule as A8 R2.** Both picked the generator combo PY/UDAY/SEQ, so one test is counted twice in
     Holm, which makes Holm slightly conservative.
  3. **A6 R2 and A10 R2 are exact complements of their R1** (hits = 11 − hits). These were pre-registered as two-tailed
     pairs, so they are not independent tests.
  4. **A4's target weekday is "previous date + 1 day"**, which is wrong after the 24–25.12 and 3.4 gaps. This was
     pre-registered and is not a leak.
  5. **`aggregate.py` counts two families.** It declares a survivor if Holm(p) *or* Holm(p_le3) is below 0.05, so the
     family-wise error rate is up to about 0.10. This does not matter here, because nothing survives.
  6. **File times and git cannot rule out earlier unsaved exploratory runs.** The study took about 5 minutes in total.

## 4. Multiplicity, p-value distribution, stability of A7 R2

- **Holm recomputed** independently over all 30 primary p-values: it is identical to `aggregate.json`. There are no
  survivors for p_mean_lower (minimum Holm 0.422) or for p_le3 (minimum Holm 0.798). BH gives none either (minimum q 0.42).
- **KS test of the 30 p-values against U(0,1):**
  - All 30: D = 0.175, on the side of small p. The two-sided p is about 0.28 and the one-sided p about 0.14, both by MC
    assuming independence.
  - 27 p-values, after dropping the duplicate and the two complements: D = 0.212, two-sided p 0.15, one-sided p 0.076.
  - Two of the 30 p-values are ≤ 0.05, against 1.5 expected; P(≥2) = 0.45.
  - The average mean hits over the 27 is 5.478, which is −0.36 SD of a single rule.
  - The p-values are correlated, so these KS numbers are only indicative. The hit series are correlated at −1 for A6 and
    A10 R1/R2, +1 for A8 R1/R2, 0.80 for A1 R3/A9 R3, 0.70 for A9 R1/R2 and 0.61 for A4 R1/A9 R3; the mean |r| is 0.08.
- **Correlation-aware global test.** I kept the 30 real ticket sequences and re-simulated the draws uniformly 20 000 times.
  The smallest p came out ≤ 0.0141 in 31 % of the simulations. The best result is unremarkable.
- **A7 R2 (mirror 23 − x) stability.** This is descriptive, not a new test.

  | Segment | n | Mean hits | Exact p |
  |---|---|---|---|
  | all (t 30..411) | 382 | 5.364 | 0.014 |
  | first half (t 30..220) | 191 | 5.272 | 0.005 |
  | second half (t 221..411) | 191 | 5.455 | 0.315 |
  | quarters | — | 5.316 / 5.232 / 5.337 / **5.567** | — |
  | direction-fixing draws 1..29 | 29 | 5.483 | 0.50 (the orientation was a coin flip) |

  The effect sits in the first half and is gone in the last quarter. The difference between the halves has z = −1.49. This
  is the pattern of a chance fluctuation, not a stable bias.
- **What the result would mean even if it were real.**
  - Tilting the hit distribution to mean 5.364 (exponential tilt) moves P(0 hits) from 1/705 432 to only about 1/422 000.
  - The design can detect, at the Holm-30 level, a shift of about 0.18 hits per draw with 50 % power, or 0.23 with 80 %
    power.

## 5. Ticket for 25.11.2026

The ticket is **T = 1 4 7 8 10 11 14 16 18 20 21**, and its complement is **C = 2 3 5 6 9 12 13 15 17 19 22**, which matches
the lead's complement.

- **Validity.** Both are 11 distinct numbers in 1..22.
- **Odd/even:** T has 4 odd / 7 even and C has 7/4, so neither is all-odd or all-even.
- **Low (1..11) / high (12..22):** T has 6/5 and C has 5/6, so neither is 1–11 or 12–22.
- **Runs:** the longest run is 2 in both. 99.998 % of all tickets have a run of at least 2, so this is not a pattern.
- **Arithmetic progressions:**
  - T's longest is 4 (1,4,7,10 and 14,16,18,20); 95.9 % of all 705 432 tickets contain one at least that long.
  - C's longest is 5 (3,6,9,12,15); 49.4 % of tickets contain one at least that long.
  - Neither whole set is a progression, and both are typical.
- **Full slip lines:** neither contains a whole row or column of length ≥ 4 in row-major slip layouts of width 4..11. 58 % of
  random tickets would.
- **Sum:** T sums to 130; the mean is 126.5 with sd 15.2.
- **Recent draws:**
  - T is neither equal to the 23.11 or 24.11 draw nor to their complements. It would have had 6 hits on each.
  - It is not any of the 44 rotation, reflection or parity images of those draws, or their complements; the maximum overlap
    is 8.
  - It is not equal to any of the 412 past draws or their complements; its overlap with them ranges from 2 to 9.
- **Exact odds:**

  | Event | Probability |
  |---|---|
  | 0 hits | 1/705 432 (0.000142 %) |
  | 0 or 11 hits (top prize) | 1/352 716 |
  | any prize (0–3 or 8–11 hits) | 2531/29393 = **8.61 %** |
  | 5 or 6 hits | 2541/4199 = **60.51 %** (30.26 % each) |
  | 4 to 7 hits (no prize) | 91.39 % |

  The expected payout per bet is 0.755 € if the top prize is not shared, or 0.472 € without the top prize. No ticket has
  better odds.
- **Optional note on prize sharing (not a reason to change).** Only the top prize is affected.
  - A10's ridge betas, fitted on 410 draws of tier data, measure *player* preferences precisely. 3, 11, 7, 13, 9, 5 and 2 are
    the most popular numbers, and 14, 16 and 20 the least.
  - C is built from popular numbers and sits at the 91st percentile of all tickets; T sits at the 9th. The contrast has
    z ≈ −12, so this is a real player preference, not a draw effect.
  - In both top-prize events (0 hits or 11 hits), the winners are exactly the holders of T or C.
  - With about 40 000–46 000 bets per draw, about 0.13 other holders are expected for an average ticket. In 410 draws there
    were 46 top-prize winners, against 54 expected under uniform play. So sharing is uncommon, and C's popularity raises the
    risk only somewhat.
  - If the lead wants to minimise sharing, they can draw a random ticket again until its popularity percentile is about
    25–75. This is optional; the ticket passes every requested check.
