"""Red team, part 4: multiplicity + stability (python3 -I -B, numpy, fixed seeds).
- own Holm over all 30 primary p (p_mean_lower) and over p_le3; compare with aggregate.json;
- distribution of the 30 p-values: KS vs U(0,1) (all 30, and 27 after dropping exact duplicates/complements);
- correlation-aware global min-p test, conditional on the 30 actual ticket sequences (redteam_tickets.json):
  draws re-simulated uniformly, P(min_r p_r <= observed min p);
- A7 R2 (mirror 23-x) stability: halves / quarters of the evaluation draws (descriptive, not a new test);
- what the best effect would mean for P(0 hits) if it were real; power of the design.
Writes redteam_stats.json."""
import sys, os, json
sys.dont_write_bytecode = True
RUN = '/home/user/Mobil/tipos-all/lab/run_2511'
sys.path.insert(0, RUN)
import numpy as np
from math import comb, erf, sqrt, exp, log
from harness import DRAWS, PMF, _sum_pmf

AG = os.path.join(RUN, 'agents')
rows = []
for i in range(1, 11):
    j = json.load(open(os.path.join(AG, f'A{i}.json')))
    for r in j['rules']:
        rows.append({'agent': j['id'], 'rule': r['rule'], 'p': r['p_mean_lower'], 'p_le3': r['p_le3'],
                     'mean': r['mean_hits']})
m = len(rows)


def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps, kind='stable'); adj = np.empty(len(ps)); run = 0.0
    for k, i in enumerate(o):
        run = max(run, min(1.0, (len(ps) - k) * ps[i])); adj[i] = run
    return adj


def bh(ps):
    ps = np.asarray(ps, float); n_ = len(ps); o = np.argsort(ps); q = np.empty(n_); run = 1.0
    for k in range(n_ - 1, -1, -1):
        i = o[k]; run = min(run, ps[i] * n_ / (k + 1)); q[i] = run
    return q


hp = holm([r['p'] for r in rows]); hl = holm([r['p_le3'] for r in rows]); q = bh([r['p'] for r in rows])
agg = {(r['agent'], r['rule']): r for r in json.load(open(os.path.join(RUN, 'aggregate.json')))['rows']}
for r, a, b, c in zip(rows, hp, hl, q):
    r['holm'] = float(a); r['holm_le3'] = float(b); r['bh_q'] = float(c)
    g = agg[(r['agent'], r['rule'])]
    r['matches_aggregate'] = abs(g['holm'] - a) < 1e-12 and abs(g['holm_le3'] - b) < 1e-12 and abs(g['p'] - r['p']) < 1e-15
rows.sort(key=lambda r: r['p'])


def kolmogorov_sf(x):
    return float(max(0.0, min(1.0, 2 * sum((-1) ** (k - 1) * exp(-2 * k * k * x * x) for k in range(1, 101)))))


def ks(ps, rng, sims=200000):
    p = np.sort(np.asarray(ps)); n_ = len(p); i = np.arange(1, n_ + 1)
    dp = float(np.max(i / n_ - p)); dm = float(np.max(p - (i - 1) / n_)); D = max(dp, dm)
    U = np.sort(rng.random((sims, n_)), axis=1)
    Dp = np.max(i / n_ - U, axis=1); Dm = np.max(U - (i - 1) / n_, axis=1)
    return {'n': n_, 'D': D, 'D_plus_excess_small_p': dp, 'D_minus': dm,
            'p_two_sided_mc_indep': float((np.maximum(Dp, Dm) >= D - 1e-12).mean()),
            'p_one_sided_excess_small_mc_indep': float((Dp >= dp - 1e-12).mean()),
            'p_two_sided_asymptotic': kolmogorov_sf(D * (sqrt(n_) + 0.12 + 0.11 / sqrt(n_))),
            'n_p_le_0.05': int((p <= 0.05).sum()), 'expected_le_0.05': 0.05 * n_,
            'P_at_least_that_many_le_0.05_indep': float(sum(comb(n_, k) * 0.05 ** k * 0.95 ** (n_ - k)
                                                          for k in range(int((p <= 0.05).sum()), n_ + 1))),
            'mean_p': float(p.mean())}


