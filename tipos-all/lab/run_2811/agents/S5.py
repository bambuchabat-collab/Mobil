"""S5 — machine learning / AI. Game: Euromilióny (EM), 7 of 33, ticket 7.
F1 Hedge over 26 experts, F2 delay-embedding kNN analogues, F3 permutation-symmetric numpy MLP (walk-forward).
Preregistration: agents/S5_prereg.md. Run: python3 -I S5.py
"""
import sys, json, math, datetime, time, functools
import numpy as np
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2811')
from harness2 import evaluate, load, params

GAME = 'EM'
_D, N, K, T = params(GAME)
PI = np.random.RandomState(2811).permutation(N).astype(float)   # tie-break permutation
EPS = 1e-9
TB = EPS * PI


def key(r):
    return (r['date'], tuple(r['main']))


def Xmat(past):
    X = np.zeros((len(past), N))
    for u, r in enumerate(past):
        X[u, np.array(r['main']) - 1] = 1.0
    return X


def top(score):
    s = np.asarray(score, float) + TB
    idx = np.argsort(-s, kind='stable')[:T]
    return [int(i) + 1 for i in idx]


@functools.lru_cache(maxsize=None)
def wd(date):
    return datetime.date.fromisoformat(date).weekday()


# ---------------------------------------------------------------- F1: Hedge over experts
def expert_scores(past, date):
    """26 score vectors (length N) computed only from past and the target date."""
    t = len(past)
    X = Xmat(past) if t else np.zeros((0, N))
    cnt = lambda W: X[max(0, t - W):].sum(0) if t else np.zeros(N)
    c_all = X.sum(0)
    c50 = cnt(50)
    last = X[t - 1] if t >= 1 else np.zeros(N)
    last2 = X[t - 2] if t >= 2 else np.zeros(N)
    # gap
    gap = np.full(N, float(t))
    for u in range(t - 1, -1, -1):
        m = (X[u] > 0) & (gap == t)
        gap[m] = t - 1 - u
        if not (gap == t).any():
            break
    nums = np.arange(1, N + 1)
    lastset = [j for j in range(1, N + 1) if last[j - 1] > 0]
    nb1 = np.array([sum(1 for j in lastset if abs(i - j) == 1) for i in nums], float)
    nb2 = np.array([sum(1 for j in lastset if abs(i - j) == 2) for i in nums], float)
    early = np.zeros(N); late = np.zeros(N)
    for r in past[max(0, t - 100):]:
        o = r.get('order') or []
        if len(o) != K:
            continue
        for p, x in enumerate(o):
            if p <= 2: early[x - 1] += 1
            if p >= 4: late[x - 1] += 1
    w0 = wd(date)
    same_wd = [u for u in range(t) if wd(past[u]['date']) == w0][-50:]
    wdc = X[same_wd].sum(0) if same_wd else np.zeros(N)
    mo = int(date[5:7])
    same_mo = [u for u in range(t) if int(past[u]['date'][5:7]) == mo]
    moc = X[same_mo].sum(0) if same_mo else np.zeros(N)
    mirror = last[::-1].copy()          # score_i = last[34-i]
    C = X.T @ X if t else np.zeros((N, N))
    np.fill_diagonal(C, 0)
    pairs = C @ last
    Fm = X[:-1].T @ X[1:] if t >= 2 else np.zeros((N, N))   # F[j,i]: j at u-1, i at u
    markov = last @ Fm
    def ema(h):
        if not t: return np.zeros(N)
        w = 0.5 ** ((t - 1 - np.arange(t)) / h)
        return w @ X
    rnd = np.random.RandomState(int(date.replace('-', ''))).permutation(N).astype(float)
    S = [cnt(5), cnt(10), cnt(20), cnt(50), cnt(100), c_all,
         -cnt(10), -cnt(50), -c_all,
         gap, gap * (c_all + 1) / (t + 1),
         last + 0.01 * c50, last2 + 0.01 * c50, -last + 0.01 * c50,
         nb1 + 0.01 * c50, nb2 + 0.01 * c50,
         early, late, wdc, moc,
         mirror + 0.01 * c50, pairs, markov, ema(10.0), ema(100.0), rnd]
    return S


