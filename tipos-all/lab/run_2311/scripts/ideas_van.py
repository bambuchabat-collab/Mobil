"""Subagent 5: pre-registered VAN hypothesis H9 + descriptive D3, D6 (see ../ideas_prereg.md).
python3 -I ideas_van.py -> ../ideas_van_results.json
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from math import comb
from ideas_common import DATA, BASE

van = json.load(open(os.path.join(DATA, 'van.json')))
n = len(van)
TIERS = [0, 1, 2, 3, 8, 9, 10, 11]
TOT = comb(22, 11)
p = np.zeros(12)
for h in TIERS:
    p[h] = comb(11, h) * comb(11, 11 - h) / TOT
bets = np.array([v['bets'] for v in van])
NC = np.zeros((n, 12)); E = np.zeros((n, 12))
for t, v in enumerate(van):
    for h in TIERS:
        NC[t, h] = v['tiers'][str(h)][1]
        E[t, h] = bets[t] * p[h]
Dm = np.zeros((n, 22))
for t, v in enumerate(van):
    Dm[t, np.array(v['main']) - 1] = 1
A = np.where(E > 0, (NC - E) / np.where(E > 0, E, 1), 0.0)   # (n-E)/E
B = np.where(E > 0, 1 / np.where(E > 0, E, 1), 0.0)            # 1/E (0 for non-winning h)

pats = {}
for k in range(1, 13):
    pats[f'{k}-{k + 10}'] = list(range(k, k + 11))
pats['odd'] = list(range(1, 23, 2)); pats['even'] = list(range(2, 23, 2))
PM = np.zeros((len(pats), 22))
for i, s in enumerate(pats.values()):
    PM[i, np.array(s) - 1] = 1


def mhat(Pmat):
    H = (Dm @ Pmat.T).astype(int)              # n x npat hits
    rows = np.repeat(np.arange(n)[:, None], H.shape[1], 1)
    num = A[rows, H].sum(); den = B[rows, H].sum()
    return num / den if den > 0 else 0.0, H


m_obs, Hobs = mhat(PM)
rng = np.random.default_rng(20261132)
R = 9999
null = np.empty(R)
for r in range(R):
    Pm = np.zeros((len(pats), 22))
    for i in range(len(pats)):
        Pm[i, rng.choice(22, 11, replace=False)] = 1
    null[r] = mhat(Pm)[0]
pval = float((1 + (null >= m_obs).sum()) / (R + 1))

# descriptive per pattern: cells and excess
cells = []
for i, name in enumerate(pats):
    for t in range(n):
        h = Hobs[t, i]
        if h in (9, 10, 2, 1):
            cells.append(dict(pattern=name, date=van[t]['date'], hits=int(h), tier_winners=int(NC[t, h]),
                              expected=round(float(E[t, h]), 2), excess=round(float(NC[t, h] - E[t, h]), 1)))
# D3 fixed prizes
prizes = {str(h): sorted(set(v['tiers'][str(h)][0] for v in van if v['tiers'][str(h)][1] > 0)) for h in TIERS}
# D6 over-dispersion and calibration
disp = {}
for h in (1, 2, 3, 8, 9, 10):
    z = (NC[:, h] - E[:, h]) / np.sqrt(E[:, h])
    disp[str(h)] = dict(obs_over_exp=float(NC[:, h].sum() / E[:, h].sum()), var_z=float(z.var()),
                        mean_exp=float(E[:, h].mean()))
top_obs = int(NC[:, 11].sum() + NC[:, 0].sum()); top_exp = float(E[:, 11].sum() + E[:, 0].sum())
lam = float(bets.mean() * 2 / TOT)
share = (1 - np.exp(-lam)) / lam
res = dict(
    H9=dict(m_hat_obs=float(m_obs), p=pval, R=R, seed=20261132, null_mean=float(null.mean()),
            null_q95=float(np.quantile(null, 0.95)), n_patterns=len(pats),
            n_cells_9_10_2_1=len(cells), cells_9_10_2_1=cells,
            interpretation='m_hat = inverse-variance estimate of extra players per pattern ticket (beyond uniform)'),
    D3_prizes_seen=prizes,
    D6_dispersion=disp,
    top_prize=dict(observed_winners=top_obs, expected_uniform=top_exp, mean_bets=float(bets.mean()),
                   lambda_cowinners_random_ticket=lam, share_factor=float(share),
                   max_gain_pp_of_stake=float(100 * (1 - share) * 100000 * 2 / TOT / 1.5)))
json.dump(res, open(os.path.join(BASE, 'ideas_van_results.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps({k: (v if k != 'H9' else {kk: vv for kk, vv in v.items() if kk != 'cells_9_10_2_1'})
                  for k, v in res.items()}, indent=1, ensure_ascii=False))
for c in cells:
    if c['hits'] in (10, 1): print(c)
