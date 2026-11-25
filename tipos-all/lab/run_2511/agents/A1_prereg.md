# A1 pre-registration: DRAW ORDER / BALL POSITION family

Written: Wed Nov 25 05:55:51 UTC 2026 (before any evaluation was run).
Data: van412.json, sha256 ce9a079e488f458befa620ef7695a3c9f01a2e3fbbe02f3229a4d13d807bd73e (412 draws).
Only data check done before writing this: every `order` is a permutation of `main` (0 bad, 0 draws with order == sorted).
No hit counts of any rule were looked at.

Harness: `harness.evaluate(rule, name)`, walk-forward over draws 30..411 (n = 382), rule sees only `past = DRAWS[:t]`.
Primary metric: p_mean_lower (mean hits < 5.5). Secondary: p_le3. Raw p only (lead applies Holm).
Positions are 1..11 in draw order (`order[0]` is position 1). All parameters are fixed here a priori; nothing is tuned.

## R1 (PRIMARY) — late-ball score (order only, all past draws)
For each number x in 1..22, over ALL past draws in which x was drawn, m(x) = mean draw position of x (1..11).
A number never drawn in `past` gets m(x) = 12.
Ticket = the 11 numbers with the LARGEST m(x) (balls that tend to come out late are predicted least likely to be drawn next).
Tie-break: fewer appearances in `past` first, then smaller number.
Hypothesis: a physically "reluctant" ball comes out late when drawn and is also less likely to be drawn at all.
Note: order-only by construction, so it is not one of the frequency rules already tested on 24.11.

## R2 — early balls of the last 3 draws
Scan positions p = 1, 2, ..., 11; for each p scan lags L = 1, 2, 3 (draws t-1, t-2, t-3, most recent first);
add ball `order[p]` of that draw to the ticket if not already in it; stop as soon as the ticket has 11 numbers.
(i.e. the first-drawn balls of the three most recent draws). Hypothesis: first-drawn balls of recent draws avoid the next draw.
Differs from 24.11 R12 (late half of previous draw + random fill) and R1/R11 (whole previous draw).

## R3 — order-transition Markov model (ball drawn right after X), all past draws
From all past draws: first-ball counts F[b] = #draws with position-1 ball b; transition counts C[a][b] = #times ball b was
drawn immediately after ball a (positions k -> k+1 inside the same draw).
Simulate N = 10000 draw sequences of 11 balls without replacement: first ball with prob proportional to F[b] + 1;
each next ball, among balls not yet drawn, with prob proportional to C[prev][b] + 1 (Laplace smoothing, alpha = 1).
Inclusion probability pi(b) = share of simulated sequences containing b.
Ticket = the 11 numbers with the LOWEST pi(b); tie-break smaller number.
RNG: numpy.random.default_rng(20261125 + len(past)) (deterministic, independent of evaluation order).

## Outputs
agents/A1.py, agents/A1.json with evaluate() dicts + definitions for R1..R3, and `ticket_25_11` = R1 applied to all 412 draws.
