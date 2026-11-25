# A9 pre-registration — BAYESIAN BALL-PROPENSITY MODELS

Written: 2026-11-25 05:55 UTC (`date -u`: Wed Nov 25 05:55:13 UTC 2026), before any evaluation was run.

Data/harness: lab/run_2511/van412.json, harness.evaluate (draws 30..411, n = 382). Each rule sees only `past`.
All parameters below are fixed a priori (none chosen from the data). Ticket = the 11 numbers with the LOWEST
posterior predictive probability of being drawn; ties broken by the smaller number first (deterministic).
No randomness is used (seed fixed at 0 anyway). Primary metric: p_mean_lower of R1. Secondary: p_le3, R2, R3.

## R1 (primary) — Dirichlet–multinomial propensity with exponential forgetting
- Draw d in past (index 0..t-1) has weight w_d = 0.5 ** ((t-1-d) / 30) (half-life 30 draws; newest past draw w = 1).
- Weighted counts c_i = sum_d w_d * 1[i in main_d], i = 1..22.
- Symmetric Dirichlet prior alpha0 = 1 per number. Posterior predictive propensity
  pi_i = (alpha0 + c_i) / (22*alpha0 + sum_j c_j).
- Ticket = 11 numbers with lowest pi_i.

## R2 — Bayesian online change-point detection (Adams & MacKay 2007) on per-number rates
- For each number i independently: x_d = 1[i in main_d], Bernoulli with rate p_i that resets at change points.
- Constant hazard H = 1/50. Conjugate prior on each segment's rate: Beta(1, 1).
- Exact BOCPD recursion over run lengths (no truncation) through all past draws; posterior predictive
  P(x_t = 1 | x_0..x_{t-1}) = sum_r P(r_{t} = r | data) * (1 + s_r) / (2 + r), where for the next step the run-length
  distribution includes the change-point branch (r = 0, predictive 1/2) with probability H.
- Ticket = 11 numbers with lowest posterior predictive P(x_t = 1).

## R3 — Plackett–Luce on the draw order (MAP, Gaussian prior s = 0.1)
- Worth theta_i, i = 1..22. Each past draw's order o_1..o_11 has likelihood
  prod_{k=1}^{11} exp(theta_{o_k}) / sum_{j not in {o_1..o_{k-1}}} exp(theta_j) (all 22 balls start in the drum).
- Prior theta_i ~ N(0, 0.1^2) i.i.d. All past draws weighted equally (no forgetting).
- MAP by Newton's method on the strictly concave log-posterior (converged to |grad| < 1e-10, max 100 iterations).
- Under PL the inclusion probability of ball i in the next 11 is strictly increasing in theta_i, so the 11 lowest
  plug-in posterior predictive inclusion probabilities = the 11 lowest MAP theta_i.
- Ticket = 11 numbers with lowest MAP theta_i.

## Outputs
agents/A9.py, agents/A9.json (evaluate dicts + definitions, ticket_25_11 = R1 on all 412 draws). Raw p only, no
multiple-testing correction.
