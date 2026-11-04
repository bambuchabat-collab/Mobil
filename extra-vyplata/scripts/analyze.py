"""Extra výplata (TIPOS, 6/27 + 1/7) — full statistical analysis.

Usage: python3 -I analyze.py draws.json out.json
"""
import json, sys, time, itertools, math
import numpy as np

rng = np.random.default_rng(20261105)
D = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
N, K, P = 27, 6, 7
T = len(D)
R = {}

main = np.zeros((T, N + 1), dtype=np.int8)
for i, d in enumerate(D):
    main[i, d['main']] = 1
pb = np.array([d['pb'] for d in D])
R['n_draws'] = T
R['first'] = D[0]['date']; R['last'] = D[-1]['date']
R['last_draw'] = {'date': D[-1]['date'], 'main': D[-1]['main'], 'pb': D[-1]['pb']}

# ---------- all 296 010 main combinations as bitmasks ----------
combos = np.array(list(itertools.combinations(range(1, N + 1), K)), dtype=np.int64)
cmask = np.zeros(len(combos), dtype=np.int64)
for j in range(K):
    cmask |= (np.int64(1) << combos[:, j])
NC = len(combos)  # 296010

_tbl = np.array([bin(i).count('1') for i in range(256)], dtype=np.int8)
def _pc8(x):
    x = x.astype(np.uint64)
    s = np.zeros(x.shape, dtype=np.int16)
    for sh in range(0, 32, 8):
        s += _tbl[((x >> np.uint64(sh)) & np.uint64(255)).astype(np.int64)]
    return s

def tmask(t):
    m = 0
    for v in t: m |= 1 << v
    return np.int64(m)

# ---------- 1. frequencies ----------
freq = main[:, 1:].sum(0).astype(int)
pbf = np.bincount(pb, minlength=P + 1)[1:]
E = T * K / N; Epb = T / P
chi_main = float(((freq - E) ** 2 / E).sum())
chi_pb = float(((pbf - Epb) ** 2 / Epb).sum())

# Monte Carlo null: fair machine, same number of draws
SIMS = 20000
sim_chi = np.empty(SIMS); sim_max = np.empty(SIMS); sim_min = np.empty(SIMS)
sim_chi_pb = np.empty(SIMS); sim_pbmin = np.empty(SIMS)
for s in range(SIMS):
    picks = np.argsort(rng.random((T, N)), axis=1)[:, :K]
    f = np.bincount(picks.ravel(), minlength=N)
    sim_chi[s] = ((f - E) ** 2 / E).sum(); sim_max[s] = f.max(); sim_min[s] = f.min()
    fp = np.bincount(rng.integers(0, P, T), minlength=P)
    sim_chi_pb[s] = ((fp - Epb) ** 2 / Epb).sum(); sim_pbmin[s] = fp.min()
R['freq'] = {
    'main': {str(i + 1): int(v) for i, v in enumerate(freq)},
    'pb': {str(i + 1): int(v) for i, v in enumerate(pbf)},
    'expected_main': E, 'expected_pb': Epb,
    'sd_main': math.sqrt(T * (K / N) * (1 - K / N)), 'sd_pb': math.sqrt(T * (1 / P) * (1 - 1 / P)),
    'chi_main': chi_main, 'p_chi_main': float((sim_chi >= chi_main).mean()),
    'chi_pb': chi_pb, 'p_chi_pb': float((sim_chi_pb >= chi_pb).mean()),
    'p_max_main_ge': float((sim_max >= freq.max()).mean()),
    'p_min_main_le': float((sim_min <= freq.min()).mean()),
    'p_min_pb_le': float((sim_pbmin <= pbf.min()).mean()),
}
for w, name in [(52, '6m'), (80, '12m'), (9, '1m')]:
    R['freq']['main_' + name] = {str(i + 1): int(v) for i, v in enumerate(main[-w:, 1:].sum(0))}

# ---------- 2. stability: does "hot" persist? ----------
h = T // 2
f1 = main[:h, 1:].sum(0); f2 = main[h:, 1:].sum(0)
def spearman(a, b):
    ra = np.argsort(np.argsort(a + rng.random(len(a)) * 1e-6)); rb = np.argsort(np.argsort(b + rng.random(len(b)) * 1e-6))
    return float(np.corrcoef(ra, rb)[0, 1])
