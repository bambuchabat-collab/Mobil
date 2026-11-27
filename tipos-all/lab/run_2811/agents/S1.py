"""S1 — PHYSICS (nonlinear dynamics / chaos): Takens delay embedding + empirical dynamic modelling.
Pre-registration: agents/S1_prereg.md (written before any evaluation). Run: python3 -I S1.py
F1 (EM, primary): simplex projection on delay-embedded occupation states, E in {1,2,3} chosen walk-forward by
    leave-one-out skill with a Theiler window.
F2 (EM): S-map (locally weighted linear map), E = 1, theta = 2, ridge lambda = 1.
F3 (VAN): Poincare-section Takens embedding of the drawing order (11-dim), Lorenz analogues, k = 12, simplex weights.
"""
import sys, json, os, time
import numpy as np
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2811')
from harness2 import evaluate, load, params

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'S1.json')
BIG = 100000  # composite key: squared distance * BIG + library index -> stable tie-break by smaller index


def indicators(past, N):
    X = np.zeros((len(past), N))
    for s, r in enumerate(past):
        X[s, np.array(r['main']) - 1] = 1.0
    return X


def ticket(score, N, T, fid, t):
    perm = np.random.default_rng([2811, fid, t]).permutation(N)
    u = np.empty(N, int); u[perm] = np.arange(N)  # u[i] = rank of number i+1 in the permutation
    order = np.lexsort((u, -np.asarray(score, float)))  # primary: score desc, secondary: u asc
    return sorted(int(i) + 1 for i in order[:T])


def simplex_weights(d):
    """d: (..., k) sorted ascending distances. w = exp(-d/d1); d1 = 0 -> weight only exact matches."""
    d1 = d[..., :1]
    with np.errstate(divide='ignore', invalid='ignore'):
        w = np.where(d1 > 0, np.exp(-d / np.where(d1 > 0, d1, 1.0)), (d == 0).astype(float))
    return w


def delay_sqdist(H1, E):
    """Summed squared distances of E-lag delay vectors; entries with s < E-1 or s' < E-1 are set to -1 (invalid)."""
    t = H1.shape[0]
    H = np.full((t, t), -1, dtype=np.int64)
    acc = np.zeros((t - E + 1, t - E + 1), dtype=np.int64)
    for l in range(E):
        acc += H1[E - 1 - l: t - l, E - 1 - l: t - l]
    H[E - 1:, E - 1:] = acc
    return H


