# Extra výplata – player-popularity update, pre-registered plan

Written: 2026-11-22T23:31Z (UTC), BEFORE any model fit / walk-forward result on `data/ev.json` was looked at.
Seen before writing: file structure, tier names, pool shares per tier (fixed % of deposits, prize floored to 0.10 €),
and that before 2024-10-07 (draw index 28) the 3+0 tier counts only "3 main, extra not matched" (3+0/4+0 ≈ 8.2 in both eras),
so 3+1 winners are simply absent then. Old agent_extra results (C1/C2) were read.
Data: `data/ev.json`, sha256 d2aff931…f43e, 170 draws 2024-03-25..2026-11-19, index t = 0..169 (oldest first).
Note: agent_extra's full-data model used draws through 2026-11-12 (168 draws); only t = 168, 169 are truly unseen by it.

## Targets (per draw t; B_t = deposits/1.5; P_m = C(6,m)C(21,6-m)/C(27,6))
- 3-match: W3 = 3+0 + 3+1 (post era) or 3+0 (pre era, t<28). E3 = B·P3 (post) or B·P3·(1 − ŝ_pb) (pre), ŝ_pb = extra-number share estimated on the training draws of the same fit.
- 4-match: W4 = 4+0 + 4+1, E4 = B·P4. 5-match: W5 = 5+0 + 5+1, E5 = B·P5.
- y_m = log(W_m / E_m).
- Extra share: s_t = (Σ_m W_{m+1}) / (Σ_m W_m) over m ∈ {3,4,5} (post) or {4,5} (pre) = share of fields holding the drawn extra.

## Models
- Covariates (unpenalised, all models): intercept, #consecutive pairs in D_t, pre-era dummy (no 3+1 tier), Thursday, premium month (May/Oct 2026), log(B_t) centred. A covariate with no variation in a training set is dropped.
- M1 (per category m=3,4,5): weighted ridge of y_m on 27 drawn-number indicators + covariates. Weights 1/(τ_m² + 1/E_m,t); τ_m² = max(1e-6, mean(resid²) − mean(1/E)) from an unweighted ridge fit (λ from {0.1,0.3,1,3,10,30} by LOO) on the same training set, then the weighted fit. (Clarified 23:36Z, still before any fit.)
- M2 (pooled player popularity a_i): stacked rows m=3,4,5, number part c_m·Σ_{i∈D} a_i with c_m = m/6 − (6−m)/21 (log-linear player model, linearised: c3=0.357, c4=0.571, c5=0.786), per-category covariates, same weights.
- Cov-only baseline: same covariates, no numbers (per category).
- λ grid (weighted scale): {10, 30, 100, 300, 1000, 3000, 1e4, 3e4, 1e5}; chosen inside each training set by closed-form leave-one-out (M2: leave-one-draw-out, block formula). Nothing tuned on evaluation draws.
- Extra model: ŝ_x = Σ_{t:pb=x} n1_t / Σ_{t:pb=x} n_t (pooled ratio); relative popularity r_x = ŝ_x / mean(ŝ).

## Walk-forward (strict)
For every t = 40..169 (130 draws): fit everything on draws < t only, predict draw t.
Metrics per category m and model: corr(p_t, r_t) where p_t = predicted number part and r_t = y_t − ŷ_cov,t (cov-only walk-forward prediction);
incremental OOS R² = 1 − Σ(y − ŷ_full)²/Σ(y − ŷ_cov)²; residual R² = 1 − Σ(r − p)²/Σ(r − r̄)².
Extra: corr(ŝ_{pb_t}^{(<t)}, s_t) and R² vs training-mean share.
Secondary money check: realized mean exp(−r_t) in lowest vs highest tercile of p_t (3-match).

## Tests (Holm, family α = 0.05, one-sided "corr > 0")
T1 M1 m=3, T2 M1 m=4, T3 M1 m=5, T4 M2 (evaluated on m=3 target), T5 extra-number.
p-value: permute number labels of the fitted coefficient vectors at prediction time (same permutation for all t), 20000 perms (extra: all 5040 permutations of 7 labels).
Secondary null (not in Holm): refit-based, main sets D shuffled across draws (number indicators only; covariates kept), 200 reps, for M1 m=3.
Frozen comparison (descriptive): agent_extra C1_full β (3-match) on the 8 newest draws t=162..169 (only 168,169 unseen by it) vs new walk-forward M1 on the same draws.

## Money (tiers 3–5) and optimiser
- Final fits on all 170 draws. Per tier m the model (M1 or M2) with the higher walk-forward incremental OOS R² for that category is used (stated optimism: chosen on the evaluation draws).
- Slope check: per tier, regress log(prize) on log(winners), log(deposits), premium, era; expect slope ≈ −1 (pools are fixed shares).
- R_m(D) = exp(u_m(D)) / E_D[exp(u_m(D))] over all 296010 D (u = number part + pair term); A_m(S) = E_D[1/R_m(D) | |S∩D| = m] (exact enumeration).
- Extra factors: +1 tiers ∝ 1/(7 ŝ_x); +0 tiers ∝ (1/7) Σ_{pb≠x} 1/(1 − ŝ_pb). Pool shares f from 2026 normal-month data.
- EV per 1 € (tiers 3–5) = Σ_m A_m(S)·[f_{m,1}/(7ŝ_x) + f_{m,0}·(1/7)Σ_{pb≠x} 1/(1−ŝ_pb)]. Compare: best valid field, uniform random field, population-average field (=Σf), most-popular valid field.
- CI: bootstrap over draws (1000 reps, λ fixed at full-data value), fields fixed. Selection-honesty check: choose field on draws 0..84, evaluate with model fit on 85..169 (and reverse).
- Optimiser: 2 disjoint fields, each with no run of 3 consecutive numbers and no 3-term arithmetic progression; extras distinct from {5,6,7}. Screen all valid fields with the pair-free closed form (elementary symmetric polynomials), exact enumeration (with pair term) for the top 3000, best disjoint pairs among them (bound-checked). Report top 5 pairs, their factor vs average, bootstrap SD of differences and regret of the chosen pair across bootstrap refits.
- Consecutive pairs: sign of the pair covariate decides; if players avoid pairs (negative coefficient), pairs in a field are allowed/favoured (runs of 3 stay forbidden).
