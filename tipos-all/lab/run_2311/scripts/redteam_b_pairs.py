"""Red team, attack (b): is the consecutive-pair effect (P2) real, or confounded with per-number popularity,
and is a 3-pair field an extrapolation?  python3 -I redteam_b_pairs.py -> ../redteam_b.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from redteam_common import *

logB = np.log(B)
COV = np.column_stack([np.ones(N), PRE, THU, PREM, logB - logB.mean()]).astype(float)
CLAIM13 = set(CLAIM_ORDER[:13])
pair_list = [(i, i + 1) for i in range(1, 27)]


def pair_count(sel_pairs):
    s = set(sel_pairs)
    return np.array([sum(1 for a, b in zip(r, r[1:]) if b == a + 1 and (a, b) in s) for r in MAIN], float)


def gap_count(g):
    return np.array([sum(1 for a in r for b in r if b - a == g) for r in MAIN], float)


def ols(X, y):
    th, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ th; dof = len(y) - np.linalg.matrix_rank(X)
    XtXi = np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.diag(XtXi) * (res @ res) / dof)
    meat = (X * res[:, None]).T @ (X * res[:, None]); hc = np.sqrt(np.diag(XtXi @ meat @ XtXi) * len(y) / dof)
    return th, se, hc


out = {}
# 1. joint fits: pair coefficient with/without per-number control, OLS (no shrinkage => numbers cannot leak into pairs)
fits = {}
for m in (3, 4, 5):
    y = Y[m]
    r = {}
    th, se, hc = ols(np.column_stack([COV, NPAIR]), y)
    r['no_number_control'] = (th[-1], se[-1], hc[-1])
    th, se, hc = ols(np.column_stack([COV, NPAIR, Z]), y)
    r['OLS_27_numbers'] = (th[5], se[5], hc[5])
    # post-era only
    ii = np.where(POST)[0]
    X = np.column_stack([COV[ii][:, [0, 2, 3, 4]], NPAIR[ii], Z[ii]])
    th, se, hc = ols(X, y[ii]); r['OLS_27_numbers_post_era'] = (th[4], se[4], hc[4])
    # pairs split by popularity class of the pair (both numbers in claimed 13 least popular vs not)
    unpop = [p for p in pair_list if p[0] in CLAIM13 and p[1] in CLAIM13]
    other = [p for p in pair_list if p not in unpop]
    X = np.column_stack([COV, pair_count(unpop), pair_count(other), Z])
    th, se, hc = ols(X, y)
    r['split_unpopular_pairs'] = (th[5], se[5], hc[5]); r['split_other_pairs'] = (th[6], se[6], hc[6])
    # other "clustering" features alongside pairs
    X = np.column_stack([COV, NPAIR, gap_count(2), gap_count(3), Z])
    th, se, hc = ols(X, y)
    r['with_gap2_gap3:pairs'] = (th[5], se[5], hc[5]); r['with_gap2_gap3:gap2'] = (th[6], se[6], hc[6])
    r['with_gap2_gap3:gap3'] = (th[7], se[7], hc[7])
    # saturating version: dummies 1, 2, 3 pairs
    X = np.column_stack([COV, NPAIR == 1, NPAIR == 2, NPAIR >= 3, Z]).astype(float)
    th, se, hc = ols(X, y)
    r['dummy_1pair'] = (th[5], se[5], hc[5]); r['dummy_2pairs'] = (th[6], se[6], hc[6]); r['dummy_3pairs'] = (th[7], se[7], hc[7])
    fits[f'{m}match'] = {k: {'coef': float(v[0]), 'se': float(v[1]), 'se_HC0': float(v[2]),
                             'pct_per_unit': float(100 * (np.exp(v[0]) - 1))} for k, v in r.items()}
    print(m, {k: (round(v['coef'], 4), round(v['se'], 4)) for k, v in fits[f'{m}match'].items()})
out['joint_fits'] = fits
out['draws_by_npairs'] = {str(k): int(np.sum(NPAIR == k)) for k in range(5)}
out['uniform_draw_npairs_distribution'] = {str(k): float(np.mean(NPAIR_ALL == k)) for k in range(6)}
print(out['draws_by_npairs'], out['uniform_draw_npairs_distribution'])

# 2. past-only walk-forward: OOS MSE of [cov + numbers(ridge lam=3)] vs [... + pairs]; pair coefficient path
def wf(m, lam=3.0, t0=40):
    e0, e1, gpath = [], [], []
    for t in range(t0, N):
        tr = np.arange(t)
        X0 = np.column_stack([COV[tr], Z[tr]]); X1 = np.column_stack([COV[tr], NPAIR[tr], Z[tr]])
        keep0 = [c for c in range(5) if c == 0 or np.ptp(COV[tr, c]) > 0]
        X0 = np.column_stack([COV[tr][:, keep0], Z[tr]]); X1 = np.column_stack([COV[tr][:, keep0], NPAIR[tr], Z[tr]])
        k = len(keep0)
        th0, _ = ridge(X0, Y[m][tr], np.r_[np.full(k, 1e-9), np.full(27, lam)])
        th1, _ = ridge(X1, Y[m][tr], np.r_[np.full(k + 1, 1e-9), np.full(27, lam)])
        x0 = np.r_[COV[t, keep0], Z[t]]; x1 = np.r_[COV[t, keep0], NPAIR[t], Z[t]]
        e0.append(Y[m][t] - x0 @ th0); e1.append(Y[m][t] - x1 @ th1); gpath.append(th1[k])
    e0, e1, gpath = map(np.array, (e0, e1, gpath))
    # sign-flip / permutation of the pair feature on the evaluation draws is not clean; use paired test on squared errors
    d = e0 ** 2 - e1 ** 2
    return {'oos_mse_reduction_pct': float(100 * (1 - np.mean(e1 ** 2) / np.mean(e0 ** 2))),
            'paired_t_on_sq_errors': float(d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))),
            'pair_coef_first_last_min_max': [float(gpath[0]), float(gpath[-1]), float(gpath.min()), float(gpath.max())]}

out['walk_forward_pairs'] = {f'{m}match': wf(m) for m in (3, 4, 5)}
print(out['walk_forward_pairs'])

# 3. extrapolation: npairs(D) over the draws D that make each field win tier m (|S∩D| = m)
def support(field):
    S = np.zeros(27, bool); S[np.array(field) - 1] = True
    ov = DB[:, S].sum(1)
    res = {}
    for m in (3, 4, 5, 6):
        sel = ov == m; h = np.bincount(NPAIR_ALL[sel].astype(int), minlength=6) / sel.sum()
        res[f'{m}match'] = {str(k): round(float(h[k]), 4) for k in range(6) if h[k] > 0}
    return res

out['npairs_of_winning_draws'] = {'field1 ' + ' '.join(map(str, FINAL[0])): support(FINAL[0]),
                                  'field2 ' + ' '.join(map(str, FINAL[2])): support(FINAL[2]),
                                  'random-like 2-pair field 1 2 10 15 16 23 (for contrast)': support([1, 2, 10, 15, 16, 23])}
print(json.dumps(out['npairs_of_winning_draws'], indent=0)[:1500])
json.dump(out, open(os.path.join(BASE, 'redteam_b.json'), 'w'), indent=1)
