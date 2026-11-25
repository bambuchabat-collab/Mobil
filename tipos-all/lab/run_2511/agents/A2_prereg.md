# A2 pre-registration — family CO-OCCURRENCE / PAIRS

Written: Wed Nov 25 05:56:01 UTC 2026 (before any evaluation was run).

Data/harness: van412.json, harness.evaluate (walk-forward over draws 30..411, n = 382). Each rule sees only
`past` = draws strictly before the evaluated one. All statistics use an expanding window over ALL past draws
(no window length, no decay, no tunable parameters). Ties in any ranking are broken by lower number first
(stable argsort over numbers 1..22). Primary rule: R1. Primary metric: p_mean_lower. Raw p only (no correction).

Notation: past draws D_0..D_{N-1} (sets of 11), D_last = D_{N-1}. c_i = #past draws containing i.

## R1 (primary) — negative lag-1 pair association with the previous draw
Transitions k = 1..N-1 (D_{k-1} -> D_k). A[i,j] = #{k : i in D_{k-1} and j in D_k};
a_i = #{k : i in D_{k-1}}, b_j = #{k : j in D_k}, M = N-1.
Residual R[i,j] = A[i,j] - a_i * b_j / M. Score s_j = sum_{i in D_last} R[i,j].
Ticket = the 11 numbers with the LOWEST s_j (least positively associated with the previous draw's numbers).

## R2 — least contemporaneous co-occurrence with the predicted draw
Predicted draw P = the 11 numbers with the HIGHEST s_j from R1 (i.e. complement of R1's ticket).
Contemporaneous phi coefficient over all past draws: n_kp = #draws with both k and p,
phi[k,p] = (N*n_kp - c_k*c_p) / sqrt(c_k (N-c_k) c_p (N-c_p)) (0 if denominator is 0), diagonal ignored.
Score u_k = mean_{p in P, p != k} phi[k,p] (mean, so the uniform negative bias of 11-of-22 cancels).
Ticket = the 11 numbers with the LOWEST u_k.

## R3 — mutually-avoiding cliques (best 11/11 partition) with learned lag direction
Using phi from R2 (all past draws), enumerate all 352 716 partitions {A, B} of 1..22 into two 11-sets
(A contains number 1). Choose the partition maximising within-group affinity
sum_{i<j in A} phi[i,j] + sum_{i<j in B} phi[i,j] (first in itertools.combinations order on ties).
Overlap series x_k = |D_k ∩ A| for all past draws; r = Pearson lag-1 autocorrelation of x (r := 0 if undefined).
Predicted side of the next draw: if r >= 0 the same side as D_last leans to (A if x_last > 5.5 else B),
if r < 0 the opposite side. Ticket = the OTHER (non-predicted) side, an 11-set.

## Outputs
agents/A2.py, agents/A2.json with evaluate() dicts + definitions; ticket_25_11 = R1 applied to all 412 draws.