rho = spearman(f1, f2)
sim_rho = []
for s in range(5000):
    p1 = np.bincount(np.argsort(rng.random((h, N)), axis=1)[:, :K].ravel(), minlength=N)
    p2 = np.bincount(np.argsort(rng.random((T - h, N)), axis=1)[:, :K].ravel(), minlength=N)
    sim_rho.append(spearman(p1, p2))
sim_rho = np.array(sim_rho)
top6_first = list(np.argsort(-f1)[:6] + 1)
R['stability'] = {'rho_half': rho, 'p_rho': float((sim_rho >= rho).mean()),
                  'top6_first_half': [int(x) for x in top6_first],
                  'top6_first_half_hits_in_second_half': int(f2[np.array(top6_first) - 1].sum()),
                  'expected_hits': (T - h) * 6 * K / N,
                  'freq_11_by_half': [int(f1[10]), int(f2[10])]}

# ---------- 3. patterns vs exact theory ----------
csum = combos.sum(1); codd = (combos % 2).sum(1); clow = (combos <= 13).sum(1)
ccons = (np.diff(combos, axis=1) == 1).sum(1)
dm = np.array([d['main'] for d in D])
dsum = dm.sum(1); dodd = (dm % 2).sum(1); dlow = (dm <= 13).sum(1); dcons = (np.diff(dm, axis=1) == 1).sum(1)
rep = np.array([len(set(D[i]['main']) & set(D[i - 1]['main'])) for i in range(1, T)])
def dist(arr, vals):
    return {str(v): float((arr == v).mean()) for v in vals}
R['patterns'] = {
    'sum': {'mean_obs': float(dsum.mean()), 'mean_theory': float(csum.mean()), 'sd_theory': float(csum.std()),
            'p10_90_theory': [int(np.percentile(csum, 10)), int(np.percentile(csum, 90))],
            'obs_in_p10_90': float(((dsum >= np.percentile(csum, 10)) & (dsum <= np.percentile(csum, 90))).mean())},
    'odd': {'obs': dist(dodd, range(7)), 'theory': dist(codd, range(7))},
    'low1_13': {'obs': dist(dlow, range(7)), 'theory': dist(clow, range(7))},
    'consecutive_pairs': {'obs': dist(dcons, range(6)), 'theory': dist(ccons, range(6))},
    'repeat_from_prev': {'mean_obs': float(rep.mean()), 'mean_theory': 36 / 27,
                         'obs': dist(rep, range(7))},
    'pb_repeat_prev': {'obs': float((pb[1:] == pb[:-1]).mean()), 'theory': 1 / 7},
}

# ---------- 4. walk-forward backtest of "prediction formulas" ----------
START = 30
def gaps_at(t):
    g = np.full(N, t + 1.0)
    for n in range(N):
        idx = np.nonzero(main[:t, n + 1])[0]
        if len(idx): g[n] = t - idx[-1]
    return g

pair = np.zeros((T + 1, N, N))
for i in range(T):
    ns = np.array(D[i]['main']) - 1
    pair[i + 1] = pair[i]
    for a in ns:
        for b in ns:
            if a != b: pair[i + 1, a, b] += 1
trans = np.zeros((T + 1, N, N))  # number in draw i -> numbers in draw i+1
for i in range(1, T):
    trans[i + 1] = trans[i]
    for a in np.array(D[i - 1]['main']) - 1:
        trans[i + 1, a, np.array(D[i]['main']) - 1] += 1
trans[1] = trans[0]

def top6(score, t):
    # tie-break deterministically by a hash of t to avoid low-number bias
    tb = np.random.default_rng(t).random(N) * 1e-9
    return np.argsort(-(score + tb))[:6]

def pb_hot(t, w=None):
    x = pb[:t] if w is None else pb[max(0, t - w):t]
    return int(np.argmax(np.bincount(x, minlength=P + 1)[1:] + np.random.default_rng(t).random(P) * 1e-9) + 1)

def composite(t):
    """The 'formula': z-scored blend of long-run frequency, recent frequency, overdue gap and pair affinity."""
    f_all = main[:t, 1:].sum(0); f_rec = main[max(0, t - 20):t, 1:].sum(0)
    g = gaps_at(t)
    last = np.array(D[t - 1]['main']) - 1
    aff = pair[t][last].sum(0)
    z = lambda v: (v - v.mean()) / (v.std() + 1e-9)
    return 0.35 * z(f_all) + 0.25 * z(f_rec) + 0.20 * z(g) + 0.20 * z(aff)

