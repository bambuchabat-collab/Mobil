# Extra výplata: which numbers other players avoid (subagent 4, target Mon 23.11.2026)

Script `lab/run_2311/scripts/popularity.py` (python3 -I, about 2.5 min). All numbers are in `popularity.json`. The plan was written before any fit: `popularity_prereg.md` (23:31Z).
Data: `data/ev.json`, 170 draws from 2024-03-25 to 2026-11-19.

This work does not predict draws. It only estimates how many people share a prize. Tiers 3+0 to 5+1 are pari-mutuel: each tier pays a fixed % of deposits, and the slope of log prize on log winners is −1.00 for every tier (−0.998 to −1.014).

## 1. Popularity (full data, pooled model over 3-, 4- and 5-match winners)

Least → most popular. The relative pick frequency is ≈ 1 + 0.81·a. Its SE is about ±0.01 for every number.

| # | 20 | 14 | 15 | 1 | 16 | 18 | 2 | 10 | 23 | 22 | 26 | 19 | 8 | 24 | 21 | 4 | 5 | 6 | 27 | 12 | 17 | 9 | 13 | 25 | 3 | 7 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| freq | .94 | .94 | .94 | .95 | .95 | .95 | .96 | .97 | .98 | .98 | .98 | .99 | .99 | 1.00 | 1.00 | 1.00 | 1.01 | 1.01 | 1.03 | 1.03 | 1.04 | 1.04 | 1.04 | 1.06 | 1.07 | 1.08 | 1.09 |
| rank CI | 1–7 | 1–7 | 1–7 | 1–8 | 1–8 | 1–9 | 3–11 | 3–11 | 7–14 | 7–15 | 7–16 | 8–17 | 8–17 | 10–18 | 9–18 | 11–18 | 13–19 | 13–20 | 17–23 | 17–23 | 19–24 | 19–24 | 19–24 | 21–26 | 23–27 | 25–27 | 25–27 |

- The new ranking matches agent_extra almost exactly (corr 0.99). The six least popular numbers are still {14, 15, 20, 1, 16, 18}.
- **Extra number** (share of +1 winners): 1 1.03, 2 1.10, **3 1.23**, 4 1.06, **5 0.86, 6 0.86, 7 0.86** (SE ≈ 0.01–0.02). The gap is shrinking: in 2024, 5/6/7 were picked at 0.70 of average; in 2026 H2 at 0.92, and 3 at 1.16.
- **Consecutive pairs: players avoid them.** A draw with a pair has fewer co-winners: −1.2 % at 3 matches, −6.0 % at 4 and −14.8 % at 5, for each pair (all CIs exclude 0). The effect is linear in the number of pairs; dummies for 1, 2 and 3 pairs agree. So pairs inside a field are **good**. Runs of 3 stay forbidden.

## 2. Strict walk-forward (t = 40..169; each draw predicted only from earlier draws)

| target | corr(number part, residual) | incremental OOS R² | calib. slope | perm. p (Holm) |
|---|---|---|---|---|
| 3-match, M1 per-category ridge | 0.79 | 0.70 | 1.04 | 5e-5 (2.5e-4) |
| 4-match, M1 | 0.57 | 0.36 | 0.87 | 5e-5 (2.5e-4) |
| 5-match, M1 | 0.32 | 0.10 | 0.76 | 0.0019 (0.0038) |
| 3 / 4 / 5-match, **M2 pooled** | **0.81 / 0.64 / 0.42** | **0.73 / 0.45 / 0.19** | 1.06 / 0.92 / 1.07 | 5e-5 (2.5e-4), tested on 3-match |
| extra number | 0.85 | 0.02 (drift, slope 0.51) | — | 0.004 (0.004) |

