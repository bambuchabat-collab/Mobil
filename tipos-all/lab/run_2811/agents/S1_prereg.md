# S1 pre-registration — PHYSICS: nonlinear dynamics / chaos (Takens embedding, empirical dynamic modelling)

- Written: 2026-11-27T20:42:05Z (UTC, `date -u`). No formula has been evaluated and no draw statistics were computed
  before this file was written (only the field layout of the JSON files was inspected).
- Data (sha256): em.json b0696a8529bbc369f32f7108659c3a80eceeae083578cf6f64c172ea67193e85 (1242 draws),
  van415.json e47d6b2488f8f61f17167d96122d97658a11c2c07cd99d1f106da857efd9c2b7 (415 draws),
  harness2.py 2ce514e65599c2bb42671e908df524ed190fb48001e770f870d249801f0efaf9.
- Code: agents/S1.py (python3 -I, numpy 2.5.3 only). Output: agents/S1.json. Evaluation only via harness2.evaluate (start = 30).
- Primary metric: p_upper (more hits than chance). Raw p reported, no multiplicity correction (the leader applies Holm to all 15).

## Idea

If the ball drum were a low-dimensional deterministic system observed through the draws, Takens' theorem says that delay
vectors of the observations reconstruct its state space, and the future can be forecast from the futures of past
*analogues* (nearest neighbours in the reconstructed space; Lorenz 1969, Sugihara & May 1990 "simplex projection",
Sugihara 1994 "S-map"). These methods were never applied in earlier sessions: the old "analogue forecast" (Loto 5 z 35,
Extra výplata) matched single draws without delay embedding, without simplex weights, without embedding-dimension
selection, without local-linear maps, and never on Euromilióny. Physics prior: the drum is a strongly chaotic
many-body system (positive Kolmogorov–Sinai entropy, Lyapunov time below 1 s, earlier drum simulation), so the honest
expectation is chance level; the test is whether any draw-to-draw determinism survives.

Ball-wear / "aging" models are NOT used: any monotone wear model reduces to cumulative or exponentially-forgotten
frequencies (hot/cold, Dirichlet with forgetting, Plackett–Luce with forgetting, change points) which were all tested.

## Game choice

Main game **EM** (Euromilióny, 7 of 33, ticket 7): 1242 draws over 11 years = 3x the VAN library; nearest-neighbour /
attractor methods need a long library; EM was never tested in earlier sessions; per-draw hit s.d. relative to the
mean is lower, so smaller relative effects are detectable. F3 is run on **VAN** (daily draws, 11 balls per draw, the
longest drawing-order sequence per draw) as a cross-game check of the order-sequence idea.

## Common definitions

- `past` = draws strictly before the evaluated one, oldest first; t = len(past). x_s ∈ {0,1}^N = indicator of
  past[s]['main'] (N = 33, K = T = 7 for EM; N = 22, K = T = 11 for VAN).
- Tie-breaking of the final score ranking (all formulas): u = rank of each number in the permutation
  `np.random.default_rng([2811, f, t]).permutation(N)` (f = 1, 2, 3 for F1, F2, F3). Ticket = the T numbers with the
  highest score; equal scores ordered by smaller u first. Distances that tie when selecting neighbours: stable sort by
  distance, smaller library index s first.
- Simplex weights: w_j = exp(-d_j / d_1), d_1 = smallest neighbour distance; if d_1 = 0, w_j = 1 for d_j = 0 and 0 otherwise.

## F1 (PRIMARY, EM) — Simplex projection on the Takens delay-embedded occupation state, embedding dimension chosen walk-forward

- Delay vector with E lags: X^E_s = (x_s, x_{s-1}, ..., x_{s-E+1}) for s ≥ E-1, tau = 1 draw.
  Distance d_E(s, s') = sqrt( sum_{l=0}^{E-1} ||x_{s-l} - x_{s'-l}||^2 ) (Euclidean).
- Library L_E = { s : E-1 ≤ s ≤ t-2 } (successor x_{s+1} is in `past`). Query = t-1 (last past draw).
- Neighbours: k_E = min(E*N + 1, available) nearest library points (simplex: embedding dimension E*N plus one).
- Forecast x̂ = sum_j w_j x_{s_j+1} / sum_j w_j (simplex weights above).
- Choice of E ∈ {1, 2, 3} for each t, using only `past`: leave-one-out simplex forecast of x_{s+1} for every
  s ∈ S = { s : 2 ≤ s ≤ t-2 }, with the library L_E minus the Theiler window { s' : |s' - s| ≤ E } (removes the point
  itself and every delay vector that overlaps it or contains the target), same k rule (k = min(E*N+1, available)).
  Skill rho_E = Pearson correlation between x̂_{s+1,i} and x_{s+1,i} over all s ∈ S and i = 1..N.
  E* = argmax rho_E, ties (or undefined rho) -> smaller E.
- Score = x̂ for E*. Ticket = top 7. Also logged: distribution of E* (descriptive only).

## F2 (EM) — S-map (sequential locally weighted global linear map), E = 1, theta = 2

- Library s ∈ [0, t-2]: predictor x_s, target x_{s+1}. Query x_{t-1}.
- d_s = ||x_s - x_{t-1}|| (Euclidean), dbar = mean of d_s over the library, w_s = exp(-theta d_s / dbar), theta = 2,
  then rescaled so sum_s w_s = n (library size).
- Weighted ridge regression with intercept: A_s = [1, x_s] (N+1 columns), B = (A'WA + lambda R)^{-1} A'WY,
  R = diag(0, 1, ..., 1) (intercept not penalised), lambda = 1.0. Prediction y = [1, x_{t-1}] B (N values).
- Score = y. Ticket = top 7.

## F3 (VAN) — Poincaré-section (stroboscopic) Takens embedding of the drawing-order sequence, Lorenz method of analogues

- The drawing order o_s (11 ball numbers in the order drawn) is a sequence of 11 consecutive scalar measurements of the
  drum trajectory taken at the same phase of every draw (a stroboscopic section between reloadings), i.e. an 11-dim delay
  vector z_s = (o_s[0], ..., o_s[10]) ∈ R^11 (ball labels as coordinates).
- Library s ∈ [0, t-2], query z_{t-1}, distance Euclidean, k = 12 (= 11 + 1) nearest, simplex weights.
- Score_i = sum_j w_j x_{s_j+1, i}. Ticket = top 11.

## Output

- agents/S1.json: id, science, game, formulas (evaluate dict + definition + formula_text), prediction_28_11 from F1 on the
  full EM history (1242 draws, target date 2026-11-28).
- Nothing is changed after the first evaluation; if a bug is found it is reported as such, with both results.
