#!/usr/bin/env python3
"""Extra výplata: player-popularity update, strict walk-forward, money conversion, 2-field optimiser.
Pre-registered plan: lab/run_2311/popularity_prereg.md (written before any fit).
Run from anywhere:  python3 -I lab/run_2311/scripts/popularity.py  -> lab/run_2311/popularity.json
Numbers cannot be predicted; this only concerns how many co-winners share a pari-mutuel prize."""
import json, os, sys, time, hashlib, itertools
from math import comb
import numpy as np

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data', 'ev.json')
OLD = os.path.join(ROOT, '..', 'agent_extra', 'popularity_results.json')
OUT = os.path.join(ROOT, 'popularity.json')
QUICK = '--quick' in sys.argv
rng = np.random.default_rng(20261123)
def log(*a): print(f'[{time.time()-T0:6.1f}s]', *a, flush=True)

# ---------------------------------------------------------------- data
raw = open(DATA, 'rb').read(); SHA = hashlib.sha256(raw).hexdigest()
d = json.loads(raw); n = len(d)
P = {m: comb(6, m) * comb(21, 6 - m) / comb(27, 6) for m in range(7)}
NM = {m: comb(6, m) * comb(21, 6 - m) for m in range(7)}
CATS = (3, 4, 5)
CM = {m: m / 6 - (6 - m) / 21 for m in range(7)}          # linearised log-linear player model
Z = np.zeros((n, 27))
for t, x in enumerate(d): Z[t, np.array(x['main']) - 1] = 1
pb = np.array([x['pb'] for x in d])
Bt = np.array([x['deposits'] / 1.5 for x in d])
pre = np.array([0. if '3+1' in x['tiers'] else 1. for x in d])
thu = np.array([1. if x['day'].startswith('Š') else 0. for x in d])
prem = np.array([1. if x['date'][:7] in ('2026-05', '2026-10') else 0. for x in d])
def npairs_of(s): s = set(s); return sum(1 for i in s if i + 1 in s)
npr = np.array([npairs_of(x['main']) for x in d], float)
logBc = np.log(Bt) - np.log(Bt).mean()
XC = np.column_stack([np.ones(n), npr, pre, thu, prem, logBc])
COVN = ['intercept', 'n_consecutive_pairs', 'pre_era_no_3+1_tier', 'thursday', 'premium_month', 'log_bets_c']
def tier(x, k): return x['tiers'].get(k, [0.0, 0])
W = {m: np.array([tier(x, f'{m}+0')[1] + tier(x, f'{m}+1')[1] for x in d], float) for m in CATS}
W1 = {m: np.array([tier(x, f'{m}+1')[1] for x in d], float) for m in CATS}
n1 = W1[4] + W1[5] + np.where(pre == 0, W1[3], 0)
ntot = W[4] + W[5] + np.where(pre == 0, W[3], 0)
s_obs = n1 / ntot
assert all((W[m] > 0).all() for m in CATS)
log('draws', n, d[0]['date'], d[-1]['date'], 'pre-era', int(pre.sum()), 'thu', int(thu.sum()), 'premium', int(prem.sum()))

def extra_fit(idx):
    sh = np.empty(7)
    for x in range(1, 8):
        sel = idx[pb[idx] == x]
        sh[x - 1] = n1[sel].sum() / ntot[sel].sum() if len(sel) else 1 / 7
    return sh

def targets(shat):
    E = {m: Bt * P[m] for m in CATS}
    E[3] = Bt * P[3] * np.where(pre == 1, 1 - shat[pb - 1], 1.0)
    return {m: np.log(W[m] / E[m]) for m in CATS}, E

# ---------------------------------------------------------------- ridge machinery
LGRID = [10, 30, 100, 300, 1000, 3000, 1e4, 3e4, 1e5]
UGRID = [0.1, 0.3, 1, 3, 10, 30]

def ridge(X, y, w, pen, loo=False):
    XtW = X.T * w
    Ainv = np.linalg.inv(XtW @ X + np.diag(pen))
    th = Ainv @ (XtW @ y)
    if not loo: return th, None
    h = np.einsum('ij,jk,ik->i', X, Ainv, X) * w
    ok = h < 1 - 1e-8                     # rows fitted exactly by their own dummy carry no CV information
    e = (y - X @ th)[ok] / (1 - h[ok])
    return th, float(np.sum(w[ok] * e * e) / np.sum(w[ok]))

def covcols(idx): return [0] + [j for j in range(1, XC.shape[1]) if np.ptp(XC[idx, j]) > 0]

def est_tau2(idx, y, E, Zm):
    cols = covcols(idx); k = len(cols)
    X = np.hstack([XC[idx][:, cols], Zm[idx]]); yy = y[idx]
    best = None
    for lu in UGRID:
        th, cv = ridge(X, yy, np.ones(len(idx)), np.r_[np.zeros(k), np.full(27, lu)], True)
        if best is None or cv < best[0]: best = (cv, th)
    res = yy - X @ best[1]
    return max(1e-6, float(np.mean(res ** 2) - np.mean(1 / E[idx])))

def fit_m1(idx, y, E, tau2, Zm=Z, lam=None):
    cols = covcols(idx); k = len(cols)
    X = np.hstack([XC[idx][:, cols], Zm[idx]]); yy = y[idx]; w = 1 / (tau2 + 1 / E[idx])
    if lam is None:
        best = None
        for l in LGRID:
            th, cv = ridge(X, yy, w, np.r_[np.zeros(k), np.full(27, l)], True)
            if best is None or cv < best[0]: best = (cv, l, th)
        _, lam, th = best
    else:
        th, _ = ridge(X, yy, w, np.r_[np.zeros(k), np.full(27, lam)])
    g = np.zeros(XC.shape[1]); g[cols] = th[:k]
    return {'g': g, 'b': th[k:], 'lam': lam}

def fit_cov(idx, y, E, tau2):
    cols = covcols(idx); X = XC[idx][:, cols]; w = 1 / (tau2 + 1 / E[idx])
    th, _ = ridge(X, y[idx], w, np.zeros(len(cols)))
    g = np.zeros(XC.shape[1]); g[cols] = th; return g

