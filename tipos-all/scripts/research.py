"""Research step: (1) can a learned model predict draws? (2) which numbers are popular with players?
Usage: python3 -I research.py <data_dir> <extra_draws.json> <out.json>
"""
import json, sys, math, os
import numpy as np

DD, EVD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
C = math.comb
rng = np.random.default_rng(11)

def eur(s):
    s = str(s or '').replace('€', '').replace('\xa0', '').replace(' ', '').replace(',', '.')
    try: return float(s)
    except ValueError: return 0.0

# ------------------------------------------------------------------ data
L = [r for r in json.load(open(os.path.join(DD, 'l535.json'))) if r['raw'] and len(r['raw'].get('Zrebovanie', [])) == 5]
l_draws = [sorted(int(x) for x in r['raw']['Zrebovanie']) for r in L]
l_dep = np.array([eur(r['raw']['SumOfDeposits']) for r in L])
l_t = []
for r in L:
    t = {x['PocetUhadnutych'].strip(): int(x['PocetVyhier'] or 0) for x in r['raw']['TabulkaVyhier']['Loteria']}
    l_t.append(t)
E = json.load(open(EVD))
e_draws = [d['main'] for d in E]; e_pb = [d['pb'] for d in E]
e_dep = np.array([d['deposits'] for d in E])

# ------------------------------------------------------------------ (1) learned model, walk-forward
def features(M, t, n):
    """per-number features using draws < t"""
    T0 = t
    f = lambda w: M[max(0, T0 - w):T0].mean(0) if T0 > 0 else np.zeros(n)
    last_seen = np.full(n, T0 + 1.0)
    for j in range(n):
        idx = np.nonzero(M[:T0, j])[0]
        if len(idx): last_seen[j] = T0 - idx[-1]
    last = M[T0 - 1]; last2 = M[T0 - 2] if T0 >= 2 else np.zeros(n)
    co = (M[:T0].T @ M[:T0]).astype(float); np.fill_diagonal(co, 0)
    aff = co[last == 1].sum(0) / max(1, co.sum() / n)
    return np.column_stack([f(T0), f(52), f(20), f(10), np.log1p(last_seen), last, last2, aff])

def fit_logreg(X, y, lam=1.0, iters=25):
    mu = X.mean(0); sd = X.std(0) + 1e-9; Z = np.column_stack([np.ones(len(X)), (X - mu) / sd])
    w = np.zeros(Z.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-Z @ w)); g = Z.T @ (p - y) + lam * np.r_[0, w[1:]]
        H = (Z * (p * (1 - p))[:, None]).T @ Z + lam * np.diag(np.r_[0, np.ones(len(w) - 1)])
        w -= np.linalg.solve(H, g)
    return w, mu, sd

