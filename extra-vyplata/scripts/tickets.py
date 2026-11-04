"""Build ticket sets for Extra výplata that maximise P(at least one prize) for a given number of tickets.

Exact evaluation over all C(27,6)=296 010 possible main draws.
Usage: python3 -I tickets.py draws.json results.json out.json
"""
import json, sys, itertools, math, time
import numpy as np

D = json.load(open(sys.argv[1])); R = json.load(open(sys.argv[2])); OUT = sys.argv[3]
N, K, P = 27, 6, 7
T = len(D)
combos = np.array(list(itertools.combinations(range(1, N + 1), K)), dtype=np.int64)
cm = np.zeros(len(combos), dtype=np.uint32)
for j in range(K):
    cm |= (np.uint32(1) << combos[:, j].astype(np.uint32))
NC = len(cm)

def mask(t):
    m = 0
    for v in t: m |= 1 << v
    return np.uint32(m)

def ov(t):
    return np.bitwise_count(cm & mask(t)).astype(np.int8)

# ---------------- the "formula" (best performer of the walk-forward backtest) ----------------
main = np.zeros((T, N), int)
for i, d in enumerate(D): main[i, np.array(d['main']) - 1] = 1
pb = np.array([d['pb'] for d in D])
z = lambda v: (v - v.mean()) / (v.std() + 1e-9)
f_all = main.sum(0).astype(float); f_52 = main[-52:].sum(0).astype(float); f_20 = main[-20:].sum(0).astype(float)
score = 0.5 * z(f_all) + 0.35 * z(f_52) + 0.15 * z(f_20)
formula_main = sorted((np.argsort(-score)[:6] + 1).tolist())
pbs = 0.6 * z(np.bincount(pb, minlength=P + 1)[1:].astype(float)) + 0.4 * z(np.bincount(pb[-52:], minlength=P + 1)[1:].astype(float))
formula_pb = int(np.argmax(pbs) + 1)
ranking = [{'n': int(i + 1), 'score': float(score[i]), 'all': int(f_all[i]), 'last52': int(f_52[i]), 'last20': int(f_20[i])}
           for i in np.argsort(-score)]

pop = np.array([R['popularity'][str(i + 1)] for i in range(N)])

def patterny(t):
    t = sorted(t)
    d = np.diff(t)
    longest = 1; cur = 1
    for x in d:
        cur = cur + 1 if x == 1 else 1; longest = max(longest, cur)
    same_step = len(set(d)) == 1
    return longest >= 4 or same_step

def optimise(n, fixed=None, iters=2500, seed=0):
    r = np.random.default_rng(seed)
    tick = []
    if fixed: tick.append(list(fixed))
    # greedy start
    best = np.zeros(NC, np.int8)
    for t in tick: best = np.maximum(best, ov(t))
    while len(tick) < n:
        unc = best < 3
        cands = [sorted(r.choice(np.arange(1, N + 1), 6, replace=False).tolist()) for _ in range(400)]
        gains = [((np.bitwise_count(cm[unc] & mask(c)) >= 3).sum(), c) for c in cands if not patterny(c)]
        g, c = max(gains, key=lambda x: x[0])
        tick.append(c); best = np.maximum(best, ov(c))
    rows = np.stack([ov(t) for t in tick])

    def objective(rows):
        b = rows.max(0)
        return (b >= 3).mean() + 0.02 * (b >= 4).mean()

    cur = objective(rows)
    lo = 1 if fixed else 0
    for it in range(iters):
        if n - lo <= 0: break
        i = int(r.integers(lo, n)); t = list(tick[i])
        k = int(r.integers(6)); cand = [v for v in range(1, N + 1) if v not in t]
        t[k] = int(r.choice(cand)); t.sort()
        if patterny(t) or t in tick: continue
        old = rows[i].copy(); rows[i] = ov(t)
        v = objective(rows)
        if v >= cur:
            cur = v; tick[i] = t
        else:
            rows[i] = old
    b = rows.max(0)
    return tick, float((b >= 3).mean()), float((b >= 4).mean()), bool((b >= 3).all())

def quickpick(n, sims=200):
    r = np.random.default_rng(7); vals = []
    for s in range(sims):
        b = np.zeros(NC, np.int8)
        for _ in range(n):
            b = np.maximum(b, ov(r.choice(np.arange(1, N + 1), 6, replace=False)))
        vals.append((b >= 3).mean())
    return float(np.mean(vals))

def assign_pb(n, first_pb):
    order = [first_pb] + [p for p in [2, 1, 3, 6, 4, 5, 7] if p != first_pb]
    return [order[i % 7] for i in range(n)]

payout = R['economics']['payout_ratio']
out = {'formula': {'main': formula_main, 'pb': formula_pb, 'ranking': ranking,
                   'weights': '0.50*z(freq all) + 0.35*z(freq last 52) + 0.15*z(freq last 20)'},
       'plans': {}}
t0 = time.time()
for n in [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24]:
    it = 3000 if n <= 8 else 1500
    tk, p3, p4, guar = optimise(n, fixed=formula_main, iters=it, seed=n)
    pbl = assign_pb(n, formula_pb)
    qp = quickpick(n, 200 if n <= 8 else 60)
    out['plans'][str(n)] = {
        'tickets': [{'main': t, 'pb': p} for t, p in zip(tk, pbl)],
        'cost_eur': 1.5 * n, 'p_any_prize': p3, 'p_any_prize_quickpick': qp, 'p_4plus': p4,
        'guarantee_3': guar,
        'p_6main': n / math.comb(27, 6), 'p_jackpot': n / (math.comb(27, 6) * 7),
        'p_pb_at_least_one': min(n, 7) / 7,
        'expected_return_eur': 1.5 * n * payout, 'expected_loss_eur': 1.5 * n * (1 - payout)}
    print(n, round(p3, 4), 'qp', round(qp, 4), 'guar', guar, round(time.time() - t0, 1), file=sys.stderr)

# unconstrained search for the smallest set that guarantees >= 3 matches
g = None
for n in [24, 28, 32, 36]:
    tk, p3, p4, guar = optimise(n, iters=2500, seed=100 + n)
    print('guarantee search', n, round(p3, 5), guar, file=sys.stderr)
    if guar:
        g = {'n': n, 'cost_eur': 1.5 * n, 'tickets': tk}; break
    g = {'n': None, 'best_n_tried': n, 'coverage': p3}
out['guarantee3'] = g
json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
print('done', file=sys.stderr)