def fit_m2(idx, Y, E, tau2s, Zm=Z, lam=None):
    cols = covcols(idx); k = len(cols); ni = len(idx); p = 3 * k + 27
    X = np.zeros((3 * ni, p)); y = np.zeros(3 * ni); w = np.zeros(3 * ni)
    for c, m in enumerate(CATS):
        r = slice(c * ni, (c + 1) * ni)
        X[r, c * k:(c + 1) * k] = XC[idx][:, cols]; X[r, 3 * k:] = CM[m] * Zm[idx]
        y[r] = Y[m][idx]; w[r] = 1 / (tau2s[m] + 1 / E[m][idx])
    XtW = X.T * w; G = XtW @ X; v = XtW @ y
    blk = np.stack([np.arange(ni) + c * ni for c in range(3)], 1)          # (ni,3) rows per draw
    def solve(l, loo):
        Ainv = np.linalg.inv(G + np.diag(np.r_[np.zeros(3 * k), np.full(27, l)]))
        th = Ainv @ v
        if not loo: return th, None
        Xb = X[blk]; e = (y - X @ th)[blk]; wb = w[blk]
        H = np.einsum('bip,pq,bjq->bij', Xb, Ainv, Xb) * wb[:, None, :]
        IH = np.eye(3)[None] - H; ok = np.abs(np.linalg.det(IH)) > 1e-8
        el = np.linalg.solve(IH[ok], e[ok][..., None])[..., 0]
        return th, float(np.sum(wb[ok] * el * el) / np.sum(wb[ok]))
    if lam is None:
        best = None
        for l in LGRID:
            th, cv = solve(l, True)
            if best is None or cv < best[0]: best = (cv, l, th)
        _, lam, th = best
    else:
        th, _ = solve(lam, False)
    g = {}
    for c, m in enumerate(CATS):
        gg = np.zeros(XC.shape[1]); gg[cols] = th[c * k:(c + 1) * k]; g[m] = gg
    return {'g': g, 'a': th[3 * k:], 'lam': lam}

# ---------------------------------------------------------------- walk-forward
T_START = 40
TT = np.arange(T_START, n)
wf = {key: {f: [] for f in ('y', 'yfull', 'ycov', 'p')} for key in
      [f'M1_{m}' for m in CATS] + [f'M2_{m}' for m in CATS]}
coef_store = {f'M1_{m}': [] for m in CATS}; coef_store['M2'] = []
lam_store = {f'M1_{m}': [] for m in CATS}; lam_store['M2'] = []
tau_store = {m: [] for m in CATS}
ex_pred, ex_base, ex_shat = [], [], []
log('walk-forward', len(TT), 'draws')
for t in TT:
    idx = np.arange(t)
    sh = extra_fit(idx); ex_shat.append(sh); ex_pred.append(sh[pb[t] - 1]); ex_base.append(n1[idx].sum() / ntot[idx].sum())
    Y, E = targets(sh)
    taus = {m: est_tau2(idx, Y[m], E[m], Z) for m in CATS}
    for m in CATS:
        tau_store[m].append(taus[m])
        f1 = fit_m1(idx, Y[m], E[m], taus[m]); gc = fit_cov(idx, Y[m], E[m], taus[m])
        ycov = XC[t] @ gc
        for key, yfull, p in ((f'M1_{m}', XC[t] @ f1['g'] + Z[t] @ f1['b'], Z[t] @ f1['b']),):
            s = wf[key]; s['y'].append(Y[m][t]); s['yfull'].append(yfull); s['ycov'].append(ycov); s['p'].append(p)
        coef_store[f'M1_{m}'].append(f1['b']); lam_store[f'M1_{m}'].append(f1['lam'])
        wf[f'M2_{m}']['y'].append(Y[m][t]); wf[f'M2_{m}']['ycov'].append(ycov)
    f2 = fit_m2(idx, Y, E, taus)
    coef_store['M2'].append(f2['a']); lam_store['M2'].append(f2['lam'])
    for m in CATS:
        p = CM[m] * Z[t] @ f2['a']
        wf[f'M2_{m}']['p'].append(p); wf[f'M2_{m}']['yfull'].append(XC[t] @ f2['g'][m] + p)
for key in wf:
    for f in wf[key]: wf[key][f] = np.array(wf[key][f])
for key in coef_store: coef_store[key] = np.array(coef_store[key])
ex_pred = np.array(ex_pred); ex_base = np.array(ex_base); ex_shat = np.array(ex_shat)
log('walk-forward done')

def corr(a, b): return float(np.corrcoef(a, b)[0, 1])
def wf_metrics(s):
    y, yf, yc, p = s['y'], s['yfull'], s['ycov'], s['p']; r = y - yc
    return {'n': int(len(y)), 'corr_numberpart_vs_resid': corr(p, r),
            'R2_incremental_oos': float(1 - np.sum((y - yf) ** 2) / np.sum((y - yc) ** 2)),
            'R2_resid_oos': float(1 - np.sum((r - p) ** 2) / np.sum((r - r.mean()) ** 2)),
            'rmse_full': float(np.sqrt(np.mean((y - yf) ** 2))), 'rmse_cov_only': float(np.sqrt(np.mean((y - yc) ** 2))),
            'calib_slope_r_on_p': float(np.polyfit(p, r, 1)[0])}

def perm_p(Dm, Bm, r, R, scale=1.0):
    obs = corr((Dm * Bm).sum(1), r); cnt = 0; done = 0; rc = (r - r.mean()) / r.std()
    while done < R:
        k = min(1000, R - done)
        perms = np.argsort(rng.random((k, 27)), 1)
        Pm = np.einsum('tj,tkj->tk', Dm, Bm[:, perms])         # (T,k)
        Pm = (Pm - Pm.mean(0)) / Pm.std(0)
        cnt += int(np.sum((rc @ Pm) / len(r) >= obs - 1e-12)); done += k
    return obs, (1 + cnt) / (1 + R)

RPERM = 2000 if QUICK else 20000
Dm = Z[TT]
tests = {}
for m in CATS:
    s = wf[f'M1_{m}']; r = s['y'] - s['ycov']
    obs, p = perm_p(Dm, coef_store[f'M1_{m}'], r, RPERM); tests[f'T{m-2}_M1_{m}match'] = {'corr': obs, 'p_perm': p}
s = wf['M2_3']; r = s['y'] - s['ycov']
obs, p = perm_p(Dm, coef_store['M2'], r, RPERM); tests['T4_M2_on_3match'] = {'corr': obs, 'p_perm': p}
# extra: all 5040 permutations of 7 labels
pbT = pb[TT] - 1; sT = s_obs[TT]
obs_ex = corr(ex_pred, sT); cnt = 0; perms7 = list(itertools.permutations(range(7)))
for pm in perms7:
    pm = np.array(pm)
    if corr(ex_shat[np.arange(len(TT)), pm[pbT]], sT) >= obs_ex - 1e-12: cnt += 1