def ml_test(draws, n, k, start, step=10):
    T = len(draws); M = np.zeros((T, n), int)
    for i, d in enumerate(draws): M[i, np.array(d) - 1] = 1
    F = [None] * T
    for t in range(2, T): F[t] = features(M, t, n)
    hits = []; ll_model = 0.0; ll_base = 0.0; base = k / n
    w = None
    for t in range(start, T):
        if w is None or (t - start) % step == 0:
            X = np.vstack([F[s] for s in range(20, t)]); y = np.concatenate([M[s] for s in range(20, t)])
            w, mu, sd = fit_logreg(X, y)
        Z = np.column_stack([np.ones(n), (F[t] - mu) / sd]); p = 1 / (1 + np.exp(-Z @ w))
        p = np.clip(p, 1e-6, 1 - 1e-6)
        pick = np.argsort(-p)[:k]; hits.append(M[t, pick].sum())
        yv = M[t]; ll_model += (yv * np.log(p) + (1 - yv) * np.log(1 - p)).sum(); ll_base += (yv * math.log(base) + (1 - yv) * math.log(1 - base)).sum()
    hits = np.array(hits); nd = len(hits)
    var1 = k * (k / n) * ((n - k) / n) * ((n - k) / (n - 1))
    z = (hits.sum() - nd * k * k / n) / math.sqrt(nd * var1)
    third = hits[2 * nd // 3:]; zl = (third.sum() - len(third) * k * k / n) / math.sqrt(len(third) * var1)
    return {'draws_tested': nd, 'mean_hits': float(hits.mean()), 'random_mean': k * k / n, 'z': float(z), 'z_last_third': float(zl),
            'loglik_gain_per_draw': float((ll_model - ll_base) / nd), 'coef': w.tolist()}

ml = {'extra_vyplata': ml_test(e_draws, 27, 6, 60, 5), 'loto535': ml_test(l_draws, 35, 5, 200, 20)}

# ------------------------------------------------------------------ (2) popularity among players
def popularity(draws, n, k, y, train_frac=0.7, lam=3.0, extra_feats=None):
    T = len(draws); X = np.zeros((T, n))
    for i, d in enumerate(draws): X[i, np.array(d) - 1] = 1
    if extra_feats is not None: X = np.column_stack([X, extra_feats])
    Xc = np.column_stack([np.ones(T), X]); P = Xc.shape[1]
    reg = lam * np.diag([0] + [1] * (P - 1))
    cut = int(T * train_frac)
    b_tr = np.linalg.solve(Xc[:cut].T @ Xc[:cut] + reg, Xc[:cut].T @ y[:cut])
    pred = Xc[cut:] @ b_tr; ss = ((y[cut:] - y[cut:].mean()) ** 2).sum(); r2 = 1 - ((y[cut:] - pred) ** 2).sum() / ss
    # permutation check of out-of-sample R2
    r2p = []
    for _ in range(300):
        yp = rng.permutation(y)
        b = np.linalg.solve(Xc[:cut].T @ Xc[:cut] + reg, Xc[:cut].T @ yp[:cut]); pr = Xc[cut:] @ b
        r2p.append(1 - ((yp[cut:] - pr) ** 2).sum() / ((yp[cut:] - yp[cut:].mean()) ** 2).sum())
    # stability: halves
    h = T // 2
    b1 = np.linalg.solve(Xc[:h].T @ Xc[:h] + reg, Xc[:h].T @ y[:h])[1:n + 1]
    b2 = np.linalg.solve(Xc[h:].T @ Xc[h:] + reg, Xc[h:].T @ y[h:])[1:n + 1]
    b_all = np.linalg.solve(Xc.T @ Xc + reg, Xc.T @ y)
    beta = b_all[1:n + 1]; beta = beta - beta.mean()
    return {'r2_oos': float(r2), 'p_r2': float(np.mean(np.array(r2p) >= r2)), 'half_corr': float(np.corrcoef(b1, b2)[0, 1]),
            'beta': beta.tolist(), 'extra_coef': b_all[n + 1:].tolist(), 'resid_sd': float(np.std(y - Xc @ b_all))}

# Loto 5 z 35: response = log(3-match winners / expected under random picks)
p3 = C(5, 3) * C(30, 2) / C(35, 5)
y_l = np.log((np.array([t.get('3', 0) for t in l_t]) + 1) / (l_dep / 0.60 * p3))
cons_l = np.array([sum(1 for a, b in zip(d, d[1:]) if b == a + 1) for d in l_draws])
rep_l = np.array([0] + [len(set(l_draws[i]) & set(l_draws[i - 1])) for i in range(1, len(l_draws))])
pop_l = popularity(l_draws, 35, 5, y_l, extra_feats=np.column_stack([cons_l, rep_l]))

# Extra výplata: 3-match winners (3+0 and 3+1)
p3e = C(6, 3) * C(21, 3) / C(27, 6)
w3 = np.array([d['tiers'].get('3+0', (0, 0))[1] + d['tiers'].get('3+1', (0, 0))[1] for d in E])
y_e = np.log((w3 + 1) / (e_dep / 1.5 * p3e))
cons_e = np.array([sum(1 for a, b in zip(d, d[1:]) if b == a + 1) for d in e_draws])
rep_e = np.array([0] + [len(set(e_draws[i]) & set(e_draws[i - 1])) for i in range(1, len(e_draws))])
pop_e = popularity(e_draws, 27, 6, y_e, lam=2.0, extra_feats=np.column_stack([cons_e, rep_e]))

# Extra výplata powerball popularity: share of "+1" winners among 3/4/5-match winners vs 1/7
pbpop = {v: [] for v in range(1, 8)}
for d in E:
    t = d['tiers']
    if '3+1' not in t: continue
    plus = sum(t.get(f'{m}+1', (0, 0))[1] for m in (3, 4, 5)); tot = plus + sum(t.get(f'{m}+0', (0, 0))[1] for m in (3, 4, 5))
    if tot > 0: pbpop[d['pb']].append((plus / tot) / (1 / 7))
pb_pop = {str(v): {'ratio': float(np.mean(x)) if x else None, 'n': len(x), 'se': float(np.std(x) / math.sqrt(len(x))) if len(x) > 1 else None} for v, x in pbpop.items()}

json.dump({'ml': ml, 'pop_loto535': pop_l, 'pop_extra': pop_e, 'pb_pop_extra': pb_pop}, open(OUT, 'w'), indent=1)
print(json.dumps({'ml': {k: {kk: vv for kk, vv in v.items() if kk != 'coef'} for k, v in ml.items()},
                  'pop_loto535': {k: (v if not isinstance(v, list) else [round(x, 3) for x in v]) for k, v in pop_l.items()},
                  'pop_extra': {k: (v if not isinstance(v, list) else [round(x, 3) for x in v]) for k, v in pop_e.items()},
                  'pb_pop_extra': pb_pop}, indent=1))
