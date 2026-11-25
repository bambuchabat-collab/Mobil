"""Common walk-forward harness for 'anti-hit' rules in Všetko alebo nič (11 of 22).
A rule is a function rule(past) -> iterable of 11 distinct ints in 1..22, where `past` is the list of
draws strictly before the evaluated draw (dicts: date, day, main (sorted), order (draw order)), oldest first.
evaluate(rule, name) walks forward over draws START..end and returns exact one-sided p-values for
 (a) mean hits < 5.5 (ticket hits fewer drawn numbers than random), (b) more draws with 0-3 hits than expected.
Usage inside an agent script:
    import sys; sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2511'); from harness import evaluate, DRAWS
"""
import json, os
import numpy as np
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__))
DRAWS = json.load(open(os.path.join(HERE, 'van412.json')))
START = 30                      # first evaluated draw index (every rule sees >= 30 past draws)
PMF = np.array([comb(11, k) * comb(11, 11 - k) for k in range(12)], float) / comb(22, 11)
PZ = {11: 100000, 10: 200, 9: 20, 8: 3, 3: 3, 2: 20, 1: 200, 0: 100000}
P_LOW = PMF[:4].sum()           # P(hits <= 3) = 0.04305

def _sum_pmf(n):
    out = np.array([1.0])
    for _ in range(n): out = np.convolve(out, PMF)
    return out

def evaluate(rule, name, start=START):
    hits = []
    for t in range(start, len(DRAWS)):
        T = set(int(x) for x in rule(DRAWS[:t]))
        assert len(T) == 11 and all(1 <= x <= 22 for x in T), (name, t, T)
        hits.append(len(T & set(DRAWS[t]['main'])))
    hits = np.array(hits); n = len(hits); S = int(hits.sum())
    pmf_sum = _sum_pmf(n)
    p_mean = float(pmf_sum[:S + 1].sum())                      # exact P(sum <= S) under the null
    low = int((hits <= 3).sum())
    k = np.arange(n + 1)
    binom = np.array([comb(n, int(i)) for i in k], float) * P_LOW ** k * (1 - P_LOW) ** (n - k)
    p_low = float(binom[low:].sum())                           # exact P(#low >= observed)
    won = sum(PZ.get(int(h), 0) for h in hits)
    return {'rule': name, 'n': n, 'mean_hits': S / n, 'p_mean_lower': p_mean,
            'n_hits_le3': low, 'expected_le3': n * P_LOW, 'p_le3': p_low,
            'n_zero': int((hits == 0).sum()), 'won_eur': won, 'cost_eur': 1.5 * n}