tests['T5_extra_number'] = {'corr': obs_ex, 'p_perm': cnt / len(perms7),
                            'R2_oos_vs_train_mean': float(1 - np.sum((sT - ex_pred) ** 2) / np.sum((sT - ex_base) ** 2))}
# Holm
order = sorted(tests, key=lambda k: tests[k]['p_perm']); K = len(order); prev = 0
for i, kname in enumerate(order):
    ph = min(1.0, max(prev, (K - i) * tests[kname]['p_perm'])); prev = ph
    tests[kname]['p_holm'] = ph; tests[kname]['reject_at_0.05'] = bool(ph < 0.05)
log('tests', {k: (round(v['corr'], 3), v['p_perm']) for k, v in tests.items()})

# secondary null: shuffle main sets across draws, refit M1 3-match walk-forward (tau2 reused)
R_SH = 30 if QUICK else 200
obs3 = tests['T1_M1_3match']['corr']; r3 = wf['M1_3']['y'] - wf['M1_3']['ycov']
sh_corrs = []
for rep in range(R_SH):
    Zs = Z[rng.permutation(n)]
    ps = []
    for j, t in enumerate(TT):
        idx = np.arange(t); Y, E = targets(ex_shat[j])
        f1 = fit_m1(idx, Y[3], E[3], tau_store[3][j], Zm=Zs)
        ps.append(Zs[t] @ f1['b'])
    sh_corrs.append(corr(np.array(ps), r3))
sh_corrs = np.array(sh_corrs)
shuffle_null = {'reps': R_SH, 'null_mean_corr': float(sh_corrs.mean()), 'null_sd': float(sh_corrs.std()),
                'p': float((1 + np.sum(sh_corrs >= obs3)) / (1 + R_SH))}
log('shuffle null', shuffle_null)

# realized-money check: tercile of predicted number part (M1 3-match) -> realized relative prize exp(-r)
def terciles(key):
    s = wf[key]; r = s['y'] - s['ycov']; p = s['p']; q = np.quantile(p, [1 / 3, 2 / 3])
    lo, hi = p <= q[0], p >= q[1]
    return {'mean_rel_prize_pred_unpopular_tercile': float(np.mean(np.exp(-r[lo]))),
            'mean_rel_prize_pred_popular_tercile': float(np.mean(np.exp(-r[hi]))),
            'ratio_unpopular_over_popular': float(np.mean(np.exp(-r[lo])) / np.mean(np.exp(-r[hi])))}
money_check = {k: terciles(k) for k in ('M1_3', 'M1_4', 'M1_5', 'M2_3', 'M2_5')}

# frozen old ranking (agent_extra C1_full, fit on draws through 2026-11-12) on the 8 newest draws
old = json.load(open(OLD)); bold = np.array([old['C1_full']['beta_centered_by_number'][str(i)] for i in range(1, 28)])
new8 = np.arange(n - 8, n); j8 = new8 - T_START
r8 = (wf['M1_3']['y'] - wf['M1_3']['ycov'])[j8]; pold = Z[new8] @ bold; pnew = wf['M1_3']['p'][j8]
frozen = {'draws': [d[t]['date'] for t in new8],
          'note': 'agent_extra C1_full was fit on draws through 2026-11-12: only 2026-11-16 and 2026-11-19 are truly unseen by it',
          'corr_old_8': corr(pold, r8), 'corr_newWF_8': corr(pnew, r8),
          'SSE_resid_only': float(np.sum(r8 ** 2)), 'SSE_minus_old': float(np.sum((r8 - pold) ** 2)),
          'SSE_minus_newWF': float(np.sum((r8 - pnew) ** 2)),
          'last2_unseen': [{'date': d[t]['date'], 'resid_r': float(r8[i]), 'pred_old': float(pold[i]), 'pred_newWF': float(pnew[i])}
                           for i, t in enumerate(new8) if t >= n - 2]}
log('frozen', round(frozen['corr_old_8'], 3), round(frozen['corr_newWF_8'], 3))

walk = {'scheme': f'strict: for t={T_START}..{n-1} fit on draws < t only; lambda by LOO inside training',
        'metrics': {k: wf_metrics(v) for k, v in wf.items()},
        'extra_number': {'corr': obs_ex, 'R2_oos_vs_train_mean': tests['T5_extra_number']['R2_oos_vs_train_mean']},
        'tests_holm': tests, 'shuffle_refit_null_M1_3match': shuffle_null, 'realized_prize_terciles': money_check,
        'frozen_old_ranking_8_newest': frozen,
        'lambda_chosen_last': {k: v[-1] for k, v in lam_store.items()},
        'lambda_chosen_counts': {k: {str(l): int(np.sum(np.array(v) == l)) for l in sorted(set(v))} for k, v in lam_store.items()}}

# ---------------------------------------------------------------- full-data fits
ALL = np.arange(n)
SH_ALL = extra_fit(ALL); YA, EA = targets(SH_ALL)
TAU = {m: est_tau2(ALL, YA[m], EA[m], Z) for m in CATS}
F1 = {m: fit_m1(ALL, YA[m], EA[m], TAU[m]) for m in CATS}
F2 = fit_m2(ALL, YA, EA, TAU)
LAM1 = {m: F1[m]['lam'] for m in CATS}; LAM2 = F2['lam']
CHOICE = {m: ('M1' if walk['metrics'][f'M1_{m}']['R2_incremental_oos'] >= walk['metrics'][f'M2_{m}']['R2_incremental_oos'] else 'M2')
          for m in CATS}
log('lambdas', LAM1, LAM2, 'tau', {m: round(np.sqrt(TAU[m]), 4) for m in CATS}, 'choice', CHOICE)

def tier_params(f1, f2, choice):
    """number coefficients (27) and D-side pair coefficient per tier m=3,4,5"""
    out = {}
    for m in CATS:
        if choice[m] == 'M1': out[m] = (f1[m]['b'] - f1[m]['b'].mean(), f1[m]['g'][1])
        else: out[m] = (CM[m] * (f2['a'] - f2['a'].mean()), f2['g'][m][1])
    return out

# slope check: log prize vs log winners
slope = {}
for k in ('3+0', '3+1', '4+0', '4+1', '5+0', '5+1'):
    rows = [(np.log(tier(x, k)[0]), np.log(tier(x, k)[1]), np.log(x['deposits']), prem[t], pre[t])
            for t, x in enumerate(d) if tier(x, k)[1] > 0 and tier(x, k)[0] > 0]
    A = np.array(rows); X = np.column_stack([np.ones(len(A)), A[:, 1], A[:, 2], A[:, 3], A[:, 4]])
    if np.ptp(A[:, 4]) == 0: X = X[:, :4]
    th, *_ = np.linalg.lstsq(X, A[:, 0], rcond=None)
    res = A[:, 0] - X @ th; cov = np.linalg.inv(X.T @ X) * res.var(ddof=X.shape[1])
    slope[k] = {'slope_log_prize_on_log_winners': float(th[1]), 'se': float(np.sqrt(cov[1, 1])),
                'coef_log_deposits': float(th[2]), 'n': int(len(A))}
