# VAN "anti-hit" pre-registration

- Written: 2026-11-24T18:11:16Z (UTC, `date -u`). No result had been computed when this was written.
  Only the data format was inspected (field names, first two and last records, count = 410, `order` present in all 410).
- Data: `lab/run_2311/data/van.json`, sha256 `8d367f7db9761ca371783a5d9e56c69bd302943c7dc94d1274081db39ef58c3f`
  (410 draws 2025-10-06..2026-11-22, oldest first), plus two appended draws (no `order` field available for them):
  - 2026-11-23 main [1,5,6,8,9,10,13,14,15,18,21]
  - 2026-11-24 main [1,2,4,6,7,14,15,17,20,21,22]
  - Total T = 412 draws, indexed t = 1..412.
- Script: `lab/run_2411/antihit.py`, run with `python3 -I`, numpy only, master seed `SEED = 20261124`.
  Outputs: `lab/run_2411/antihit.md`, `lab/run_2411/antihit.json`.

## Question

Does any simple rule produce 11-number tickets with FEWER hits than a random ticket
(mean hits < 5.5, or more draws with 0-3 hits)? A ticket has 0 hits iff it is the complement of the
drawn set, so "guessing nothing" is exactly as hard as guessing the draw (P = 1/C(22,11) = 1/705 432).

## Walk-forward

For each evaluation draw t = 31..412 (n = 382 draws) every rule outputs an 11-number ticket using ONLY
draws 1..t-1, then hits = |ticket ∩ main_t|. Every rule therefore has >= 30 past draws.

## Rules (fixed in advance)

Tie-breaking everywhere: for rule r and draw t, a priority permutation of 1..22 from
`numpy.random.default_rng([SEED, r, t])`; numbers are sorted by the rule's key, then by this priority.

- R1  complement of draw t-1.
- R2  complement of draw t-2.
- R3  11 least-frequent numbers over the last k = 5 draws.
- R4  same, k = 10.
- R5  same, k = 30.
- R6  same, all past draws (1..t-1).
- R7  11 most-frequent numbers over the last k = 5 draws ("hot numbers avoid repeating").
- R8  same, k = 10.
- R9  same, k = 30.
- R10 same, all past draws.
- R11 remove the 11 numbers with the longest current gap = keep the 11 numbers drawn most recently.
  Note (known before computing): the 11 numbers with gap 0 are exactly draw t-1, so R11 = draw t-1
  and hits(R11) = 11 - hits(R1) identically. R1 and R11 thus test the two directions of
  "overlap with the previous draw". Kept as specified.
- R12 "drawn last" rule: the 6 numbers at positions 6..11 of draw t-1's draw `order` (the late half incl.
  the middle ball), plus 5 numbers chosen at random (rng [SEED, 12, t]) from the 11 numbers NOT drawn
  in t-1. Requires `order` of draw t-1; the 2026-11-23 draw has no order, so R12 is evaluated on
  t = 31..411 (n = 381).
- R13 negative control: uniformly random 11-of-22 ticket, rng [SEED, 13, t]. Not in the multiple-testing family.

## Null model and metrics

Null: each draw is a uniformly random 11-of-22 set, independent of the past. Then for ANY rule using only
the past, hits are i.i.d. hypergeometric(N=22, K=11, n=11):
P(h) = C(11,h)·C(11,11-h)/C(22,11), mean 5.5, variance 11·(11/22)·(11/22)·(11/21) = 1.440476.

Per rule:
1. PRIMARY: mean hits; one-sided exact p = P(S <= S_obs), S = sum of hits, using the exact n-fold
   convolution of the hypergeometric pmf (z-score also reported). Holm-Bonferroni over R1..R12, alpha = 0.05.
   A rule "works" only if its Holm-adjusted p < 0.05.
2. SECONDARY: number of draws with hits <= 3 vs expected n·P(h<=3), P = 30372/705432 = 0.04305;
   one-sided exact binomial p = P(X >= X_obs); Holm over R1..R12 (separate family).
3. Count of exact 0-hit draws (expected n/705432 ≈ 0.0005).
4. Descriptive only (not used for any decision): opposite-direction p = P(S >= S_obs), hit histogram.
5. Money: prize table 0 or 11 hits = 100 000 € (top prize is shared in reality; counted at full nominal),
   1 or 10 = 200 €, 2 or 9 = 20 €, 3 or 8 = 3 €, 4-7 = 0 €; cost 1.50 € per ticket per draw.
   Report total won (split low side 0-3 / high side 8-11), cost, net; null expectation = 0.7552 € per ticket.

## Interpretation fixed in advance

- No rule passes Holm -> conclusion: no evidence that any simple rule lowers hits; "guess nothing"
  tickets are no better than random.
- Even a surviving rule with a small mean shift would not make 0 hits attainable in practice; it would be
  reported with its effect size and needs confirmation on future draws before being called real.