EXPERT_NAMES = ['hot5', 'hot10', 'hot20', 'hot50', 'hot100', 'hot_all', 'cold10', 'cold50', 'cold_all',
                'overdue', 'rel_overdue', 'repeat1', 'repeat2', 'not_repeat', 'neigh1', 'neigh2',
                'early_order', 'late_order', 'weekday', 'month', 'mirror', 'pairs', 'markov',
                'ema10', 'ema100', 'random']
M = len(EXPERT_NAMES)
assert M == 26


class HedgeCache:
    def __init__(self):
        self.keys = []      # key of draw s for s processed
        self.loss = []      # loss vector (M,) for draw s, s = 1..; loss[0] placeholder zeros (s=0 not scored)
_HC = HedgeCache()


def _hedge_extend(past, cache):
    # verify prefix
    n = min(len(cache.keys), len(past))
    for s in range(n):
        if cache.keys[s] != key(past[s]):
            cache.keys, cache.loss = [], []
            break
    n = len(cache.keys)
    for s in range(n, len(past)):
        if s == 0:
            cache.loss.append(np.zeros(M))
        else:
            sc = expert_scores(past[:s], past[s]['date'])
            drawn = set(past[s]['main'])
            cache.loss.append(np.array([1.0 - len(set(top(x)) & drawn) / K for x in sc]))
        cache.keys.append(key(past[s]))


def hedge_weights(past, cache):
    _hedge_extend(past, cache)
    t = len(past)
    L = np.sum(cache.loss[1:t], axis=0) if t >= 2 else np.zeros(M)
    eta = math.sqrt(8 * math.log(M) / max(1, t - 1))
    w = np.exp(-eta * (L - L.min()))
    return w / w.sum(), L


def F1(past, date, cache=None):
    cache = _HC if cache is None else cache
    w, _ = hedge_weights(past, cache)
    S = np.zeros(N)
    for e, sc in enumerate(expert_scores(past, date)):
        for x in top(sc):
            S[x - 1] += w[e]
    return top(S)


# ---------------------------------------------------------------- F2: delay-embedding kNN analogues
def F2(past, date, m=3, k=30):
    t = len(past)
    X = Xmat(past)
    if t < m + 1:
        return top(X.sum(0) if t else np.zeros(N))
    z_t = np.concatenate([X[t - 1 - j] for j in range(m)])
    cands = np.arange(m, t)                          # states before draw s, label X[s]
    Z = np.concatenate([X[cands - 1 - j] for j in range(m)], axis=1)
    d = np.abs(Z - z_t).sum(1)
    order = np.lexsort((-cands, d))                  # by distance, then more recent first
    nb = cands[order[:min(k, len(cands))]]
    return top(X[nb].sum(0))


# ---------------------------------------------------------------- F3: permutation-symmetric MLP
NF = 17


def features(past):
    """Feature tensor Fe[s] (s = 0..t) = state before draw s, built from draws < s only. Shape (t+1, N, NF)."""
    t = len(past)
    X = Xmat(past)
    Fe = np.zeros((t + 1, N, NF))
    Xpad = np.vstack([np.zeros((10, N)), X])          # Xpad[k] = X[k-10]
    for j in range(10):                               # Fe[s,:,j] = X[s-1-j]
        Fe[:, :, j] = Xpad[9 - j: 9 - j + t + 1]
    cs = np.vstack([np.zeros((1, N)), np.cumsum(X, 0)])   # cs[s] = counts over draws < s
    s = np.arange(t + 1)
    for c, W in ((10, 30), (11, 100)):
        lo = np.maximum(0, s - W)
        Fe[:, :, c] = (cs - cs[lo]) / np.maximum(1, np.minimum(W, s))[:, None]
    Fe[:, :, 12] = cs / np.maximum(1, s)[:, None]
    idx = np.where(X > 0, np.arange(t)[:, None], -1)
    lastidx = np.maximum.accumulate(idx, axis=0) if t else np.zeros((0, N))
    ls = np.vstack([np.full((1, N), -1.0), lastidx])   # ls[s] = last index < s
    gap = np.where(ls >= 0, s[:, None] - 1 - ls, s[:, None])
    Fe[:, :, 13] = np.log1p(gap)
    prev = Fe[:, :, 0]
    nb = np.zeros_like(prev); nb[:, 1:] += prev[:, :-1]; nb[:, :-1] += prev[:, 1:]
    Fe[:, :, 14] = nb
    O = np.zeros((t + 1, N))
    for u, r in enumerate(past):
        o = r.get('order') or []
        if len(o) == K:
            for p, x in enumerate(o):
                O[u + 1, x - 1] = 1.0 - p / K
    Fe[:, :, 15] = O
    Fe[:, :, 16] = (np.arange(1, N + 1) - 17) / 16.0
    return Fe, X