log('slopes', {k: round(v['slope_log_prize_on_log_winners'], 3) for k, v in slope.items()})

# pool shares (normal months, post-era 2026) -> f_{m,e}
norm26 = [t for t, x in enumerate(d) if x['date'][:4] == '2026' and not prem[t]]
FPOOL = {}
for m in CATS:
    for e in (1, 0):
        k = f'{m}+{e}'
        FPOOL[k] = float(np.mean([tier(d[t], k)[0] * tier(d[t], k)[1] / d[t]['deposits'] for t in norm26]))
log('pool shares', {k: round(v, 5) for k, v in FPOOL.items()}, 'sum', round(sum(FPOOL.values()), 4))

# ---------------------------------------------------------------- all 296010 draws / fields
COMBS = np.array(list(itertools.combinations(range(27), 6)), dtype=np.int8)
NC = len(COMBS)
DALL = np.zeros((NC, 27), dtype=np.float32); DALL[np.arange(NC)[:, None], COMBS] = 1
DB = DALL.astype(bool)
NPAIR_ALL = (DB[:, :-1] & DB[:, 1:]).sum(1).astype(np.float32)
bad = np.zeros(NC, bool)
for a in range(27):
    for st in range(1, 14):
        if a + 2 * st < 27: bad |= DB[:, a] & DB[:, a + st] & DB[:, a + 2 * st]
VALID = ~bad                                     # no 3-term AP (includes: no run of 3)
log('valid fields', int(VALID.sum()))
MASK = (DB.astype(np.int64) * (1 << np.arange(27, dtype=np.int64))).sum(1)

def u_all(beta, gpair): return DALL @ beta.astype(np.float32) + np.float32(gpair) * NPAIR_ALL

def dp_sums(Smask, wv, theta):
    """for each field S (rows of bool Smask): sum over 6-sets D of prod_{i in D} wv_i * theta^{npairs(D)}, split by |S∩D|"""
    Nf = len(Smask); V = np.zeros((Nf, 7, 7, 2)); V[:, 0, 0, 0] = 1
    for j in range(27):
        inS = Smask[:, j]
        Vn = np.empty_like(V); Vn[..., 0] = V[..., 0] + V[..., 1]; Vn[..., 1] = 0
        add = wv[j] * (V[..., 0] + theta * V[..., 1])
        Vn[~inS, 1:, :, 1] += add[~inS, :-1, :]
        Vn[inS, 1:, 1:, 1] += add[inS, :-1, :-1]
        V = Vn
    return V[:, 6, :, 0] + V[:, 6, :, 1]

def A_fields(Smask, tp, chunk=20000):
    """A_m(S) = E[1/R_m(D) | |S∩D|=m] for m=3,4,5 (exact, incl. pair term); also random-field value"""
    out = np.zeros((len(Smask), 3)); rnd = {}
    for c, m in enumerate(CATS):
        beta, gp = tp[m]; u = u_all(beta, gp).astype(np.float64); ebar = np.mean(np.exp(u))
        rnd[m] = float(np.mean(np.exp(-u)) * ebar)
        for s0 in range(0, len(Smask), chunk):
            S = Smask[s0:s0 + chunk]
            out[s0:s0 + chunk, c] = dp_sums(S, np.exp(-beta), np.exp(-gp))[:, m] / NM[m] * ebar
    return out, rnd

def K_extra(sh):
    """per-tier multipliers K_m(x): sum over e of pool share * extra factor; sh normalised to sum 1"""
    sh = sh / sh.sum(); K = np.zeros((3, 7))
    for c, m in enumerate(CATS):
        for x in range(7):
            plus0 = np.mean([1 / (1 - sh[q]) for q in range(7) if q != x]) * 6 / 7
            K[c, x] = FPOOL[f'{m}+1'] / (7 * sh[x]) + FPOOL[f'{m}+0'] * plus0
    return K

TP = tier_params(F1, F2, CHOICE)
VIDX = np.where(VALID)[0]
AV, ARND = A_fields(DB[VIDX], TP)
# sanity: DP vs brute force for 2 fields
for vi in (0, 5000):
    S = DB[VIDX[vi]]; ov = DB[:, S].sum(1)
    for c, m in enumerate(CATS):
        beta, gp = TP[m]; u = u_all(beta, gp).astype(np.float64)
        bf = np.mean(np.exp(-u[ov == m])) * np.mean(np.exp(u))
        assert abs(bf / AV[vi, c] - 1) < 1e-4, (bf, AV[vi, c])
log('A computed for valid fields; DP check ok')
KX = K_extra(SH_ALL)
EVX = AV @ KX                                    # (Nvalid, 7): EV per 1 EUR, tiers 3-5
Kbar = KX.mean(1)
EV_RANDOM = float(sum(ARND[m] * Kbar[c] for c, m in enumerate(CATS)))
EV_POPAVG = float(sum(FPOOL.values()))

# ---------------------------------------------------------------- optimiser: 2 disjoint fields, extras distinct in {5,6,7}
XS = (4, 5, 6)                                   # 0-based extras 5,6,7
def best_pairs(EVX, top=3000, keep=50):
    cands = []
    for x1 in XS:
        for x2 in XS:
            if x2 <= x1: continue
            for (xa, xb) in ((x1, x2), (x2, x1)):
                ia = np.argsort(-EVX[:, xa])[:top]; ib = np.argsort(-EVX[:, xb])[:top]
                ma, mb = MASK[VIDX[ia]], MASK[VIDX[ib]]
                tot = EVX[ia, xa][:, None] + EVX[ib, xb][None, :]
                ok = (ma[:, None] & mb[None, :]) == 0
                tot = np.where(ok, tot, -np.inf)
                flat = np.argsort(-tot, axis=None)[:keep * 6]
                bound = EVX[ia[0], xa] + EVX[ib[-1], xb]
                for f in flat:
                    i, j = divmod(int(f), top)
                    if not np.isfinite(tot[i, j]): continue
                    cands.append((float(tot[i, j]), int(ia[i]), xa, int(ib[j]), xb, float(bound)))
    # dedupe by the unordered pair of main-number fields (keep the best extra assignment)
    seen = set(); out = []
    for c in sorted(cands, key=lambda z: -z[0]):
        key = frozenset([c[1], c[3]])
        if key in seen: continue
        seen.add(key); out.append(c)
    return out[:keep]