- Second null test (main sets shuffled across draws, then refit): p = 0.005 (200 reps).
- Real prizes on held-out draws: in draws the model had rated unpopular (bottom third) prizes were higher than in draws rated popular (top third): ×1.09 at 3 matches, ×1.12 at 4, ×1.17 at 5.
- The frozen agent_extra ranking on the 8 newest draws: corr 0.69; the new walk-forward model on the same draws: 0.50. With n = 8 this is noise. Caveat: agent_extra was fitted on data through 12.11, so only 16.11 and 19.11 were truly new to it, not 8 draws. On those two, both models predicted fewer co-winners (residuals −0.03/−0.04), and the realized residuals were −0.06/−0.08.

## 3. Money (tiers 3–5, normal month; pool shares 31.07 % of stake)

| field | return per 1 € from tiers 3–5 | vs random field |
|---|---|---|
| most popular valid (3 11 13 17 25 27 + 3) | 0.268 | −15 % |
| population average | 0.311 | −1 % |
| uniform random field | 0.314 | 0 |
| **recommended pair** | **0.356** | **+13.2 % (bootstrap CI 12.2–14.3)** |

- The +13.2 % breaks down into main numbers +9.3 % (CI 8.4–10.2; +6.7 % without the pair effect) and extra 5/6/7 +3.5 % (CI 2.8–4.1). Extra 3 is −5.0 %.
- With 2026-H2 extra popularity the gain is about **+11.7 %**. Main-number popularity is stable: models fitted on the recent half and on the last 60 draws give +12.4 % and +11.9 %.
- Selection bias is small. A field chosen on one half and scored on the other half's model gains +15.0 % and +13.8 %.
- Prize factor per tier vs a random field: 3-match ×1.04, 4-match ×1.12, 5-match ×1.34. The recommended pair beats the most popular field by +33 %.
- **Return per 1 € goes up by about +4 percentage points** (+0.037 to +0.042 € per 1 € from tiers 3–5, plus about +0.003 from 6+0/6+1 sharing). Normal-month baseline ≈ 0.49–0.51 → **≈ 0.53–0.55**. It is still a loss of about 45 % of the stake. Your chance of winning does not change.

## 4. Optimiser (2 disjoint fields, no 3-term AP, no run of 3, extras distinct from {5, 6, 7}; 83 148 valid fields; exact enumeration)

| rank | field 1 | field 2 | factor vs random | Δ vs #1 (bootstrap SD) |
|---|---|---|---|---|
| 1 | 1 2 14 15 20 21 + **6** | 10 16 18 19 23 24 + **7** | 1.132 | — |
| 2 | 1 2 15 16 18 19 + 6 | 10 14 20 21 23 24 + 7 | 1.132 | 0.00 % (0.03) |
| 3 | 1 2 14 15 20 21 + 6 | 16 18 19 23 24 26 + 7 | 1.129 | 0.29 % (0.23) |
| 4 | 1 2 15 16 18 19 + 6 | 13 14 20 21 23 24 + 7 | 1.129 | 0.31 % (0.26) |
| 5 | 14 15 20 21 23 24 + 6 | 1 2 16 18 19 26 + 7 | 1.129 | 0.34 % (0.24) |

The honest answer is that **many pairs are equivalent within noise**:
- 22 of the next 49 distinct pairs cannot be told apart from #1 (bootstrap P(#1 better) < 0.95).
- The 50th pair is still ×1.125.
- If you refit on bootstrap resamples, the chosen pair loses only 0.10 % on average (90th percentile 0.43 %) against each refit's own optimum.
- Extras 5, 6 and 7 are interchangeable: every assignment is within 0.06 %.

The near-equivalent pairs reuse {1, 2, 10, 13, 14, 15, 16, 18, 19, 20, 21, 23, 24, 26}, with 2–3 consecutive pairs per field.

**Recommendation for 23.11:** field 1 = `1 2 14 15 20 21` + extra 6; field 2 = `10 16 18 19 23 24` + extra 7. `check_ev_tickets.py` confirms: no run of 3, no equal steps, disjoint, P(any prize) 20.05 %.
