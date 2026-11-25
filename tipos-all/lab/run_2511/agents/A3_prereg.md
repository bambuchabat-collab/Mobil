# A3 pre-registration: per-number Markov chains and gap/hazard models

Written: 2026-11-25T05:55:18Z (UTC), before any evaluation was run.
Family: PER-NUMBER MARKOV CHAINS AND GAP/HAZARD MODELS.
Harness: lab/run_2511/harness.py, evaluate(rule, name), draws 30..411 (n = 382), past = draws strictly before.
Primary rule: R1. Primary metric: p_mean_lower. Secondary: p_le3. Raw p only (lead applies Holm).

Notation: for number i (1..22) and past draw index u, x_i(u) = 1 if i is in draw u's `main`, else 0.
All estimates use ALL past draws (expanding window), nothing from the evaluated draw.
Every rule outputs the 11 numbers with the LOWEST predicted probability of being drawn next.
Tie-break (all rules): add a uniform jitter of size 1e-9 drawn from numpy default_rng(seed = 20251125 + len(past)),
i.e. ties are broken by a fixed-seed random order that depends only on the draw index. No other parameters.

## R1 (primary) - per-number 1st-order Markov chain
For each number i, count over past transitions u -> u+1 (u+1 < len(past)):
 n_i(s) = #{u : x_i(u) = s}, k_i(s) = #{u : x_i(u) = s and x_i(u+1) = 1}, s in {0,1}.
Laplace estimate p_i(s) = (k_i(s) + 1) / (n_i(s) + 2).
Current state s_i = x_i(last past draw). Prediction q_i = p_i(s_i). Ticket = 11 smallest q_i.

## R2 - per-number 2nd-order Markov chain
State pair (a, b) = (x_i(u-1), x_i(u)), 4 states. n_i(ab), k_i(ab) counted over u with u-1 >= 0 and u+1 < len(past).
Laplace estimate p_i(ab) = (k_i(ab) + 1) / (n_i(ab) + 2).
Current state = (x_i(T-2), x_i(T-1)) where T = len(past). Prediction q_i = p_i(current). Ticket = 11 smallest q_i.

## R3 - pooled run-length (gap) hazard
State of number i at time u: signed run length r_i(u) computed from draws <= u:
 if x_i(u) = 0: r = -g, g = number of consecutive most recent draws (ending at u) in which i was absent (gap since last appearance);
 if x_i(u) = 1: r = +h, h = number of consecutive most recent draws (ending at u) in which i was drawn.
 Lengths are capped at 6 (so states -6..-1, +1..+6; "6" means >= 6). At the start of history a run that reaches back to
 draw 0 is counted with its observed length (no special censoring), which is fixed a priori.
Hazard h(r) = P(drawn at u+1 | state r at u), pooled across all 22 numbers and all past transitions:
 h(r) = (K(r) + 1) / (N(r) + 2) (Laplace).
Prediction q_i = h(r_i(T-1)). Ticket = 11 smallest q_i (ties - many numbers share a state - broken by the jitter above).
Rationale: generalizes "hazard as a function of current gap" (negative states) and also distinguishes among the numbers
that were drawn last time by how long their current streak is. Plain least-frequent / longest-gap rules are NOT used.

## Outputs
agents/A3.py implements R1..R3; agents/A3.json stores evaluate() dicts + definitions and ticket_25_11 = R1 output on all
412 draws (tickets of R2/R3 also listed for information). Under the null (independent fair draws) all p-values ~ U(0,1).