def mlp_fit(Ftr, Ytr, Fva, Yva, seed, H=16, lr=0.005, l2=1e-4, max_ep=300, patience=20):
    rng = np.random.RandomState(seed)
    mu = Ftr.reshape(-1, NF).mean(0); sd = Ftr.reshape(-1, NF).std(0); sd[sd < 1e-8] = 1.0
    A, B = (Ftr - mu) / sd, (Fva - mu) / sd
    a1 = math.sqrt(6 / (NF + H)); a2 = math.sqrt(6 / (H + 1))
    P = {'W1': rng.uniform(-a1, a1, (NF, H)), 'b1': np.zeros(H), 'w2': rng.uniform(-a2, a2, H)}
    Mo = {k: np.zeros_like(v) for k, v in P.items()}; Vo = {k: np.zeros_like(v) for k, v in P.items()}

    def fwd(Z, P):
        Hh = np.tanh(Z @ P['W1'] + P['b1'])
        lg = Hh @ P['w2']
        lg = lg - lg.max(1, keepdims=True)
        p = np.exp(lg); p /= p.sum(1, keepdims=True)
        return Hh, p

    def loss(Z, Y, P):
        _, p = fwd(Z, P)
        return float(-(Y / K * np.log(p + 1e-12)).sum(1).mean())

    best = (loss(B, Yva, P), {k: v.copy() for k, v in P.items()}, 0); bad = 0
    n = len(A)
    for ep in range(1, max_ep + 1):
        Hh, p = fwd(A, P)
        dl = (p - Ytr / K) / n
        g = {'w2': np.einsum('ndh,nd->h', Hh, dl) + 2 * l2 * P['w2']}
        dpre = dl[..., None] * P['w2'] * (1 - Hh ** 2)
        g['W1'] = np.einsum('ndf,ndh->fh', A, dpre) + 2 * l2 * P['W1']
        g['b1'] = dpre.sum((0, 1))
        for k_ in P:
            Mo[k_] = 0.9 * Mo[k_] + 0.1 * g[k_]
            Vo[k_] = 0.999 * Vo[k_] + 0.001 * g[k_] ** 2
            mh = Mo[k_] / (1 - 0.9 ** ep); vh = Vo[k_] / (1 - 0.999 ** ep)
            P[k_] = P[k_] - lr * mh / (np.sqrt(vh) + 1e-8)
        v = loss(B, Yva, P)
        if v < best[0] - 1e-9:
            best = (v, {k: x.copy() for k, x in P.items()}, ep); bad = 0
        else:
            bad += 1
            if bad >= patience:
                break
    return {'P': best[1], 'mu': mu, 'sd': sd, 'best_ep': best[2], 'val': best[0]}


class MLPCache:
    def __init__(self):
        self.models = {}    # t_refit -> (prefix keys hash, model)
_MC = MLPCache()