PAIRS = best_pairs(EVX)
def fld(vi): return [int(v) + 1 for v in COMBS[VIDX[vi]]]
log('best pair', fld(PAIRS[0][1]), PAIRS[0][2] + 1, fld(PAIRS[0][3]), PAIRS[0][4] + 1, round(PAIRS[0][0] / 2, 5))

# single best field (extra 5,6,7 best), most popular valid field (extra 3), random reference
best_single = int(np.argmax(EVX[:, list(XS)].max(1))); best_single_x = int(XS[np.argmax(EVX[best_single, list(XS)])])
most_pop = int(np.argmin(EVX[:, 2]))
# most popular by main numbers only (uniform extra)
EVmain_unif = AV @ Kbar
most_pop_main = int(np.argmin(EVmain_unif)); least_pop_main = int(np.argmax(EVmain_unif))

# ---------------------------------------------------------------- bootstrap over draws
NB = 200 if QUICK else 1000
NB_REGRET = 100 if QUICK else 300
TOPK = PAIRS[:50]
fixed_fields = sorted(set([p[1] for p in TOPK] + [p[3] for p in TOPK] + [best_single, most_pop, most_pop_main, least_pop_main]))
fixed_ov = {vi: DB[:, DB[VIDX[vi]]].sum(1).astype(np.int8) for vi in fixed_fields}
fixed_idx = {vi: {m: np.where(fixed_ov[vi] == m)[0] for m in CATS} for vi in fixed_fields}
CAND = np.unique(np.concatenate([np.argsort(-EVX[:, x])[:1500] for x in XS] + [np.argsort(-EVmain_unif)[:1500]]))
boot = {'a': [], 'b3': [], 'b4': [], 'b5': [], 'gpair': [], 'sh': [], 'ev_fixed': [], 'ev_random': [], 'A_rand': [],
        'regret': [], 'best_pair_ev': []}
log('bootstrap', NB, 'reps; regret reps', NB_REGRET, 'candidates', len(CAND))
for b in range(NB):
    ib = rng.integers(0, n, n)
    sh = extra_fit(ib); Y, E = targets(sh)
    f1 = {m: fit_m1(ib, Y[m], E[m], TAU[m], lam=LAM1[m]) for m in CATS}
    f2 = fit_m2(ib, Y, E, TAU, lam=LAM2)
    tp = tier_params(f1, f2, CHOICE)
    boot['a'].append(f2['a'] - f2['a'].mean())
    for m in CATS: boot[f'b{m}'].append(f1[m]['b'] - f1[m]['b'].mean())
    boot['gpair'].append([tp[m][1] for m in CATS]); boot['sh'].append(sh / sh.sum())
    K = K_extra(sh); Kb = K.mean(1)
    ue = {}; arnd = {}
    for c, m in enumerate(CATS):
        u = u_all(*tp[m]).astype(np.float64); eb = np.mean(np.exp(u)); ue[m] = (np.exp(-u), eb)
        arnd[m] = float(np.mean(np.exp(-u)) * eb)
    evf = {}
    for vi in fixed_fields:
        Am = np.array([np.mean(ue[m][0][fixed_idx[vi][m]]) * ue[m][1] for m in CATS])
        evf[vi] = Am @ K                                 # (7,)
    boot['ev_fixed'].append(evf); boot['ev_random'].append(float(sum(arnd[m] * Kb[c] for c, m in enumerate(CATS))))
    boot['A_rand'].append([arnd[m] for m in CATS])
    if b < NB_REGRET:
        Ac, _ = A_fields(DB[VIDX[CAND]], tp)
        evc = Ac @ K
        # best disjoint pair among candidates under this bootstrap model
        bestv = -np.inf
        for x1 in XS:
            for x2 in XS:
                if x1 == x2: continue
                ia = np.argsort(-evc[:, x1])[:400]; jb = np.argsort(-evc[:, x2])[:400]
                ma, mb = MASK[VIDX[CAND[ia]]], MASK[VIDX[CAND[jb]]]
                tot = evc[ia, x1][:, None] + evc[jb, x2][None, :]
                tot = np.where((ma[:, None] & mb[None, :]) == 0, tot, -np.inf)
                bestv = max(bestv, float(tot.max()))
        chosen = evf[PAIRS[0][1]][PAIRS[0][2]] + evf[PAIRS[0][3]][PAIRS[0][4]]
        boot['regret'].append(bestv - chosen); boot['best_pair_ev'].append(bestv)
    if b % 100 == 0: log('boot', b)
log('bootstrap done')

def ci(a, q=(2.5, 97.5)): a = np.asarray(a); return [float(np.percentile(a, q[0])), float(np.percentile(a, q[1]))]

# ---------------------------------------------------------------- ranking tables
A_SE = np.array(boot['a']).std(0); B3_SE = np.array(boot['b3']).std(0)
a_c = F2['a'] - F2['a'].mean()
b_c = {m: F1[m]['b'] - F1[m]['b'].mean() for m in CATS}
order_a = list(np.argsort(a_c) + 1); order_b3 = list(np.argsort(b_c[3]) + 1)
ranks_boot = np.argsort(np.argsort(np.array(boot['a']), 1), 1) + 1
ranking = []
for i in range(27):
    ranking.append({'number': i + 1, 'rank_least_popular_pooled': int(order_a.index(i + 1) + 1),
                    'a_pooled_player_logweight': float(a_c[i]), 'a_se': float(A_SE[i]),
                    'rel_pick_freq_approx': float(1 + (1 - 5 / 26) * a_c[i]),
                    'rank_boot_CI95': [int(np.percentile(ranks_boot[:, i], 2.5)), int(np.percentile(ranks_boot[:, i], 97.5))],
                    'beta3_Dside': float(b_c[3][i]), 'beta3_se': float(B3_SE[i]),
                    'beta4_Dside': float(b_c[4][i]), 'beta5_Dside': float(b_c[5][i])})