def knn_forecast(Hrows, lib, X, k_cap, valid_mask=None):
    """Hrows: (m, len(lib)) int squared distances from m queries to library points lib (indices, ascending);
    valid_mask: (m, len(lib)) bool. Returns (m, N) simplex forecasts of x_{s+1}."""
    m, L = Hrows.shape
    if valid_mask is None:
        valid_mask = np.ones((m, L), bool)
    avail = valid_mask.sum(1)
    kk = np.minimum(k_cap, avail)
    kmax = int(kk.max())
    key = np.where(valid_mask, Hrows * BIG + np.arange(L)[None, :], np.iinfo(np.int64).max)
    if kmax < L:
        part = np.partition(key, kmax - 1, axis=1)[:, :kmax]
    else:
        part = key
    part = np.sort(part, axis=1)[:, :kmax]
    pos = (part % BIG).astype(int)
    pos = np.minimum(pos, L - 1)
    d = np.sqrt((part // BIG).astype(float))
    use = np.arange(kmax)[None, :] < kk[:, None]
    d = np.where(use, d, np.inf)
    w = simplex_weights(d)
    w = np.where(use, w, 0.0)
    succ = X[np.asarray(lib)[pos] + 1]  # (m, kmax, N)
    return (w[:, :, None] * succ).sum(1) / w.sum(1)[:, None]


E_LOG = {}


def F1(past, date, game='EM', fid=1):
    d, N, K, T = CACHE_P[game]
    t = len(past)
    X = indicators(past, N)
    G = (X @ X.T).astype(np.int64)
    H1 = 2 * K - 2 * G
    S = np.arange(2, t - 1)  # LOO targets s, successor s+1 <= t-1
    best, bestE, fc = -np.inf, 1, None
    for E in (1, 2, 3):
        H = delay_sqdist(H1, E)
        lib = np.arange(E - 1, t - 1)
        kcap = E * N + 1
        # leave-one-out skill with Theiler window |s'-s| <= E
        rows = H[S][:, lib]
        valid = np.abs(lib[None, :] - S[:, None]) > E
        ok = valid.sum(1) > 0
        rho = -np.inf
        if ok.sum() >= 2:
            xh = knn_forecast(rows[ok], lib, X, kcap, valid[ok])
            obs = X[S[ok] + 1]
            a, b = xh.ravel(), obs.ravel()
            if a.std() > 0 and b.std() > 0:
                rho = float(np.corrcoef(a, b)[0, 1])
        if rho > best:
            best, bestE = rho, E
    E = bestE
    H = delay_sqdist(H1, E)
    lib = np.arange(E - 1, t - 1)
    fc = knn_forecast(H[t - 1][None, lib], lib, X, E * N + 1)[0]
    E_LOG[(game, t)] = (E, best)
    return ticket(fc, N, T, fid, t)


def F2(past, date, game='EM', fid=2, theta=2.0, lam=1.0):
    d, N, K, T = CACHE_P[game]
    t = len(past)
    X = indicators(past, N)
    P, Y, q = X[:-1], X[1:], X[-1]
    n = len(P)
    ds = np.sqrt(((P - q) ** 2).sum(1))
    dbar = ds.mean()
    w = np.exp(-theta * ds / dbar) if dbar > 0 else np.ones(n)
    w = w * n / w.sum()
    A = np.hstack([np.ones((n, 1)), P])
    R = np.eye(N + 1); R[0, 0] = 0.0
    AW = A * w[:, None]
    B = np.linalg.solve(A.T @ AW + lam * R, AW.T @ Y)
    y = np.concatenate([[1.0], q]) @ B
    return ticket(y, N, T, fid, t)


def F3(past, date, game='VAN', fid=3, k=12):
    d, N, K, T = CACHE_P[game]
    t = len(past)
    X = indicators(past, N)
    Z = np.array([r['order'] for r in past], dtype=np.int64)
    lib = np.arange(0, t - 1)
    H = ((Z[lib] - Z[t - 1]) ** 2).sum(1)[None, :]
    fc_w = knn_forecast(H, lib, X, k)[0]  # weighted mean of successors = score / sum(w): same ranking
    return ticket(fc_w, N, T, fid, t)


CACHE_P = {g: params(g) for g in ('EM', 'VAN')}

DEFS = {
    'F1': ("Simplex projection (Sugihara-May) on Takens delay vectors of the 33-dim occupation state, "
           "E in {1,2,3} lags chosen walk-forward by leave-one-out Pearson skill with Theiler window |s'-s|<=E; "
           "k=E*33+1 nearest (Euclidean), weights exp(-d/d1); ticket = top 7 forecast probabilities."),
    'F2': ("S-map (Sugihara 1994), E=1: weighted ridge regression x_{s+1} ~ [1, x_s], weights exp(-2 d/dbar) "
           "around the last draw, lambda=1 (intercept unpenalised); ticket = top 7 predicted values."),
    'F3': ("Poincare-section Takens embedding of the VAN drawing order: 11-dim order vector of each draw, "
           "k=12 nearest past analogues of the last draw (Euclidean on ball labels), weights exp(-d/d1); "
           "ticket = 11 numbers most frequent (weighted) in the analogues' next draws."),
}
TEXT = {
    'F1': "x̂_{t+1} = Σ_j w_j x_{s_j+1}/Σ_j w_j over the k=33E*+1 nearest delay vectors (x_s..x_{s-E*+1}) to (x_t..x_{t-E*+1}), w_j=exp(-d_j/d_1), E*=argmax LOO ρ_E; pick top 7",
    'F2': "ŷ = [1,x_t]·B, B = argmin Σ_s w_s||x_{s+1}-[1,x_s]B||² + ||B_{1:}||², w_s ∝ exp(-2||x_s-x_t||/mean||x_s-x_t||); pick top 7",
    'F3': "score_i = Σ_{j≤12} exp(-d_j/d_1)·1[i ∈ draw(s_j+1)], d_j = ||order_{s_j} - order_t||₂ (12 nearest); pick top 11",
}


def main():
    res = []
    for name, f, game in (('F1', F1, 'EM'), ('F2', F2, 'EM'), ('F3', F3, 'VAN')):
        t0 = time.time()
        r = evaluate(f, game, 'S1_' + name)
        r = {kk: (v.item() if hasattr(v, 'item') else v) for kk, v in r.items()}
        r['definition'] = DEFS[name]
        r['formula_text'] = TEXT[name]
        r['formula'] = name
        r['seconds'] = round(time.time() - t0, 1)
        print(name, game, r['n'], round(r['mean_hits'], 4), round(r['expected'], 4),
              'p_upper=%.4f p_lower=%.4f' % (r['p_upper'], r['p_lower']), r['hist'], r['seconds'], 's', flush=True)
        res.append(r)
    # descriptive: chosen embedding dimension E* for F1
    Es = [v[0] for k, v in sorted(E_LOG.items()) if k[0] == 'EM']
    res[0]['E_star_counts'] = {str(e): int(Es.count(e)) for e in (1, 2, 3)}
    # predictions for 2026-11-28 on the full history
    em, van = load('EM'), load('VAN')
    pred = {'game': 'EM', 'numbers': F1(em, '2026-11-28'), 'formula': 'F1',
            'E_star': int(E_LOG[('EM', len(em))][0]), 'loo_rho': float(E_LOG[('EM', len(em))][1])}
    other = {'F2_EM': F2(em, '2026-11-28'), 'F3_VAN': F3(van, '2026-11-28')}
    out = {'id': 'S1', 'science': 'PHYSICS: nonlinear dynamics and chaos (Takens embedding, simplex projection, S-map)',
           'game': 'EM (F1, F2), VAN (F3)', 'formulas': res, 'prediction_28_11': pred,
           'other_predictions_28_11': other}
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(pred), other)


if __name__ == '__main__':
    main()
