"""Red team, P5 (VAN): are tiers 10/9/8 and 1/2/3 fixed in all draws, and are all-odd / all-even tickets over-played?
Statistic: mean standardized excess (n-E)/sqrt(E) in the tier cells where the all-odd or all-even ticket lands;
null: the same statistic for a random 11-set and its complement (odd/even are complements), 5000 reps.
python3 -I redteam_p5_van.py -> ../redteam_p5.json"""
import json, os
from math import comb
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = json.load(open(os.path.join(BASE, 'data', 'van.json')))
rng = np.random.default_rng(5)
FIX = {'10': 200, '1': 200, '9': 20, '2': 20, '8': 3, '3': 3}
viol = [(x['date'], k, x['tiers'][k][0]) for x in V for k, p in FIX.items() if x['tiers'][k][1] > 0 and abs(x['tiers'][k][0] - p) > 1e-9]
P = {h: comb(11, h) * comb(11, 11 - h) / comb(22, 11) for h in range(12)}
HS = (0, 1, 2, 3, 8, 9, 10, 11)
M = np.array([sorted(x['main']) for x in V]); bets = np.array([x['bets'] for x in V])
cnt = {h: np.array([x['tiers'][str(h)][1] for x in V], float) for h in HS}


def stat(S):
    S = set(S); z = []
    for t in range(len(V)):
        k = len(S & set(M[t]))
        for h in {k, 11 - k}:
            if h in HS and h not in (0, 11):
                E = bets[t] * P[h]; z.append((cnt[h][t] - E) / np.sqrt(E))
    return float(np.mean(z)) if z else 0.0, len(z)


odd = list(range(1, 23, 2))
obs, ncell = stat(odd)
null = []
for _ in range(5000):
    S = rng.choice(np.arange(1, 23), 11, replace=False)
    null.append(stat(S)[0])
null = np.array(null)
ex = [(x['date'], int(sum(1 for v in x['main'] if v % 2)), {h: (x['tiers'][str(h)][1], round(x['bets'] * P[h], 1)) for h in (1, 2, 3, 8, 9, 10)})
      for x in V if x['date'] == '2025-10-10']
out = {'n_draws': len(V), 'fixed_tier_violations': viol, 'odd_even_mean_z': obs, 'cells': ncell,
       'null_mean': float(null.mean()), 'null_q99': float(np.quantile(null, 0.99)), 'p': float((1 + np.sum(null >= obs)) / (1 + len(null))),
       'example_2025_10_10': ex}
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(BASE, 'redteam_p5.json'), 'w'), indent=1)
