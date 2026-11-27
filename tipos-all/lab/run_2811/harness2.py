"""Walk-forward harness for PREDICTION formulas (28.11.2026).
A formula is f(past, date) -> T numbers predicted to be DRAWN; `past` = draws strictly before the evaluated one
(oldest first, dicts with date, main (sorted), order, and for EM also 'extra'); `date` = the evaluated draw's date (known in advance).
evaluate(f, game, name) returns exact one-sided p-values for MORE hits than chance (p_upper, primary) and fewer (p_lower).
Games: 'VAN' (11 of 22, ticket 11) and 'EM' (Euromilióny: 7 main numbers of N, ticket = 7 numbers; N from data).
Usage: import sys; sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2811'); from harness2 import evaluate, load
"""
import json, os
import numpy as np
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__))
def load(game):
    return json.load(open(os.path.join(HERE, 'data', {'VAN': 'van415.json', 'EM': 'em.json'}[game])))
def params(game):
    d = load(game)
    if game == 'VAN': return d, 22, 11, 11
    N = max(max(r['main']) for r in d); return d, N, 7, 7
def evaluate(f, game, name, start=30):
    d, N, K, T = params(game)
    pmf = np.array([comb(T, k) * comb(N - T, K - k) for k in range(T + 1)], float) / comb(N, K)
    hits = []
    for t in range(start, len(d)):
        P = set(int(x) for x in f(d[:t], d[t]['date']))
        assert len(P) == T and all(1 <= x <= N for x in P), (name, t, P)
        hits.append(len(P & set(d[t]['main'])))
    hits = np.array(hits); n = len(hits); S = int(hits.sum())
    s = np.array([1.0])
    for _ in range(n): s = np.convolve(s, pmf)
    mu = float((np.arange(T + 1) * pmf).sum())
    return {'rule': name, 'game': game, 'n': n, 'mean_hits': S / n, 'expected': mu,
            'p_upper': float(s[S:].sum()), 'p_lower': float(s[:S + 1].sum()),
            'hist': np.bincount(hits, minlength=T + 1).tolist()}
