"""Estimate how Slovak players actually pick their numbers.

The trick: the number of tier-3 winners in a draw is a thermometer for how
popular that draw's five numbers are. Compare observed winners against what
uniform random play predicts, then attribute the gap to individual numbers.
"""
import json, math
import numpy as np
from math import comb

rows = [r for r in json.load(open('data/draws_2014_2026.json')) if r['deposits'] and r['w3']]
C = comb(35, 5)
P3 = comb(5, 3) * comb(30, 2) / C
PRICE = 0.50


def fit(sub, lam=3.0):
    """Ridge regression of log(observed/expected winners) on number indicators."""
    n = len(sub)
    y = np.array([math.log(r['w3'] / ((r['deposits'] / PRICE) * P3)) for r in sub])
    X = np.zeros((n, 35))
    for i, r in enumerate(sub):
        for num in r['nums']:
            X[i, num - 1] = 1.0
    Xc = np.column_stack([np.ones(n), X])
    A = Xc.T @ Xc + lam * np.eye(36)
    A[0, 0] -= lam                       # leave the intercept unpenalised
    b = np.linalg.solve(A, Xc.T @ y)
    return b[0], b[1:] - b[1:].mean()


_, pop = fit(rows)
order = np.argsort(pop)
print(f"=== PER-NUMBER PLAYER POPULARITY  (n={len(rows)} draws) ===")
print("negative = under-played = you share the pot with fewer people\n")
for rank, i in enumerate(order, 1):
    pct = (math.exp(pop[i]) - 1) * 100
    bar = ('-' if pct < 0 else '+') * min(int(abs(pct) * 1.6), 26)
    print(f"  {rank:2d}. number {i+1:2d}  {pct:+6.1f}%  {bar}")

# out-of-sample check
train = [r for r in rows if r['date'] < '2025-01-01']
test = [r for r in rows if r['date'] >= '2025-01-01']
_, pop_tr = fit(train)
yt = np.array([math.log(r['w3'] / ((r['deposits'] / PRICE) * P3)) for r in test])
pred = np.array([sum(pop_tr[n - 1] for n in r['nums']) for r in test])
c = np.corrcoef(pred, yt)[0, 1]
t = c * math.sqrt((len(yt) - 2) / (1 - c * c))
print(f"\n=== OUT-OF-SAMPLE ({len(train)} train / {len(test)} test) ===")
print(f"  r = {c:+.3f}, t = {t:+.2f}, slope = {np.polyfit(pred, yt, 1)[0]:.2f}")
np.save('data/pop_full.npy', pop)
