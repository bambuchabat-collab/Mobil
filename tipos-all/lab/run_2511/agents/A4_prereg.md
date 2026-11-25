# A4 pre-registration — family: MACHINE LEARNING

Written: Wed Nov 25 05:55:33 UTC 2026 (`date -u`), BEFORE any evaluation was run.
Only data inspection done beforehand: count of draws, weekday counts, date gaps (2025-12-24/25 and 2026-04-03 missing).

Harness: lab/run_2511/harness.py, evaluate() over draws 30..411 (n = 382). Primary metric: p_mean_lower of R1.
Ticket for every rule = the 11 numbers with the LOWEST predicted probability of being drawn
(ties broken by smaller number first). All seeds fixed (numpy seed 2511; the methods below are deterministic anyway).

## Features (computed for number j and target draw s using ONLY draws 0..s-1)
- L1..L10: 1 if j was drawn in draw s-k (k = 1..10); 0.5 if s-k < 0.
- F20: frequency of j over the last min(20, s) draws.
- FALL: frequency of j over all s past draws.
- GAP: min(draws since j was last drawn, 10) / 10 (1 if never drawn).
- POS: if j is in draw s-1: (position of j in its draw order, 1..11, minus 6) / 5; else 0.
- WD (R2, R3 only): one-hot weekday (7) of the target draw. For the predicted draw the weekday is
  taken as (date of last past draw + 1 day); for training rows the actual date of draw s (which is in the past).
Features are standardized with mean/std of the training rows (std 0 -> 1).

## Training / walk-forward
Training rows: target draws s = 10 .. R-1, label y = 1[j in draw s], where R = 30 + 10*floor((t-30)/10)
is the most recent refit point <= t (refit every 10 draws, using only draws < R <= t). The model fitted at R
predicts draws R..R+9 with features from their own past. The 25.11.2026 ticket uses past = all 412 draws (R = 410).

## Rules
- **R1 (PRIMARY) pooled L2 logistic regression with per-number intercepts.** One model over all (draw, number)
  rows (22 rows per draw). Inputs: L1..L10, F20, FALL, GAP, POS (14 standardized) + 22 one-hot number dummies.
  Loss = sum log-loss + (lambda/2)*||w||^2 with lambda = 10 on all weights except a global intercept (unpenalized).
  Fitted by Newton/IRLS (max 50 iterations, tol 1e-8). No weekday (it cannot change the ranking in a pooled model).
- **R2 per-number L2 logistic regression.** 22 separate models (one per number), each on its own rows
  (one per training draw). Inputs: L1..L10, F20, FALL, GAP, POS + WD one-hot (21 standardized).
  Same loss, lambda = 10, unpenalized intercept, Newton/IRLS.
- **R3 gradient-boosted stumps (pooled).** Inputs: L1..L10, F20, FALL, GAP, POS, 22 number dummies, 7 WD dummies
  (raw, unstandardized). Log-loss, start at logit of training base rate, 100 rounds, learning rate 0.1,
  each round one depth-1 stump chosen by second-order gain G_L^2/(H_L+1)+G_R^2/(H_R+1)-G^2/(H+1),
  leaf values -G/(H+1) times lr; candidate thresholds = midpoints between sorted unique feature values
  (at most 16, taken at evenly spaced quantiles when more), min 20 rows per side.

No hyper-parameter is tuned; nothing else will be evaluated. Raw p-values only (lead applies Holm).
