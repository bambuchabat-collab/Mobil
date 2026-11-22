"""Descriptive (post hoc) stability of the H1 consecutive-pair coefficient by period; not a test.
python3 -I ideas_h1_stability.py"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from ideas_common import *
d = load_ev(); n = d['n']; D = d['D']
Y = np.column_stack([np.log(d['n3'] / d['bets']), np.log(d['n4'] / d['bets'])])
C = np.column_stack([np.ones(n), d['old'], d['thu'], d['prem'], np.log(d['bets']) - np.log(1e5)])
X = np.column_stack([C, ind27(D), f_consec(D)]); pen = np.array([1e-8] * 5 + [2.0] * 27 + [1e-8])
out = {}
dates = np.array(d['dates'])
for lab, sel in [('all', np.ones(n, bool)), ('2024-03..2025-06', dates < '2025-07-01'),
                 ('2025-07..2026-11', dates >= '2025-07-01'), ('mondays', d['thu'] == 0), ('thursdays', d['thu'] == 1)]:
    Xs, Ys = X[sel], Y[sel]
    b = np.linalg.solve(Xs.T @ Xs + np.diag(pen), Xs.T @ Ys)
    r = Ys - Xs @ b; s2 = (r ** 2).sum(0) / max(1, sel.sum() - 20)
    A = np.linalg.inv(Xs.T @ Xs + np.diag(pen)); se = np.sqrt(np.diag(A)[-1] * s2)
    out[lab] = dict(n=int(sel.sum()), gamma_y3=float(b[-1, 0]), se_y3=float(se[0]), gamma_y4=float(b[-1, 1]),
                    se_y4=float(se[1]))
cp = f_consec(D); out['consec_pairs_in_draws_hist'] = {int(k): int((cp == k).sum()) for k in np.unique(cp)}
json.dump(out, open(os.path.join(BASE, 'ideas_h1_stability.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
# linearity check: mean residual of M0 (no pair term) by number of consecutive pairs in the draw
X0 = np.column_stack([C, ind27(D)]); pen0 = np.array([1e-8] * 5 + [2.0] * 27)
b0 = np.linalg.solve(X0.T @ X0 + np.diag(pen0), X0.T @ Y); r0 = Y - X0 @ b0
lin = {int(k): dict(n=int((cp == k).sum()), mean_resid_y3=float(r0[cp == k, 0].mean()),
                    mean_resid_y4=float(r0[cp == k, 1].mean())) for k in np.unique(cp)}
out['M0_residual_by_pairs'] = lin
json.dump(out, open(os.path.join(BASE, 'ideas_h1_stability.json'), 'w'), indent=1)
print(json.dumps(lin, indent=1))