def F3(past, date, cache=None, start=30, every=20):
    cache = _MC if cache is None else cache
    t = len(past)
    tr = start + every * ((t - start) // every) if t >= start else t
    Fe, X = features(past)
    pk = hash(tuple(key(r) for r in past[:tr]))
    ent = cache.models.get(tr)
    if ent is None or ent[0] != pk:
        s_idx = np.arange(10, tr)
        nv = max(4, int(round(0.2 * len(s_idx))))
        tr_i, va_i = s_idx[:-nv], s_idx[-nv:]
        model = mlp_fit(Fe[tr_i], X[tr_i], Fe[va_i], X[va_i], seed=2811 + tr)
        cache.models[tr] = (pk, model)
        ent = cache.models[tr]
    mdl = ent[1]
    Z = (Fe[t] - mdl['mu']) / mdl['sd']
    lg = np.tanh(Z @ mdl['P']['W1'] + mdl['P']['b1']) @ mdl['P']['w2']
    return top(lg - lg.min())


# ---------------------------------------------------------------- run
DEFS = {
    'F1': ('Hedge (exponential weights, eta_t=sqrt(8 ln26/(t-1))) over 26 fixed experts; loss=1-hits/7; '
           'ensemble = weighted vote of experts\' top-7 sets; predicted = top-7 by vote.',
           'S(i)=sum_e w_e*1[i in top7(s_e)], w_e ∝ exp(-eta_t*L_e), L_e=sum_{s<t}(1-|top7_e(s)∩draw_s|/7)'),
    'F2': ('Lorenz analogue / kNN: state z_s=[X_{s-1},X_{s-2},X_{s-3}] (99 bits), Hamming distance, '
           'k=30 nearest past states (ties -> more recent), score = sum of successor-draw indicators.',
           'S(i)=sum_{s in kNN30(z_t)} X[s,i]'),
    'F3': ('Permutation-symmetric MLP 17->16 tanh->1 shared over numbers, softmax over 33 numbers, CE vs X/7, '
           'L2 1e-4, Adam lr 0.005, early stopping on last 20% of past draws (patience 20, max 300), '
           'refit from scratch every 20 draws (t=30,50,...), features: 10 lags, freq30/100/all, log(1+gap), '
           'neighbours in last draw, order position in last draw, number id.',
           'S(i)=w2·tanh(W1·std(f_i(t))+b1)'),
}


def leakage_check(d):
    """Cached results must equal fresh computations from d[:t] only."""
    out = {}
    for t in (30, 200, 777, 1241):
        a1 = F1(d[:t], d[t]['date']); b1 = F1(d[:t], d[t]['date'], cache=HedgeCache())
        a3 = F3(d[:t], d[t]['date']); b3 = F3(d[:t], d[t]['date'], cache=MLPCache())
        out[t] = (sorted(a1) == sorted(b1), sorted(a3) == sorted(b3))
    return out


def main():
    t0 = time.time()
    d = load(GAME)
    res = []
    for name, f in (('F1', F1), ('F2', F2), ('F3', F3)):
        r = evaluate(f, GAME, 'S5_' + name)
        r['definition'], r['formula_text'] = DEFS[name]
        r = json.loads(json.dumps(r, default=float))
        res.append(r)
        print(name, r['mean_hits'], r['expected'], r['p_upper'], r['p_lower'], r['hist'], round(time.time() - t0, 1), flush=True)
    lk = leakage_check(d)
    print('leakage check', lk, flush=True)
    # diagnostics: final Hedge weights and per-expert walk-forward mean hits on evaluated draws (t>=30)
    w, L = hedge_weights(d, _HC)
    loss = np.array(_HC.loss)
    exp_hits = (1 - loss[30:]) * K
    diag = {'hedge_final_weights': {EXPERT_NAMES[e]: round(float(w[e]), 4) for e in np.argsort(-w)},
            'expert_mean_hits_t30plus': {EXPERT_NAMES[e]: round(float(exp_hits[:, e].mean()), 4) for e in range(M)},
            'leakage_check_cached_equals_fresh': {str(k): list(v) for k, v in lk.items()},
            'mlp_best_epochs': {str(k): int(v[1]['best_ep']) for k, v in sorted(_MC.models.items())}}
    pred = {n: sorted(f(d, '2026-11-28')) for n, f in (('F1', F1), ('F2', F2), ('F3', F3))}
    print('pred 28.11', pred)
    out = {'id': 'S5', 'science': 'machine learning / AI', 'game': GAME, 'formulas': res,
           'prediction_28_11': {'game': GAME, 'numbers': [int(x) for x in pred['F1']], 'formula': 'F1'},
           'other_formula_predictions_28_11': {k: [int(x) for x in v] for k, v in pred.items()},
           'diagnostics': diag, 'runtime_s': round(time.time() - t0, 1)}
    json.dump(out, open('/home/user/Mobil/tipos-all/lab/run_2811/agents/S5.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(diag, indent=1))


if __name__ == '__main__':
    main()
