"""How many Loto 5 z 35 + JOKER tickets: outcome distribution, Kelly stake, and diversified fields.
Usage: python3 -I joker_plan.py multi.json out.json
"""
import json, sys, math, itertools
import numpy as np

R = json.load(open(sys.argv[1])); OUT = sys.argv[2]
J = R['joker']; L = R['loto535']
rng = np.random.default_rng(7)
C = math.comb
N35 = C(35, 5)

# ---- per-ticket outcome table (1 field Loto 5 z 35 + JOKER, 1.20 EUR) ----
jack_j = J['pot_next_est'] * J['share_factor']          # expected Joker jackpot payout incl. sharing
jack_l = L['pot_next_est'] * 0.8                        # Loto 5 z 35 pot with typical sharing
pj = {'J6': 1e-6, 'J5': 9e-6, 'J4': 9e-5, 'J3': 9e-4, 'J2': 9e-3}
vj = {'J6': jack_j, 'J5': 3300, 'J4': 330, 'J3': 33, 'J2': 3.30}
pl = {'L5': 1 / N35, 'L4': C(5, 4) * C(30, 1) / N35, 'L3': C(5, 3) * C(30, 2) / N35}
vl = {'L5': jack_l, 'L4': L['avg_prizes']['4'], 'L3': L['avg_prizes']['3']}
jk = list(pj); lk = list(pl)
jp = np.array([pj[k] for k in jk] + [1 - sum(pj.values())]); jv = np.array([vj[k] for k in jk] + [0.0])
lp = np.array([pl[k] for k in lk] + [1 - sum(pl.values())]); lv = np.array([vl[k] for k in lk] + [0.0])
ev1 = float((jp * jv).sum() + (lp * lv).sum())

# ---- Kelly: maximise E[log wealth] for a bet of size f*bankroll on this ticket ----
outs = []
for a, b in itertools.product(range(len(jp)), range(len(lp))):
    outs.append((jp[a] * lp[b], (jv[a] + lv[b]) / 1.20))
pr = np.array([o[0] for o in outs]); ret = np.array([o[1] for o in outs])
def g(f): return float((pr * np.log1p(f * (ret - 1))).sum())
lo, hi = 0.0, 1e-3
for _ in range(200):
    m1 = lo + (hi - lo) / 3; m2 = hi - (hi - lo) / 3
    if g(m1) < g(m2): lo = m1
    else: hi = m2
kelly_f = (lo + hi) / 2
kelly_bankroll_for_one = 1.20 / kelly_f if kelly_f > 0 else float('inf')

# ---- Monte Carlo for N tickets in one draw ----
plans = {}
for n in [1, 3, 5, 10, 20, 50, 100]:
    S = 400000
    tot = np.zeros(S)
    for _ in range(n):
        tot += jv[np.searchsorted(np.cumsum(jp), rng.random(S))] + lv[np.searchsorted(np.cumsum(lp), rng.random(S))]
    cost = 1.20 * n
    plans[str(n)] = {'cost': cost, 'ev': ev1 * n, 'ev_ratio': ev1 / 1.20,
                     'p_joker_jackpot': 1 - (1 - 1e-6) ** n, 'p_any_joker': 1 - (1 - 0.01) ** n,
                     'p_any_prize': 1 - ((1 - 0.01) * (1 - sum(pl.values()))) ** n,
                     'p_profit': float((tot >= cost).mean()), 'median_back': float(np.median(tot)),
                     'p90_back': float(np.percentile(tot, 90)),
                     'mean_back_without_jackpots': float(n * ((jp[1:] * jv[1:]).sum() + (lp[1:] * lv[1:]).sum()))}

# guarantee: random 6-digit Joker numbers -> share of distinct numbers covered by n random tickets
guar = {'tickets_for_63pct': 1_000_000, 'cost_1m': 1.2e6,
        'coverage_1m': 1 - math.exp(-1), 'tickets_for_99pct': int(math.ceil(-math.log(0.01) * 1e6)),
        'cost_99pct': 1.2 * math.ceil(-math.log(0.01) * 1e6), 'jackpot': J['pot_next_est']}

# ---- diversified Loto 5 z 35 fields (max chance of >=3 matches somewhere), first = formula pick ----
combos = np.array(list(itertools.combinations(range(1, 36), 5)), dtype=np.int64)
cm = np.zeros(len(combos), dtype=np.uint64)
for j in range(5): cm |= (np.uint64(1) << combos[:, j].astype(np.uint64))
def mask(t):
    m = 0
    for v in t: m |= 1 << v
    return np.uint64(m)
def ov(t): return np.bitwise_count(cm & mask(t)).astype(np.int8)
def optimise(n, fixed, iters, seed):
    r = np.random.default_rng(seed); tick = [list(t) for t in fixed]
    best = np.zeros(len(cm), np.int8)
    for t in tick: best = np.maximum(best, ov(t))
    while len(tick) < n:
        unc = best < 3
        cands = [sorted(r.choice(np.arange(1, 36), 5, replace=False).tolist()) for _ in range(500)]
        c = max(cands, key=lambda c: (np.bitwise_count(cm[unc] & mask(c)) >= 3).sum())
        tick.append(c); best = np.maximum(best, ov(c))
    rows = np.stack([ov(t) for t in tick]); obj = lambda rows: (rows.max(0) >= 3).mean()
    cur = obj(rows); lo_ = len(fixed)
    for _ in range(iters):
        i = int(r.integers(lo_, n)); t = list(tick[i]); k = int(r.integers(5))
        t[k] = int(r.choice([v for v in range(1, 36) if v not in t])); t.sort()
        if t in tick: continue
        old = rows[i].copy(); rows[i] = ov(t); v = obj(rows)
        if v >= cur: cur = v; tick[i] = t
        else: rows[i] = old
    return tick, float(cur)
first = [L['pool']['formula_pick']]
t5, c5 = optimise(5, first, 1500, 1)
t10, c10 = optimise(10, t5, 1500, 2)
t20, c20 = optimise(20, t10, 1000, 3)
out = {'ev_per_ticket': ev1, 'ev_ratio': ev1 / 1.20, 'kelly_fraction': kelly_f, 'kelly_bankroll_for_one_ticket': kelly_bankroll_for_one,
       'plans': plans, 'guarantee': guar, 'fields': {'5': t5, '10': t10, '20': t20}, 'cover': {'5': c5, '10': c10, '20': c20},
       'jack_joker_eff': jack_j}
json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'fields'}, ensure_ascii=False, indent=1))
print(t10)
