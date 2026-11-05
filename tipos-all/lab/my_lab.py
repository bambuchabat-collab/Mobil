"""My own experiments for Loto 5 z 35 (different from the agent's list).
A) analog / nearest-neighbour forecasting  B) Hedge meta-learner over strategies
C) compression randomness test  D) power analysis: smallest bias we could detect
Usage: python3 -I my_lab.py l535.json out.json
"""
import json, sys, math, zlib
import numpy as np
raw = [r for r in json.load(open(sys.argv[1])) if r['raw'] and len(r['raw'].get('Zrebovanie', [])) == 5]
dates = [r['date'] for r in raw]
D = [[int(x) for x in r['raw']['Zrebovanie']] for r in raw]
T, N, K = len(D), 35, 5
M = np.zeros((T, N), int)
for i, d in enumerate(D): M[i, np.array(d) - 1] = 1
rng = np.random.default_rng(3)
HOLD = next(i for i, d in enumerate(dates) if d >= '2024-01-01')
var1 = K * (K / N) * ((N - K) / N) * ((N - K) / (N - 1)); base = K * K / N
def z_of(h): h = np.asarray(h); return float((h.sum() - len(h) * base) / math.sqrt(len(h) * var1))
out = {}

# ---------- A) analog forecasting: find past draws similar to the latest window, look at what came next ----------
def analog_scores(t, w, k):
    # state = frequency vector of the last w draws; neighbours by cosine similarity
    S = np.array([M[max(0, s - w):s].sum(0) for s in range(w, t)], float)   # states preceding draw s
    cur = M[t - w:t].sum(0).astype(float)
    sim = (S @ cur) / (np.linalg.norm(S, axis=1) * np.linalg.norm(cur) + 1e-9)
    idx = np.argsort(-sim)[:k] + w
    return M[idx].sum(0) + rng.random(N) * 1e-6
best_cfg = None; res_train = {}
for w in (1, 2, 3, 5, 10):
    for k in (5, 20, 50):
        h = [M[t, np.argsort(-analog_scores(t, w, k))[:5]].sum() for t in range(200, HOLD)]
        res_train[f'w{w}_k{k}'] = z_of(h)
        if best_cfg is None or z_of(h) > res_train[best_cfg]: best_cfg = f'w{w}_k{k}'
w, k = [int(x[1:]) for x in best_cfg.split('_')]
h_hold = [M[t, np.argsort(-analog_scores(t, w, k))[:5]].sum() for t in range(HOLD, T)]
out['analog'] = {'train_z_by_config': res_train, 'chosen_on_train': best_cfg, 'holdout_mean_hits': float(np.mean(h_hold)), 'holdout_z': z_of(h_hold),
                 'pick_next': sorted((np.argsort(-analog_scores(T, w, k))[:5] + 1).tolist())}

# ---------- B) Hedge meta-learner over 8 base strategies (learns which one works lately) ----------
def strat_scores(t):
    tb = rng.random(N) * 1e-6
    last_seen = np.array([t - (np.nonzero(M[:t, j])[0][-1] if M[:t, j].any() else -1) for j in range(N)], float)
    co = (M[:t].T @ M[:t]).astype(float); np.fill_diagonal(co, 0)
    return [M[:t].sum(0) + tb, M[max(0, t - 52):t].sum(0) + tb, M[max(0, t - 20):t].sum(0) + tb, -M[:t].sum(0) + tb,
            last_seen + tb, M[t - 1] + tb, co[M[t - 1] == 1].sum(0) + tb, rng.random(N)]
names = ['hot_all', 'hot_52', 'hot_20', 'cold', 'overdue', 'repeat', 'pairs', 'random']
eta = 0.3; wts = np.ones(len(names)); hits_meta = []; hits_meta_hold = []
for t in range(60, T):
    sc = strat_scores(t)
    picks = [np.argsort(-s)[:5] for s in sc]
    # aggregate: weighted vote of each strategy's top-5
    vote = np.zeros(N)
    for wgt, p in zip(wts, picks): vote[p] += wgt
    pick = np.argsort(-(vote + rng.random(N) * 1e-6))[:5]
    hm = M[t, pick].sum(); hits_meta.append(hm)
    if t >= HOLD: hits_meta_hold.append(hm)
    gains = np.array([M[t, p].sum() for p in picks], float)
    wts *= np.exp(eta * (gains - gains.mean())); wts /= wts.sum()
out['hedge'] = {'holdout_mean_hits': float(np.mean(hits_meta_hold)), 'holdout_z': z_of(hits_meta_hold),
                'final_weights': dict(zip(names, map(float, wts)))}
sc = strat_scores(T); vote = np.zeros(N)
for wgt, s in zip(wts, sc): vote[np.argsort(-s)[:5]] += wgt
out['hedge']['pick_next'] = sorted((np.argsort(-(vote + rng.random(N) * 1e-6))[:5] + 1).tolist())

# ---------- C) compression test: is the real sequence more compressible than shuffled ones? ----------
def comp_len(Mx): return len(zlib.compress(np.packbits(Mx.astype(np.uint8), axis=None).tobytes(), 9))
real = comp_len(M)
sims = []
for _ in range(300):
    Ms = np.zeros_like(M)
    for i in range(T): Ms[i, rng.choice(N, 5, replace=False)] = 1
    sims.append(comp_len(Ms))
out['compression'] = {'real_bytes': real, 'random_mean': float(np.mean(sims)), 'random_sd': float(np.std(sims)), 'p_more_compressible': float(np.mean(np.array(sims) <= real))}

# ---------- D) power: smallest single-ball bias detectable with these draws ----------
# if one ball had probability (5/35)*(1+b), how big must b be for a 2-sided 1% test across 35 balls (Bonferroni) to catch it 80% of the time?
p0 = 5 / 35
zcrit = 3.43  # ~ two-sided 0.01/35
for b in np.arange(0.02, 0.6, 0.01):
    p1 = p0 * (1 + b); se0 = math.sqrt(T * p0 * (1 - p0)); se1 = math.sqrt(T * p1 * (1 - p1))
    power = 1 - 0.5 * math.erfc(-((T * p0 + zcrit * se0 - T * p1) / se1) / math.sqrt(2))
    if power >= 0.8: break
gain = b * 1 / 5  # if you include that ball, expected hits rise by p0*b per ball pick... relative gain of a 5-pick containing it
out['power'] = {'draws': T, 'min_detectable_bias': float(b), 'note': 'one ball drawn this much more often than 1/7 would be detected with 80% power'}
json.dump(out, open(sys.argv[2], 'w'), indent=1)
print(json.dumps(out, indent=1))