strategies = {
    'hot_all':      lambda t: top6(main[:t, 1:].sum(0).astype(float), t),
    'hot_last10':   lambda t: top6(main[max(0, t - 10):t, 1:].sum(0).astype(float), t),
    'hot_last20':   lambda t: top6(main[max(0, t - 20):t, 1:].sum(0).astype(float), t),
    'hot_last52':   lambda t: top6(main[max(0, t - 52):t, 1:].sum(0).astype(float), t),
    'cold_all':     lambda t: top6(-main[:t, 1:].sum(0).astype(float), t),
    'overdue':      lambda t: top6(gaps_at(t), t),
    'repeat_last':  lambda t: np.array(D[t - 1]['main']) - 1,
    'pair_affinity': lambda t: top6(pair[t][np.array(D[t - 1]['main']) - 1].sum(0) * (1 - main[t - 1, 1:]), t),
    'markov':       lambda t: top6(trans[t][np.array(D[t - 1]['main']) - 1].sum(0).astype(float), t),
    'composite_formula': lambda t: top6(composite(t), t),
}
pb_strats = {'hot_all': lambda t: pb_hot(t), 'hot_last20': lambda t: pb_hot(t, 20),
             'cold_all': lambda t: int(np.argmin(np.bincount(pb[:t], minlength=P + 1)[1:] + np.random.default_rng(t).random(P) * 1e-9) + 1),
             'repeat_last': lambda t: int(pb[t - 1])}

def prize_of(d, m, p):
    key = f'{m}+{1 if p else 0}'
    tiers = d['tiers']
    if m < 3: return 0.0
    if key in tiers: return tiers[key][0]
    return tiers.get(f'{m}+0', (0.0, 0))[0]

bt = {}
nd = T - START
for name, fn in strategies.items():
    hits = []; ge3 = 0; money = 0.0
    for t in range(START, T):
        pick = set((fn(t) + 1).tolist())
        m = len(pick & set(D[t]['main'])); hits.append(m); ge3 += m >= 3
        money += prize_of(D[t], m, False)
    bt[name] = {'mean_hits': float(np.mean(hits)), 'total_hits': int(np.sum(hits)), 'ge3_rate': ge3 / nd,
                'hist': [int(np.sum(np.array(hits) == k)) for k in range(7)]}
pbt = {}
for name, fn in pb_strats.items():
    pbt[name] = float(np.mean([fn(t) == pb[t] for t in range(START, T)]))

# null distribution: random 6 picks each draw
SIMB = 20000
drawn = main[START:, 1:]
rnd_tot = np.empty(SIMB)
for s in range(SIMB):
    picks = np.argsort(rng.random((nd, N)), axis=1)[:, :K]
    rnd_tot[s] = np.take_along_axis(drawn, picks, 1).sum()
best = max(v['total_hits'] for v in bt.values())
for name in bt:
    bt[name]['p_vs_random'] = float((rnd_tot >= bt[name]['total_hits']).mean())
R['backtest'] = {'draws_tested': nd, 'from': D[START]['date'], 'random_mean_hits': 36 / 27,
                 'random_total_mean': float(rnd_tot.mean()), 'random_total_sd': float(rnd_tot.std()),
                 'random_ge3_rate': None, 'strategies': bt, 'pb_hit_rate': pbt, 'pb_random': 1 / 7,
                 # chance that the BEST of 10 random strategies looks at least this good
                 'p_best_of_10': float(1 - (1 - (rnd_tot >= best).mean()) ** 10)}

# ---------- 5. exact game odds ----------
c = math.comb
pm = {m: c(6, m) * c(21, 6 - m) / c(27, 6) for m in range(7)}
R['odds'] = {f'{m}+{b}': pm[m] * (1 / 7 if b else 6 / 7) for m in range(3, 7) for b in (1, 0)}
R['backtest']['random_ge3_rate'] = pm[3] + pm[4] + pm[5] + pm[6]
R['p_any_prize_1ticket'] = R['backtest']['random_ge3_rate']

# economics
dep = sum(d['deposits'] for d in D); win = sum(d['wins'] for d in D)
tickets = dep / 1.5
t1 = sum(d['tiers']['6+1'][1] for d in D); t2 = sum(d['tiers']['6+0'][1] for d in D)
R['economics'] = {'deposits': dep, 'wins': win, 'payout_ratio': win / dep, 'tickets_est': tickets,
                  'tier1_winners': t1, 'tier1_expected': tickets * R['odds']['6+1'],
                  'tier2_winners': t2, 'tier2_expected': tickets * R['odds']['6+0']}
