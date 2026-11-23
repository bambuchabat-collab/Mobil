"""Red team, attack (a): independent minimal walk-forward of per-number popularity (P1).
Each draw t is predicted ONLY from earlier draws of the same subset:
  covariate baseline = OLS of y on [1, pre-era, thu, premium, log bets] (+ optional #pairs) on past draws,
  beta_i = (26/21) * (mean past residual of draws containing i - mean past residual)   [no ridge, no tuning]
  prediction p_t = sum_{i in D_t} beta_i ; target r_t = y_t - covariate baseline prediction.
Metric: corr(p_t, r_t); p-value by permuting number labels of beta (same permutation for all t), R=20000.
python3 -I redteam_a_walkforward.py -> ../redteam_a.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from redteam_common import *

rng = np.random.default_rng(23112026)
R = 20000
logB = np.log(B)


def covX(idx, with_pairs):
    cols = [np.ones(len(idx)), PRE[idx].astype(float), THU[idx].astype(float), PREM[idx].astype(float), logB[idx]]
    if with_pairs:
        cols.append(NPAIR[idx])
    return np.column_stack(cols)


def walk(m, subset, burn, with_pairs=False, baseline='ols'):
    ii = np.where(subset)[0]
    P, Rr, Dt, Bstore = [], [], [], []
    for j in range(burn, len(ii)):
        tr, t = ii[:j], ii[j]
        y = Y[m][tr]
        if baseline == 'ols':
            X = covX(tr, with_pairs)
            keep = [0] + [c for c in range(1, X.shape[1]) if np.ptp(X[:, c]) > 0]
            th, *_ = np.linalg.lstsq(X[:, keep], y, rcond=None)
            res = y - X[:, keep] @ th
            pred_cov = covX(np.array([t]), with_pairs)[0, keep] @ th
        else:   # no covariates at all: local baseline = mean of the previous 10 draws
            loc = np.array([y[max(0, k - 10):k].mean() if k else y[0] for k in range(len(tr))])
            res = (y - loc)[1:]; trz = tr[1:]
            pred_cov = y[-10:].mean()
        Zt = Z[tr] if baseline == 'ols' else Z[trz]
        cnt = Zt.sum(0)
        beta = (26 / 21) * ((Zt.T @ res) / np.maximum(cnt, 1) - res.mean())
        beta -= beta.mean()
        P.append(Z[t] @ beta); Rr.append(Y[m][t] - pred_cov); Dt.append(t); Bstore.append(beta)
    P, Rr, Bs = np.array(P), np.array(Rr), np.array(Bstore)
    obs = corr(P, Rr)
    Zt = Z[np.array(Dt)]
    rc = (Rr - Rr.mean()) / Rr.std()
    cnt = 0; done = 0
    while done < R:
        k = min(2000, R - done)
        perms = np.argsort(rng.random((k, 27)), 1)
        Pm = np.einsum('tj,tkj->tk', Zt, Bs[:, perms])
        Pm = (Pm - Pm.mean(0)) / Pm.std(0)
        cnt += int(np.sum(rc @ Pm / len(rc) >= obs - 1e-12)); done += k
    slope = float(np.polyfit(P, Rr, 1)[0])
    r2 = float(1 - np.sum((Rr - P) ** 2) / np.sum((Rr - Rr.mean()) ** 2))
    return {'n_eval': int(len(P)), 'first_eval': DATES[Dt[0]], 'corr': obs, 'p_perm': (1 + cnt) / (1 + R),
            'calib_slope': slope, 'R2_oos_vs_mean': r2}


subsets = {
    'all_draws': (np.ones(N, bool), 40),
    'drop_2024_(train+eval from 2025-01-01)': (DATES >= '2025-01-01', 30),
    'drop_premium_months': (~PREM, 40),
    'monday_only': (~THU, 40),
    'post_era_only_2026': (DATES >= '2026-01-01', 25),
}
out = {'method': __doc__.strip().splitlines()[0], 'results': {}}
for name, (sub, burn) in subsets.items():
    for m in (3, 4, 5):
        key = f'{name}|{m}match'
        out['results'][key] = walk(m, sub, burn)
        print(key, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out['results'][key].items()}, flush=True)
# variants on all draws
for m in (3, 4, 5):
    key = f'all_draws_with_pair_covariate|{m}match'
    out['results'][key] = walk(m, np.ones(N, bool), 40, with_pairs=True)
    print(key, out['results'][key], flush=True)
    key = f'all_draws_no_covariates_local_baseline|{m}match'
    sub = POST if m == 3 else np.ones(N, bool)      # pre-era 3-match level jump would need a dummy
    out['results'][key] = walk(m, sub, 30, baseline='local')
    print(key, out['results'][key], flush=True)

# Holm over the 15 subset x tier tests (family of the robustness runs)
keys = [k for k in out['results'] if k.split('|')[0] in subsets]
ps = sorted((out['results'][k]['p_perm'], k) for k in keys)
run = 0
for i, (p, k) in enumerate(ps):
    run = max(run, min(1, (len(ps) - i) * p)); out['results'][k]['p_holm_15'] = run

# full-data per-number estimate (post era, OLS covariates incl. pairs) and half-split stability of the ranking
def beta_full(sel, m, with_pairs=True):
    tr = np.where(sel)[0]
    X = covX(tr, with_pairs); keep = [0] + [c for c in range(1, X.shape[1]) if np.ptp(X[:, c]) > 0]
    th, *_ = np.linalg.lstsq(X[:, keep], Y[m][tr], rcond=None); res = Y[m][tr] - X[:, keep] @ th
    b = (26 / 21) * ((Z[tr].T @ res) / Z[tr].sum(0) - res.mean()); return b - b.mean()

post = np.where(POST)[0]; h1 = np.zeros(N, bool); h2 = np.zeros(N, bool)
h1[post[:len(post) // 2]] = True; h2[post[len(post) // 2:]] = True
stab = {}
for m in (3, 4):
    b1, b2, ba = beta_full(h1, m), beta_full(h2, m), beta_full(POST, m)
    stab[f'{m}match'] = {'corr_half1_vs_half2': corr(b1, b2),
                         'order_least_popular_post_era': [int(i) + 1 for i in np.argsort(ba)],
                         'corr_with_claimed_order_rank': corr(np.argsort(np.argsort(ba)),
                                                              np.array([CLAIM_ORDER.index(i + 1) for i in range(27)]))}
    print(m, stab[f'{m}match'])
out['ranking_stability'] = stab
ticket_nums = sorted(FINAL[0] + FINAL[2])
o3 = stab['3match']['order_least_popular_post_era']
out['ticket_numbers_rank_in_claimed_order'] = {i: CLAIM_ORDER.index(i) + 1 for i in ticket_nums}
out['ticket_numbers_rank_in_redteam_3match_order'] = {i: o3.index(i) + 1 for i in ticket_nums}
json.dump(out, open(os.path.join(BASE, 'redteam_a.json'), 'w'), indent=1)
print(json.dumps({k: out[k] for k in ('ticket_numbers_rank_in_claimed_order', 'ticket_numbers_rank_in_redteam_3match_order')}))