rng = np.random.default_rng(31)
allp = [r['p'] for r in rows]
drop = {('A8', 'R2'), ('A6', 'R2'), ('A10', 'R2')}   # A8 R2 == R1 (same combo); A6/A10 R2 = complement of R1
dedup = [r['p'] for r in rows if (r['agent'], r['rule']) not in drop]
OUT = {'holm': {'m': m, 'rows': rows, 'survivors_holm_p': [(r['agent'], r['rule']) for r in rows if r['holm'] < 0.05],
                'survivors_holm_le3': [(r['agent'], r['rule']) for r in rows if r['holm_le3'] < 0.05],
                'survivors_bh_q_0.05': [(r['agent'], r['rule']) for r in rows if r['bh_q'] < 0.05],
                'all_match_aggregate_json': all(r['matches_aggregate'] for r in rows),
                'bonferroni_threshold': 0.05 / m,
                'min_p': rows[0]['p'], 'min_p_holm': rows[0]['holm'],
                'min_p_le3': min(r['p_le3'] for r in rows), 'min_p_le3_holm': min(r['holm_le3'] for r in rows)},
       'ks_all30': ks(allp, rng), 'ks_dedup27': ks(dedup, rng),
       'ks_note': 'p-values are not independent (A6/A10 R1-R2 complements, A8 R1==R2, shared inputs); '
                  'MC p assumes independence and is only indicative'}

# ---------------- correlation-aware global min-p (conditional on actual tickets) ----------------
tk_path = os.path.join(RUN, 'redteam_tickets.json')
if os.path.exists(tk_path):
    TK = json.load(open(tk_path)); ts = TK['t']; n = len(ts)
    keys = sorted(TK['tickets'])
    TM = np.zeros((len(keys), n, 22), np.int8)
    for a, k in enumerate(keys):
        for j, T in enumerate(TK['tickets'][k]):
            TM[a, j, np.array(T) - 1] = 1
    DR = np.zeros((n, 22), np.int8)
    for j, t in enumerate(ts):
        DR[j, np.array(DRAWS[t]['main']) - 1] = 1
    H = (TM * DR[None]).sum(2)                            # observed hits (rules x draws)
    cdf = np.cumsum(_sum_pmf(n))
    S_obs = H.sum(1); p_obs = cdf[S_obs]
    rep = {k: float(p) for k, p in zip(keys, p_obs)}
    pr = {f"{r['agent']}:{r['rule']}": r['p'] for r in rows}
    same = all(abs(rep[k] - pr[k]) < 1e-12 for k in keys)
    C = np.corrcoef(H)
    iu = np.triu_indices(len(keys), 1)
    rng = np.random.default_rng(2026)
    SIMS = 20000
    minp = np.empty(SIMS)
    TMf = TM.reshape(len(keys), -1).astype(np.int16)
    for s in range(SIMS):
        D = np.zeros((n, 22), np.int16)
        D[np.arange(n)[:, None], np.argsort(rng.random((n, 22)), axis=1)[:, :11]] = 1
        Hs = TMf @ D.ravel()
        minp[s] = cdf[Hs].min()
    obs_min = float(p_obs.min())
    OUT['global_minp_conditional'] = {
        'rules': len(keys), 'tickets_reproduce_reported_p': same, 'observed_min_p': obs_min,
        'sims': SIMS, 'P_minp_le_observed': float((minp <= obs_min + 1e-15).mean()),
        'P_minp_le_observed_if_indep': float(1 - (1 - obs_min) ** len(keys)),
        'minp_5pct_quantile': float(np.quantile(minp, 0.05)),
        'hit_corr_offdiag': {'min': float(C[iu].min()), 'max': float(C[iu].max()), 'mean_abs': float(np.abs(C[iu]).mean()),
                             'pairs_abs_gt_0.5': [(keys[i], keys[j], round(float(C[i, j]), 3)) for i, j in zip(*iu)
                                                  if abs(C[i, j]) > 0.5]}}
