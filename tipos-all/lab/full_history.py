"""Full-history ball-bias study for Loto 5 z 35 (all draws TIPOS publishes).
Usage: python3 -I full_history.py l535_all.json out.json
"""
import json, sys, math
import numpy as np
rng = np.random.default_rng(2026)
raw = [r for r in json.load(open(sys.argv[1])) if r['raw'] and r['raw'].get('Zrebovanie')]
D = []
for r in raw:
    z = [int(x) for x in r['raw']['Zrebovanie']]
    if len(z) == 5 and len(set(z)) == 5 and max(z) <= 35 and min(z) >= 1: D.append((r['date'], z))
dates = [d for d, _ in D]; order = np.array([z for _, z in D]); T, N, K = len(D), 35, 5
M = np.zeros((T, N), int)
for i, z in enumerate(order): M[i, z - 1] = 1
out = {'draws': T, 'first': dates[0], 'last': dates[-1], 'skipped': len(raw) - T}
p0 = K / N; E = T * p0
f = M.sum(0)

# a) overall frequency test
chi = float(((f - E) ** 2 / E).sum())
sims = np.array([((np.bincount(np.argsort(rng.random((T, N)), 1)[:, :K].ravel(), minlength=N) - E) ** 2 / E).sum() for _ in range(2000)])
out['chi'] = {'chi': chi, 'p': float((sims >= chi).mean()), 'most': [(int(i + 1), int(f[i])) for i in np.argsort(-f)[:5]],
              'least': [(int(i + 1), int(f[i])) for i in np.argsort(f)[:5]], 'expected': E}

# b) persistence: a physical defect would push the same balls up in consecutive eras
B = 6; edges = np.linspace(0, T, B + 1).astype(int)
dev = np.array([(M[a:b].sum(0) - (b - a) * p0) / math.sqrt((b - a) * p0 * (1 - p0)) for a, b in zip(edges[:-1], edges[1:])])
def mean_adj_corr(dv): return float(np.mean([np.corrcoef(dv[i], dv[i + 1])[0, 1] for i in range(len(dv) - 1)]))
obs = mean_adj_corr(dev); sim = []
for _ in range(2000):
    Ms = np.zeros((T, N), int); idx = np.argsort(rng.random((T, N)), 1)[:, :K]
    np.put_along_axis(Ms, idx, 1, 1)
    sim.append(mean_adj_corr(np.array([(Ms[a:b].sum(0) - (b - a) * p0) / math.sqrt((b - a) * p0 * (1 - p0)) for a, b in zip(edges[:-1], edges[1:])])))
out['persistence'] = {'eras': [f'{dates[a]}..{dates[b - 1]}' for a, b in zip(edges[:-1], edges[1:])], 'mean_adjacent_corr': obs, 'p': float((np.array(sim) >= obs).mean())}

# c) draw-order: do some balls come out earlier (lighter) than others?
pos = np.zeros(N); cnt = np.zeros(N)
for z in order:
    for k, v in enumerate(z): pos[v - 1] += k + 1; cnt[v - 1] += 1
stat = float((((pos / cnt) - 3) ** 2 * cnt).sum()); sims = []
for _ in range(2000):
    ps = np.zeros(N)
    perm = np.argsort(rng.random((T, K)), 1)
    shuffled = np.take_along_axis(order, perm, 1)
    for k in range(K): np.add.at(ps, shuffled[:, k] - 1, k + 1)
    sims.append(float((((ps / cnt) - 3) ** 2 * cnt).sum()))
early = np.argsort(pos / cnt)[:5] + 1
out['draw_order'] = {'p': float((np.array(sims) >= stat).mean()), 'earliest_balls': early.tolist()}

# d) walk-forward on the long history: long-run hot numbers and 200-draw window
var1 = K * p0 * (1 - p0) * ((N - K) / (N - 1))
def wf(fn, start=200):
    h = np.array([M[t, fn(t)].sum() for t in range(start, T)]); n = len(h)
    return {'draws': n, 'mean_hits': float(h.mean()), 'z': float((h.sum() - n * K * K / N) / math.sqrt(n * var1))}
tb = lambda t: np.random.default_rng(t).random(N) * 1e-9
out['walk_forward'] = {'hot_all': wf(lambda t: np.argsort(-(M[:t].sum(0) + tb(t)))[:5]),
                       'hot_200': wf(lambda t: np.argsort(-(M[max(0, t - 200):t].sum(0) + tb(t)))[:5]),
                       'cold_all': wf(lambda t: np.argsort(M[:t].sum(0) + tb(t))[:5]), 'random_mean': K * K / N}

# e) smallest single-ball bias detectable with all these draws (80% power, Bonferroni over 35 balls)
zc = 3.43
for b in np.arange(0.01, 0.6, 0.005):
    p1 = p0 * (1 + b); power = 1 - 0.5 * math.erfc(-((T * p0 + zc * math.sqrt(T * p0 * (1 - p0)) - T * p1) / math.sqrt(T * p1 * (1 - p1))) / math.sqrt(2))
    if power >= 0.8: break
out['min_detectable_bias'] = float(b)

# f) best possible per-ball estimate for the next draw: empirical-Bayes shrinkage of recent frequencies
rec = M[-600:].sum(0); n = 600; obs_var = np.var(rec / n); samp_var = p0 * (1 - p0) / n
tau2 = max(obs_var - samp_var, 0.0); w = tau2 / (tau2 + samp_var) if tau2 > 0 else 0.0
post = p0 + w * (rec / n - p0)
out['next_draw_prob'] = {'shrink_weight': float(w), 'max_abs_deviation_pp': float(100 * np.max(np.abs(post - p0))),
                         'top5': [(int(i + 1), round(float(post[i]), 4)) for i in np.argsort(-post)[:5]]}
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