# average realised lower-tier prizes (last 52 draws)
avgp = {}
for k in ['5+1', '5+0', '4+1', '4+0', '3+1', '3+0']:
    v = [d['tiers'][k][0] for d in D[-52:] if k in d['tiers'] and d['tiers'][k][0] > 0]
    avgp[k] = float(np.mean(v))
avgp['6+1'] = 480000.0; avgp['6+0'] = 30000.0
R['avg_prize_last52'] = avgp
ev = sum(R['odds'][k] * avgp[k] for k in R['odds'])
R['ev_per_ticket'] = ev

# ---------- 6. popularity of numbers among players (from winner counts) ----------
rows = []; y = []
for d in D:
    tk = d['deposits'] / 1.5
    w3 = d['tiers'].get('3+0', (0, 0))[1] + d['tiers'].get('3+1', (0, 0))[1]
    w4 = d['tiers'].get('4+0', (0, 0))[1] + d['tiers'].get('4+1', (0, 0))[1]
    exp3 = tk * pm[3]; exp4 = tk * pm[4]
    yy = math.log((w3 + w4 * 1.0 + 1) / (exp3 + exp4))
    x = np.zeros(N); x[np.array(d['main']) - 1] = 1
    rows.append(x); y.append(yy)
X = np.array(rows); y = np.array(y)
Xc = np.hstack([X, np.ones((T, 1))])
lam = 2.0
A = Xc.T @ Xc + lam * np.diag([1] * N + [0])
beta = np.linalg.solve(A, Xc.T @ y)[:N]
beta = beta - beta.mean()
R['popularity'] = {str(i + 1): float(b) for i, b in enumerate(beta)}
R['popularity_ratio_mean'] = float(np.exp(y).mean())

# ---------- 7. how many tickets: optimised coverage ----------
def p_any(masks):
    best = np.zeros(NC, dtype=np.int16)
    for m in masks:
        best = np.maximum(best, _pc8(cmask & m))
    return best

def score(masks):
    b = p_any(masks)
    return float((b >= 3).mean()), b

def optimise(n, iters, pop_pen=None, seed=0):
    r = np.random.default_rng(seed)
    # start: spread numbers round-robin
    nums = list(r.permutation(np.arange(1, N + 1)))
    tick = []
    k = 0
    for i in range(n):
        t = set()
        while len(t) < 6:
            t.add(int(nums[k % N])); k += 1
        tick.append(sorted(t))
    def obj(ts):
        s, _ = score([tmask(t) for t in ts])
        if pop_pen is not None:
            s -= 0.002 * sum(pop_pen[v - 1] for t in ts for v in t) / max(1, n)
        return s
    cur = obj(tick); best = (cur, [list(t) for t in tick])
    temp = 0.01
    for it in range(iters):
        i = r.integers(n); t = list(tick[i])
        out = r.integers(6); cand = [v for v in range(1, N + 1) if v not in t]
        t[out] = int(r.choice(cand)); t.sort()
        new = [list(x) for x in tick]; new[i] = t
        if len({tuple(x) for x in new}) < n: continue
        v = obj(new)
        if v >= cur or r.random() < math.exp((v - cur) / temp):
            tick, cur = new, v
            if v > best[0]: best = (v, [list(x) for x in new])
        temp *= 0.997
    return best

def random_sets(n, sims=300):
    vals = []
    r = np.random.default_rng(99)
    for s in range(sims):
        ts = [sorted(r.choice(np.arange(1, N + 1), 6, replace=False).tolist()) for _ in range(n)]
        vals.append(score([tmask(t) for t in ts])[0])
    return float(np.mean(vals))

pop = np.array([R['popularity'][str(i + 1)] for i in range(N)])
cover = {}
t0 = time.time()
for n in [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 16]:
    it = 400 if n <= 8 else 250
    val, tk = optimise(n, it, seed=n)
    _, b = score([tmask(t) for t in tk])
    cover[str(n)] = {'p_any_main3_opt': val, 'p_any_main3_random': random_sets(n, 150 if n <= 8 else 60),
                     'tickets': tk, 'p_guarantee': float((b >= 3).all()),
                     'p_ge4': float((b >= 4).mean())}
    print('cover', n, round(val, 4), cover[str(n)]['p_any_main3_random'], round(time.time() - t0, 1), file=sys.stderr)
R['coverage'] = cover

json.dump(R, open(OUT, 'w'), ensure_ascii=False, indent=1)
print('done', file=sys.stderr)
