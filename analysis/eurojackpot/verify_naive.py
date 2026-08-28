"""
INDEPENDENT CHECK #1 - deliberately naive.

No binomial coefficients, no hypergeometric formulas, no vectorisation.
Just itertools.combinations and set intersections, counting draws one by one.

It enumerates all C(50,5) = 2,118,760 main draws and all C(12,2) = 66 euro
draws for the two concrete tickets, then combines the two tallies (main and
euro draws are independent, and the combination is an exact integer product
over the full 139,838,160-outcome space).

Must agree with exact_model.py to the last digit.
"""

from fractions import Fraction
from itertools import combinations

# The two concrete tickets analysed in REPORT.md
T1_MAIN, T1_EURO = {33, 38, 42, 47, 50}, {5, 11}
T2_MAIN, T2_EURO = {34, 36, 43, 45, 49}, {8, 12}

PAYING = {(5, 2), (5, 1), (5, 0), (4, 2), (4, 1), (3, 2),
          (4, 0), (2, 2), (3, 1), (3, 0), (1, 2), (2, 1)}

assert not (T1_MAIN & T2_MAIN), "tickets must have disjoint main numbers"
assert not (T1_EURO & T2_EURO), "tickets must have disjoint euro pairs"

# --- tally main draws -------------------------------------------------------
main_tally = {}
n_main = 0
for draw in combinations(range(1, 51), 5):
    d = set(draw)
    key = (len(d & T1_MAIN), len(d & T2_MAIN))
    main_tally[key] = main_tally.get(key, 0) + 1
    n_main += 1

# --- tally euro draws -------------------------------------------------------
euro_tally = {}
n_euro = 0
for draw in combinations(range(1, 13), 2):
    d = set(draw)
    key = (len(d & T1_EURO), len(d & T2_EURO))
    euro_tally[key] = euro_tally.get(key, 0) + 1
    n_euro += 1

total = n_main * n_euro
print(f"main draws enumerated : {n_main:,}")
print(f"euro draws enumerated : {n_euro:,}")
print(f"total outcomes        : {total:,}")
assert total == 139_838_160

# --- combine ----------------------------------------------------------------
w_union = w_both = w_ge4 = w_42 = w_t1_any = 0
tier_counts_t1 = {}

for (m1, m2), wm in main_tally.items():
    for (e1, e2), we in euro_tally.items():
        w = wm * we
        p1 = (m1, e1) in PAYING
        p2 = (m2, e2) in PAYING
        if p1 or p2:
            w_union += w
        if p1 and p2:
            w_both += w
        if m1 >= 4 or m2 >= 4:
            w_ge4 += w
        if (m1, e1) == (4, 2) or (m2, e2) == (4, 2):
            w_42 += w
        if p1:
            w_t1_any += w
            tier_counts_t1[(m1, e1)] = tier_counts_t1.get((m1, e1), 0) + w

F = lambda w: Fraction(w, total)

print("\n--- NAIVE RESULTS (two tickets, disjoint mains + disjoint euro pairs) ---")
print(f"P(any prize, one ticket) = {F(w_t1_any)}  = {float(F(w_t1_any)) * 100:.6f}%")
print(f"P(any prize, 2 tickets)  = {F(w_union)}  = {float(F(w_union)) * 100:.6f}%")
print(f"P(both tickets win)      = {F(w_both)}  = {float(F(w_both)) * 100:.6f}%")
print(f"P(>=4 main, 2 tickets)   = {F(w_ge4)}  = {float(F(w_ge4)) * 100:.6f}%")
print(f"P(4+2, 2 tickets)        = {F(w_42)}  = {float(F(w_42)) * 100:.6f}%")

print("\nper-tier outcome counts for ticket 1:")
for tier in sorted(tier_counts_t1, key=lambda t: -tier_counts_t1[t]):
    print(f"  {tier[0]}+{tier[1]}: {tier_counts_t1[tier]:>10,}")

# --- cross-check against the closed-form model ------------------------------
from exact_model import two_ticket_stats, p_any_prize_single, tier_count

st = two_ticket_stats(0, 0)
checks = [
    ("P(any prize, one ticket)", F(w_t1_any), p_any_prize_single()),
    ("P(any prize, 2 tickets)", F(w_union), st["p_union_any_prize"]),
    ("P(both tickets win)", F(w_both), st["p_both_win"]),
    ("P(>=4 main, 2 tickets)", F(w_ge4), st["p_union_ge4_main"]),
    ("P(4+2, 2 tickets)", F(w_42), st["p_union_4plus2"]),
]

print("\n--- CROSS-CHECK: naive enumeration vs closed-form model ---")
ok = True
for label, naive, closed in checks:
    same = naive == closed
    ok &= same
    print(f"  {label:<28} {'IDENTICAL' if same else 'MISMATCH'}")

for (k, j), c in tier_counts_t1.items():
    if c != tier_count(k, j):
        ok = False
        print(f"  tier {k}+{j} MISMATCH: naive {c} vs closed-form {tier_count(k, j)}")

print("\nALL EXACT MATCHES" if ok else "\nDISCREPANCY FOUND")
raise SystemExit(0 if ok else 1)
