# S4 — pre-registration (signal processing / time-series econometrics)

Written: 2026-11-27 20:41:20 UTC, BEFORE any calculation on the draw data
(only the file format was inspected: field names, number of records, first/last date).

## Game choice

Both games, one idea per formula:
- **F1 -> EM** (main formula, its prediction is the 28.11 prediction). Reason: Lomb–Scargle is the
  tool for *irregularly sampled* series; EM draws are on two weekdays (gaps of 3/4 days, schedule
  changed over the years), and EM has 1 242 draws over ~11 years (1 212 evaluated), i.e. the longest
  series and the finest frequency resolution (periods from a week to years: ball-set rotation,
  machine maintenance, seasons).
- **F2 -> EM**: slow drift of ball propensities (wear, set replacement) is only plausible on a long
  multi-year series.
- **F3 -> VAN**: daily, regularly sampled series (415 draws) is the natural case for classical
  linear prediction (maximum-entropy / Burg AR).

Primary metric for every formula: `p_upper` from `harness2.evaluate` (walk-forward from draw 30).
Raw p-values reported, no multiplicity correction (leader applies Holm).
No parameter is tuned on data; all values below are fixed a priori (none tuned even on the first 30 draws).

## Notation

`past` = draws strictly before the evaluated one (oldest first), t = len(past), N numbers, K drawn,
T = K ticket size (EM: N from data, K=T=7; VAN: N=22, K=T=11). x_i(j) = 1 if number i is in
draw j's `main`, else 0. p0 = K/N. Day time of draw j: d_j = date.toordinal(); target day tau =
toordinal(date argument). Ticket = T numbers with the highest score; ties broken by the smaller number.

## F1 (EM): per-number generalized Lomb–Scargle, dominant period, extrapolated to the target date

For each number i, fit on calendar time d_j (j < t) the floating-mean sinusoid
x_i(j) = a + b cos(2 pi f d_j) + c sin(2 pi f d_j) by least squares (Zechmeister & Kürster 2009 GLS).
- Frequency grid (cycles/day): f_k = k/8000, k = 1..4000 (periods 8000 d .. 2 d), plus exactly
  1/7, 2/7, 3/7 (weekday frequencies). Admissible at step t: f >= 1/span, span = d_{t-1} - d_0
  (at least one full cycle inside the past data).
- Centered sums: Y = mean x, C = mean cos, S = mean sin, YC = mean(x cos) - Y C, YS = mean(x sin) - Y S,
  CC = mean cos^2 - C^2, SS = mean sin^2 - S^2, CS = mean(cos sin) - C S, YY = mean x^2 - Y^2.
- Ridge-stabilised normal equations (handles the degenerate two-weekday phases):
  M = [[CC+lam, CS],[CS, SS+lam]], lam = 1e-3; beta = (b, c) = M^{-1} (YC, YS).
- Power P_i(f) = (YC, YS) . beta / YY (fraction of variance explained).
- Dominant frequency f*_i = argmax over admissible f of P_i(f) (chosen on past data only, re-chosen at
  every walk-forward step).
- Forecast score_i = Y + b (cos(2 pi f* tau) - C) + c (sin(2 pi f* tau) - S).
- Ticket = top 7 scores.

## F2 (EM): Kalman local-level model of each number's propensity, signal-to-noise ratio by ML

State space per number i (draw-index time): x_i(j) = mu_i(j) + eps, Var eps = R = p0(1-p0);
mu_i(j+1) = mu_i(j) + eta, Var eta = Q = q R. Init mu_i(0|-1) = p0, P(0|-1) = P0 = (0.1 p0)^2.
- Grid q in {0, 1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2}.
- For every q the standard Kalman filter is run over past draws; pooled Gaussian prediction-error
  log-likelihood L(q) = sum_j sum_i [ -0.5 ln F_j - 0.5 v_ij^2 / F_j ], F_j = P(j|j-1) + R,
  v_ij = x_i(j) - mu_i(j|j-1).
- q_hat = argmax L(q) on past draws only (ties -> smaller q), re-estimated at every step.
- Score_i = mu_i(t|t-1) under q_hat (one-step-ahead predicted propensity). Ticket = top 7.

## F3 (VAN): maximum-entropy (Burg) linear prediction, pooled AR over the 22 indicator series

- y_i(j) = x_i(j) - xbar_i, xbar_i = mean of x_i over the past draws.
- Multi-segment Burg recursion pooled over all 22 series (common reflection coefficients):
  k_m = -2 sum_i sum_j f_ij b_i,j-1 / sum_i sum_j (f_ij^2 + b_i,j-1^2), Levinson update of the
  prediction-error filter a (a_0 = 1) and of the error power sigma2_m = sigma2_{m-1}(1-k_m^2),
  sigma2_0 = mean y^2. Orders m = 0..14.
- Order by AIC: m_hat = argmin_m [ n ln sigma2_m + 2m ], n = 22 t (ties -> smaller m), on past data
  only, re-chosen every step.
- Score_i = xbar_i - sum_{k=1..m_hat} a_k y_i(t-k). Ticket = top 11.

## Outputs

`agents/S4.py` (python3 -I, numpy only, deterministic; no randomness used), `agents/S4.json`
per PROMPT_2811.md; prediction_28_11 = F1 on the full EM history for date 2026-11-28.
Predictions of F2 (EM) and F3 (VAN) for 28.11 are added as extra information only.
Honest-reporting rule: a formula "works" only if its p_upper is small after Holm over all 15
formulas (done by the leader); a single raw p ~ 0.05 is not evidence.
