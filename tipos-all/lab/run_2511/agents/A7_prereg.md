# A7 pre-registration — GEOMETRIC / TRANSFORM RULES on the previous draw

Written: Wed Nov 25 05:55:36 UTC 2026 (before any evaluation was run; no evaluation-draw statistics looked at).

Data/harness: lab/run_2511/van412.json, harness.evaluate (walk-forward over draws 30..411, n = 382).
Notation: D_t = set of 11 numbers of draw t; past = draws 0..t-1; P = D_{t-1} (last draw in past).
Complement C(S) = {1..22} \ S. Overlap of a candidate ticket with a draw = |ticket ∩ draw| (lower is better).
Primary metric: p_mean_lower. Secondary: p_le3. No multiple-testing correction applied here.

Not redone: plain complement C(P) and P itself (identity transform) — already tested 24.11.

## R1 (PRIMARY) — adaptive walk-forward selection over a fixed transform family
Family G (44 permutations of 1..22, fixed in this order):
- rotations r_k(x) = ((x - 1 + k) mod 22) + 1 for k = 1..21 (k=1 is "shift +1", k=21 is "shift -1", k=11 is
  the vertical flip of an 11x2 slip with rows 1..11 / 12..22);
- reflections f_c(x) = ((c - x) mod 22) + 1 for c = 0..21 (c = 0 gives x -> 23 - x, the mirror; others are
  mirror composed with a rotation);
- parity flip p(x) = x + 1 if x odd else x - 1 (1<->2, 3<->4, ..., = vertical flip of an 11x2 slip laid out
  column-wise (1,2),(3,4),...).
Candidates: for each g in G, two tickets: g(P) ("image") and C(g(P)) ("complement of image") -> 88 candidates,
ordered (g1,image),(g1,complement),(g2,image),... .
Rule: for each candidate c compute score(c) = sum over s = 1..t-1 of |c(D_{s-1}) ∩ D_s| (expanding window,
all transitions strictly inside past). Ticket = c(P) for the candidate with minimal score; ties -> first in
the fixed order above. No parameters.

## R2 — mirror x -> 23 - x, direction fixed on draws 0..29
m0 = mean over s = 1..29 of |M(D_{s-1}) ∩ D_s|, M(x) = 23 - x.
If m0 <= 5.5: ticket = M(P) for every evaluated draw; else ticket = C(M(P)). Direction frozen after draw 29.

## R3 — 5-column slip neighbour density, direction fixed on draws 0..29
Layout fixed a priori: 5 columns, number x at row (x-1)//5, column (x-1)%5 (rows 1-5, 6-10, 11-15, 16-20,
21-22). (5-column chosen over 11x2 because 11x2 row/column neighbours are already covered by R1 rotations
+-1 and 11.) N(x) = Moore (8-)neighbourhood of x on that grid, only cells that hold a number 1..22, x excluded.
Score f(x) = |N(x) ∩ P| / |N(x)|. Order numbers by (f(x), tiebreak(x)) ascending, tiebreak = position of x in a
fixed random permutation np.random.default_rng(2511).permutation(22)+1. A = first 11 (low neighbour density),
B = last 11 = C(A).
Direction: a0 = mean over s = 1..29 of |A_s ∩ D_s| (A_s built from D_{s-1}). If a0 <= 5.5 ticket = A,
else ticket = B. Direction frozen after draw 29.

## Output
agents/A7.py, agents/A7.json; ticket_25_11 = R1 applied to all 412 draws.