SHN = SH_ALL / SH_ALL.sum(); SH_SE = np.array(boot['sh']).std(0)
h1, h2 = np.arange(n // 2), np.arange(n // 2, n)
sh1, sh2 = extra_fit(h1), extra_fit(h2)
extra = {'share_by_extra_1to7': [float(v) for v in SHN], 'share_se': [float(v) for v in SH_SE],
         'rel_popularity_1to7': [float(v) for v in 7 * SHN], 'rel_pop_se': [float(v) for v in 7 * SH_SE],
         'least_popular_order': [int(i) + 1 for i in np.argsort(SHN)],
         'rel_pop_first_half': [float(v) for v in 7 * sh1 / sh1.sum()], 'rel_pop_second_half': [float(v) for v in 7 * sh2 / sh2.sum()],
         'sum_raw_shares': float(SH_ALL.sum())}
# shares by category (post era) as a consistency check
for m in CATS:
    post = np.where(pre == 0)[0]
    extra[f'rel_pop_from_{m}match_only'] = [float(7 * W1[m][post[pb[post] == x]].sum() / W[m][post[pb[post] == x]].sum()) for x in range(1, 8)]

cov_out = {}
for m in CATS:
    cov_out[f'M1_{m}match'] = {COVN[j]: float(F1[m]['g'][j]) for j in range(6)}
    cov_out[f'M2_{m}match'] = {COVN[j]: float(F2['g'][m][j]) for j in range(6)}
gp_boot = np.array(boot['gpair'])
pair_effect = {f'{m}match_Dside_coef_per_consecutive_pair': {'est': float(TP[m][1]), 'CI95': ci(gp_boot[:, c])} for c, m in enumerate(CATS)}

# ---------------------------------------------------------------- money
evf_b = boot['ev_fixed']; evr_b = np.array(boot['ev_random'])
def ev_pair_boot(pr): return np.array([e[pr[1]][pr[2]] + e[pr[3]][pr[4]] for e in evf_b]) / 2
def ev_field_boot(vi, x): return np.array([e[vi][x] for e in evf_b])
bp = PAIRS[0]
ev_bp = (EVX[bp[1], bp[2]] + EVX[bp[3], bp[4]]) / 2; ev_bp_b = ev_pair_boot(bp)
ev_mp = EVX[most_pop, 2]; ev_mp_b = ev_field_boot(most_pop, 2)
ev_bs = EVX[best_single, best_single_x]; ev_bs_b = ev_field_boot(best_single, best_single_x)
# main-only and extra-only decompositions (vs random field)
main_only_best = float(np.mean([AV[bp[1]] @ Kbar, AV[bp[3]] @ Kbar]) / EV_RANDOM - 1)
main_only_b = np.array([(np.mean([e[bp[1]].mean(), e[bp[3]].mean()])) for e in evf_b]) / evr_b - 1
main_only_mostpop = float(AV[most_pop_main] @ Kbar / EV_RANDOM - 1)
rnd_A = np.array([ARND[m] for m in CATS])
ex_fac = {str(x + 1): float(rnd_A @ KX[:, x] / EV_RANDOM - 1) for x in range(7)}
ex_fac_b = {str(x + 1): [] for x in range(7)}
# extra-only CI: recompute from boot shares with random-field A
for b in range(NB):
    K = K_extra(np.array(boot['sh'][b])); ar = np.array(boot['A_rand'][b]); base = ar @ K.mean(1)
    for x in range(7): ex_fac_b[str(x + 1)].append(float(ar @ K[:, x] / base - 1))

# top tiers (secondary): 6+1 480000 shared, 6+0 30000 shared, pooled a with c6=1, no pair term
Bnow = float(np.mean(Bt[-20:]))
def top_ev(Sbool, x, pv=1.0):
    ue = DALL @ a_c.astype(np.float32); ebar = float(np.mean(np.exp(ue.astype(np.float64))))
    R6 = float(np.exp(a_c[Sbool].sum()) / ebar) if Sbool is not None else 1.0
    def share(l): return (1 - np.exp(-l)) / l if l > 1e-12 else 1.0
    l1 = Bnow * P[6] * R6 * SHN[x]
    l0 = np.mean([Bnow * P[6] * R6 * (1 - SHN[q]) for q in range(7) if q != x])
    return (P[6] / 7 * 480000 * pv * share(l1) + P[6] * 6 / 7 * 30000 * share(l0)) / 1.5
top_avg = float(np.mean([top_ev(None, x) for x in range(7)]))
top_bp = float(np.mean([top_ev(DB[VIDX[bp[1]]], bp[2]), top_ev(DB[VIDX[bp[3]]], bp[4])]))

money = {
    'pool_shares_normal_month_2026': FPOOL, 'tiers3to5_return_population_average_per_EUR': EV_POPAVG,
    'model_used_per_tier': CHOICE,
    'A_random_field_per_tier': {str(m): ARND[m] for m in CATS},
    'EV_per_EUR_tiers3to5': {'population_average_field': EV_POPAVG, 'uniform_random_field': EV_RANDOM,
                             'best_pair_mean': float(ev_bp), 'best_single_field': float(ev_bs), 'most_popular_valid_field_extra3': float(ev_mp)},
    'gain_best_pair_vs_random_pct': {'est': 100 * float(ev_bp / EV_RANDOM - 1), 'CI95': ci(100 * (ev_bp_b / evr_b - 1))},
    'gain_best_pair_vs_population_avg_pct': {'est': 100 * float(ev_bp / EV_POPAVG - 1), 'CI95': ci(100 * (ev_bp_b / EV_POPAVG - 1))},
    'gain_best_pair_vs_most_popular_pct': {'est': 100 * float(ev_bp / ev_mp - 1), 'CI95': ci(100 * (ev_bp_b / ev_mp_b - 1))},
    'gain_best_single_vs_random_pct': {'est': 100 * float(ev_bs / EV_RANDOM - 1), 'CI95': ci(100 * (ev_bs_b / evr_b - 1))},
    'main_numbers_only_best_pair_vs_random_pct': {'est': 100 * main_only_best, 'CI95': ci(100 * main_only_b)},
    'main_numbers_only_most_popular_vs_random_pct': 100 * main_only_mostpop,
    'extra_number_only_vs_random_pct': {x: {'est': 100 * ex_fac[x], 'CI95': ci(100 * np.array(ex_fac_b[x]))} for x in ex_fac},
    'per_tier_prize_factor_best_pair_vs_random': {str(m): float(np.mean([AV[bp[1], c], AV[bp[3], c]]) / ARND[m]) for c, m in enumerate(CATS)},
    'per_tier_prize_factor_best_pair_vs_population_avg': {str(m): float(np.mean([AV[bp[1], c], AV[bp[3], c]])) for c, m in enumerate(CATS)},
    'per_tier_prize_factor_most_popular_vs_population_avg': {str(m): float(AV[most_pop, c]) for c, m in enumerate(CATS)},
    'top_tiers_secondary': {'bets_assumed': Bnow, 'EV_per_EUR_avg_field': top_avg, 'EV_per_EUR_best_pair': top_bp,
                            'note': '6+1 480000 (pv=1) and 6+0 30000 shared Poisson co-winners; pooled a, no pair term; extrapolated'},
    'return_per_EUR_normal_month': {'random_field': EV_RANDOM + top_avg, 'population_average': EV_POPAVG + top_avg,
                                    'best_pair': float(ev_bp + top_bp),
                                    'best_pair_CI95_tiers3to5_part': ci(ev_bp_b + top_bp)},
    'return_per_EUR_premium_month_tiers3to5_doubled': {'random_field': 2 * EV_RANDOM + top_avg, 'best_pair': float(2 * ev_bp + top_bp)},
    'slope_check': slope,
}

# selection-honesty check: choose on one half, evaluate on the other
def fitall(ii, ret_f2=False):
    sh = extra_fit(ii); Y, E = targets(sh); tau = {m: est_tau2(ii, Y[m], E[m], Z) for m in CATS}
    f1 = {m: fit_m1(ii, Y[m], E[m], tau[m]) for m in CATS}; f2 = fit_m2(ii, Y, E, tau)
    return (tier_params(f1, f2, CHOICE), sh, f2) if ret_f2 else (tier_params(f1, f2, CHOICE), sh)

def half_eval(fit_idx, eval_idx):
    def evr(rnd, K): return sum(rnd[m] * K.mean(1)[c] for c, m in enumerate(CATS))
    tpf, shf = fitall(fit_idx); Af, rndf = A_fields(DB[VIDX], tpf); Kf = K_extra(shf); evf = Af @ Kf
    i = int(np.argmax(evf[:, list(XS)].max(1))); x = int(XS[np.argmax(evf[i, list(XS)])])
    tpe, she = fitall(eval_idx); Ae, rnde = A_fields(DB[VIDX[[i]]], tpe); Ke = K_extra(she)
    return {'field_chosen_on_fit_half': fld(i), 'extra': x + 1,
            'gain_vs_random_on_fit_half_pct': float(100 * (evf[i, x] / evr(rndf, Kf) - 1)),
            'gain_vs_random_on_eval_half_pct': float(100 * ((Ae @ Ke)[0, x] / evr(rnde, Ke) - 1)),
            'main_only_gain_on_eval_half_pct': float(100 * ((Ae @ Ke.mean(1))[0] / evr(rnde, Ke) - 1))}
split_half = {'first_to_second': half_eval(h1, h2), 'second_to_first': half_eval(h2, h1)}
log('split-half', split_half)

# ---------------------------------------------------------------- top pairs output
def extras_alt(pr):
    """EV of the same two fields under every allowed extra assignment"""
    return {f'{xa+1}/{xb+1}': float((EVX[pr[1], xa] + EVX[pr[3], xb]) / 2) for xa in XS for xb in XS if xa != xb}
top_pairs = []; within = 0
for k, pr in enumerate(TOPK):
    evb = ev_pair_boot(pr); diff_b = ev_bp_b - evb
    p_better = float(np.mean(diff_b > 0)) if k else 0.0
    if k and p_better < 0.95: within += 1
    if k < 5:
        top_pairs.append({'rank': k + 1, 'field1': fld(pr[1]), 'extra1': pr[2] + 1, 'field2': fld(pr[3]), 'extra2': pr[4] + 1,
                          'EV_per_EUR_tiers3to5': pr[0] / 2, 'factor_vs_population_avg': pr[0] / 2 / EV_POPAVG,
                          'factor_vs_random_field': pr[0] / 2 / EV_RANDOM,
                          'boot_CI95_factor_vs_random': ci(evb / evr_b),
                          'consecutive_pairs': [npairs_of(fld(pr[1])), npairs_of(fld(pr[3]))],
                          'diff_vs_rank1_pct_of_avg_EV': 100 * (PAIRS[0][0] - pr[0]) / 2 / EV_POPAVG,
                          'boot_sd_of_diff_vs_rank1_pct': float(100 * np.std(diff_b) / EV_POPAVG),
                          'boot_P_rank1_better': p_better, 'EV_other_extra_assignments': extras_alt(pr)})
rank50 = TOPK[-1]
reg = np.array(boot['regret']) / 2
optimiser = {'valid_fields_no_3AP_no_3run': int(VALID.sum()), 'top5_pairs': top_pairs,
             'distinct_pairs_not_distinguishable_from_best_among_top49': within,
             'factor_vs_random_rank50_pair': rank50[0] / 2 / EV_RANDOM,
             'regret_of_chosen_pair_across_bootstrap_refits_pct_of_avg': {'mean': float(100 * reg.mean() / EV_POPAVG),
                                                                          'p90': float(100 * np.percentile(reg, 90) / EV_POPAVG)},
             'best_single_field': {'field': fld(best_single), 'extra': best_single_x + 1},
             'most_popular_valid_field': {'field': fld(most_pop), 'extra': 3},
             'most_popular_by_main_only': fld(most_pop_main), 'least_popular_by_main_only': fld(least_pop_main),
             'bound_check_note': 'search over top-3000 fields per extra; best pair sum exceeds EV(top1)+EV(rank3000)'}
# bound check: any pair using a field outside the top-3000 list of its extra is <= EV_a[0] + EV_b[2999]
bnd = []
for xa in XS:
    for xb in XS:
        if xa == xb: continue
        sa, sb = np.sort(EVX[:, xa])[::-1], np.sort(EVX[:, xb])[::-1]
        bnd.append(max(sa[0] + sb[2999], sa[2999] + sb[0]))
optimiser['bound_check_passed'] = bool(PAIRS[0][0] >= max(bnd) - 1e-12)
# ---------------------------------------------------------------- exploratory robustness (NOT pre-registered)
explore = {}
XC_LIN = XC
XC = np.column_stack([np.ones(n), npr == 1, npr == 2, npr >= 3, pre, thu, prem, logBc]).astype(float)
f2d = fit_m2(ALL, YA, EA, TAU, lam=LAM2)
explore['pair_effect_dummies_vs_linear_M2'] = {f'{m}match': {'1pair': float(f2d['g'][m][1]), '2pairs': float(f2d['g'][m][2]),
                                                            '3pairs': float(f2d['g'][m][3]),
                                                            'linear_model_1_2_3': [float(k * F2['g'][m][1]) for k in (1, 2, 3)]} for m in CATS}
explore['draws_by_npairs'] = {str(k): int(np.sum(npr == k)) for k in range(4)}
XC = XC_LIN
periods = [('2024', '2024-01-01', '2025-01-01'), ('2025H1', '2025-01-01', '2025-07-01'), ('2025H2', '2025-07-01', '2026-01-01'),
           ('2026H1', '2026-01-01', '2026-07-01'), ('2026H2', '2026-07-01', '2027-01-01')]
dates = np.array([x['date'] for x in d])
explore['extra_rel_pop_by_period'] = {}
for name, a_, b_ in periods:
    ii = np.where((dates >= a_) & (dates < b_))[0]; sh = extra_fit(ii)
    explore['extra_rel_pop_by_period'][name] = {'n': int(len(ii)), 'rel_pop_1to7': [round(float(v), 3) for v in 7 * sh / sh.sum()]}
pex = np.polyfit(ex_pred, sT, 1)
explore['extra_walkforward_calibration_slope'] = float(pex[0])
tp1, sh1_, f2h1 = fitall(h1, True); tp2, sh2_, f2h2 = fitall(h2, True)
explore['pooled_a_corr_first_vs_second_half'] = corr(f2h1['a'], f2h2['a'])
explore['pooled_a_sd_first_second'] = [float(np.std(f2h1['a'])), float(np.std(f2h2['a']))]

def gain_pair(tp, sh, pr):
    Ap, rnd = A_fields(DB[VIDX[[pr[1], pr[3]]]], tp); K = K_extra(sh); Kb = K.mean(1)
    evr = sum(rnd[m] * Kb[c] for c, m in enumerate(CATS))
    ev = (Ap[0] @ K[:, pr[2]] + Ap[1] @ K[:, pr[4]]) / 2; mn = (Ap[0] @ Kb + Ap[1] @ Kb) / 2
    return {'gain_vs_random_pct': float(100 * (ev / evr - 1)), 'main_only_pct': float(100 * (mn / evr - 1)),
            'tier_factors_vs_random': {str(m): float(Ap[:, c].mean() / rnd[m]) for c, m in enumerate(CATS)}}
tp_nopair = {m: (TP[m][0], 0.0) for m in CATS}
explore['recommended_pair_sensitivity'] = {
    'full_data_model': gain_pair(TP, SH_ALL, bp),
    'no_pair_term': gain_pair(tp_nopair, SH_ALL, bp),
    'model_fit_on_recent_half_only(85..169)': gain_pair(tp2, sh2_, bp),
    'model_fit_on_last_60_draws': gain_pair(*fitall(np.arange(n - 60, n)), bp),
    'full_main_recent_extra': gain_pair(TP, sh2_, bp)}
log('explore', json.dumps(explore['recommended_pair_sensitivity'])[:600])

g_recent = explore['recommended_pair_sensitivity']['full_main_recent_extra']['gain_vs_random_pct']
headline = {
    'least_popular_order_pooled': [int(v) for v in order_a],
    'extra_rel_popularity_full': [round(float(v), 3) for v in 7 * SHN],
    'extra_rel_popularity_2026H2': explore['extra_rel_pop_by_period']['2026H2']['rel_pop_1to7'],
    'consecutive_pairs': 'players avoid them: draws with a consecutive pair have fewer co-winners (3/4/5-match: '
                         + ', '.join(f"{100*(np.exp(TP[m][1])-1):.1f}%" for m in CATS) + ' per pair) -> pairs in a field are GOOD',
    'walk_forward_corr': {k: round(walk['metrics'][k]['corr_numberpart_vs_resid'], 3) for k in ('M2_3', 'M2_4', 'M2_5', 'M1_3')},
    'walk_forward_R2_incremental': {k: round(walk['metrics'][k]['R2_incremental_oos'], 3) for k in ('M2_3', 'M2_4', 'M2_5', 'M1_3')},
    'extra_walk_forward_corr': round(obs_ex, 3),
    'gain_tiers3to5_vs_random_pct_prereg': round(money['gain_best_pair_vs_random_pct']['est'], 2),
    'gain_CI95_bootstrap': [round(v, 2) for v in money['gain_best_pair_vs_random_pct']['CI95']],
    'gain_tiers3to5_vs_random_pct_with_recent_extra_popularity': round(g_recent, 2),
    'gain_main_numbers_only_pct': round(money['main_numbers_only_best_pair_vs_random_pct']['est'], 2),
    'gain_main_only_without_pair_term_pct': round(explore['recommended_pair_sensitivity']['no_pair_term']['main_only_pct'], 2),
    'return_per_EUR_random_field': round(EV_RANDOM + top_avg, 4),
    'return_per_EUR_recommended_prereg': round(float(ev_bp + top_bp), 4),
    'return_per_EUR_recommended_recent_extra': round(float(EV_RANDOM * (1 + g_recent / 100) + top_bp), 4),
    'recommended': {'field1': fld(bp[1]), 'extra1': bp[2] + 1, 'field2': fld(bp[3]), 'extra2': bp[4] + 1,
                    'note': 'any two different extras from 5/6/7 are equivalent within noise; ~20 other disjoint pairs are statistically indistinguishable'}}
log('headline', json.dumps(headline))
res = {'title': 'Extra výplata player popularity update (run_2311, subagent 4)', 'headline': headline, 'data_sha256': SHA, 'n_draws': n,
       'dates': [d[0]['date'], d[-1]['date']], 'prereg': 'lab/run_2311/popularity_prereg.md',
       'models': {'M1': 'per-category weighted ridge of log(winners/expected) on drawn-number indicators + covariates',
                  'M2': 'pooled player log-weights a_i, number part c_m*sum a_i, c3=.357 c4=.571 c5=.786'},
       'lambda_full': {'M1': {str(m): LAM1[m] for m in CATS}, 'M2': LAM2}, 'tau_full': {str(m): float(np.sqrt(TAU[m])) for m in CATS},
       'ranking_least_popular_pooled': [int(v) for v in order_a], 'ranking_least_popular_3match_M1': [int(v) for v in order_b3],
       'ranking': ranking, 'extra': extra, 'covariates_full_fit': cov_out, 'pair_effect': pair_effect,
       'walk_forward': walk, 'money': money, 'exploratory_not_preregistered': explore, 'split_half_selection_check': split_half, 'optimiser': optimiser,
       'corr_new_pooled_a_vs_old_beta3': corr(a_c, bold), 'corr_new_beta3_vs_old_beta3': corr(b_c[3], bold),
       'runtime_s': time.time() - T0, 'quick_mode': QUICK}
json.dump(res, open(OUT, 'w'), indent=1, ensure_ascii=False)
log('wrote', OUT)