else:
    OUT['global_minp_conditional'] = 'redteam_tickets.json missing (run redteam_leak.py first)'

# ---------------- A7 R2 mirror stability ----------------
def mirror_hits(t):
    return len({23 - x for x in DRAWS[t - 1]['main']} & set(DRAWS[t]['main']))
h = np.array([mirror_hits(t) for t in range(30, len(DRAWS))])
var1 = 11 ** 4 / (22 * 22 * 21)


def seg(hs, label):
    n_ = len(hs); S = int(hs.sum()); sp = _sum_pmf(n_)
    z = (S - 5.5 * n_) / sqrt(n_ * var1)
    return {'segment': label, 'n': n_, 'mean_hits': S / n_, 'z': z, 'p_mean_lower_exact': float(sp[:S + 1].sum()),
            'n_le3': int((hs <= 3).sum()), 'expected_le3': n_ * float(PMF[:4].sum())}


half = len(h) // 2
stab = [seg(h, 'all t=30..411'), seg(h[:half], f't=30..{30 + half - 1}'), seg(h[half:], f't={30 + half}..411')]
qn = len(h) // 4
for k in range(4):
    a, b = k * qn, (k + 1) * qn if k < 3 else len(h)
    stab.append(seg(h[a:b], f'quarter {k + 1}: t={30 + a}..{30 + b - 1}'))
h_pre = np.array([mirror_hits(t) for t in range(1, 30)])
stab.append(seg(h_pre, 'direction-fixing draws t=1..29 (m0)'))
# heterogeneity between halves: difference of means
d = h[:half].mean() - h[half:].mean(); se = sqrt(var1 * (1 / half + 1 / (len(h) - half)))
reported_mean = 5.363874345549738
OUT['A7_R2_stability'] = {'segments': stab, 'halves_diff_mean': float(d), 'halves_diff_z': float(d / se),
                          'reproduces_reported_mean': abs(h.mean() - reported_mean) < 1e-12,
                          'rolling_100_mean_min_max': [float(np.convolve(h, np.ones(100) / 100, 'valid').min()),
                                                       float(np.convolve(h, np.ones(100) / 100, 'valid').max())]}

# ---------------- what if the best effect were real? ----------------
def tilt(mean_target):
    lo, hi = -3.0, 3.0
    k = np.arange(12)
    for _ in range(200):
        lam = (lo + hi) / 2; w = PMF * np.exp(lam * k); w /= w.sum()
        if (w * k).sum() < mean_target: lo = lam
        else: hi = lam
    return w
w = tilt(reported_mean)
sd_mean = sqrt(var1 / 382)
z_holm = 2.935   # one-sided z for 0.05/30
OUT['effect_meaning'] = {
    'assumed_mean_hits': reported_mean, 'tilted_P0': float(w[0]), 'tilted_1_in': float(1 / w[0]),
    'null_P0_1_in': 705432, 'tilted_P0_or_11_1_in': float(1 / (w[0] + w[11])),
    'note': 'max-entropy (exponential tilt) hit distribution with the observed best mean; even taken at face value the '
            '0-hit chance only moves from 1/705432 to about 1/' + str(int(round(1 / w[0]))),
    'sd_of_mean_n382': sd_mean,
    'min_detectable_shift_holm30_power50': z_holm * sd_mean,
    'min_detectable_shift_holm30_power80': (z_holm + 0.8416) * sd_mean}
json.dump(OUT, open(os.path.join(RUN, 'redteam_stats.json'), 'w'), indent=1, default=lambda o: o.item())
print(json.dumps({k: v for k, v in OUT.items() if k != 'holm'}, indent=1, default=lambda o: o.item()))
print('holm survivors:', OUT['holm']['survivors_holm_p'], OUT['holm']['survivors_holm_le3'],
      'match aggregate:', OUT['holm']['all_match_aggregate_json'])
for r in rows[:6]:
    print(r)
