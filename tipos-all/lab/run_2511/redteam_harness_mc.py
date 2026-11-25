"""Red team, part 1: independent Monte-Carlo check of the harness null (python3 -I -B, numpy, fixed seeds).
(a) hit pmf of a random ticket vs a random draw, simulated as SETS (independent of the closed form);
(b) 20 000 random-ticket runs through the REAL harness.evaluate on the real 412 draws -> p calibration;
(c) MC tail P(sum <= 2049) (A7 R2 observed) with numpy's hypergeometric sampler vs the harness convolution;
(d) exact null for PAST-DEPENDENT rules: A7 R2 (mirror, direction frozen on draws 0..29) and A7 R1 (adaptive
    selection over 88 candidates) on 5 000 synthetic i.i.d. histories; p must be ~uniform (no selection bias).
Writes redteam_harness_mc.json."""
import sys, json, os, time
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2511')
import numpy as np
from math import comb
from harness import evaluate, DRAWS, PMF, P_LOW, _sum_pmf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = {}
n = len(DRAWS) - 30


def ks_uniform(p):
    p = np.sort(np.asarray(p)); m = len(p); i = np.arange(1, m + 1)
    d_plus = float(np.max(i / m - p))        # >0 : more small p than uniform (anti-conservative)
    d_minus = float(np.max(p - (i - 1) / m))  # >0 : fewer small p (conservative)
    return {'D_anticonservative': d_plus, 'D_conservative': d_minus, 'crit_5pct_two_sided': 1.358 / np.sqrt(m)}


def calib(p, alphas=(0.001, 0.005, 0.01, 0.014, 0.05, 0.1, 0.25, 0.5)):
    p = np.asarray(p); m = len(p)
    return {str(a): {'frac_p_le_alpha': float((p <= a).mean()),
                     'mc_se': float(np.sqrt(a * (1 - a) / m))} for a in alphas}


# ---------- (a) pmf of hits, simulated with sets ----------
rng = np.random.default_rng(20261125)
M = 1_000_000
draw = np.argsort(rng.random((M, 22)), axis=1)[:, :11]
tick = np.argsort(rng.random((M, 22)), axis=1)[:, :11]
dm = np.zeros((M, 22), bool); dm[np.arange(M)[:, None], draw] = True
tm = np.zeros((M, 22), bool); tm[np.arange(M)[:, None], tick] = True
hits = (dm & tm).sum(1)
cnt = np.bincount(hits, minlength=12)
exp = M * PMF
mask = exp >= 5
chi2 = float((((cnt - exp) ** 2) / exp)[mask].sum())
OUT['a_pmf_sets'] = {'M': M, 'observed': cnt.tolist(), 'expected': [round(float(e), 1) for e in exp],
                     'chi2': chi2, 'df': int(mask.sum() - 1),
                     'closed_form_numerators': [comb(11, k) * comb(11, 11 - k) for k in range(12)],
                     'pmf_sum': float(PMF.sum()), 'mean_mc': float(hits.mean()), 'var_mc': float(hits.var()),
                     'mean_exact': 5.5, 'var_exact': 11 * 11 * 11 * 11 / (22 * 22 * 21)}
del draw, tick, dm, tm, hits

# ---------- (b) 20 000 random-ticket runs through the real harness ----------
R = 20000
rng = np.random.default_rng(2511)
t0 = time.time()
pm, pl, means = [], [], []
for r in range(R):
    T = np.argsort(rng.random((len(DRAWS), 22)), axis=1)[:, :11] + 1   # one random ticket per draw index
    res = evaluate(lambda past, T=T: T[len(past)], 'random')
    pm.append(res['p_mean_lower']); pl.append(res['p_le3']); means.append(res['mean_hits'])
pm, pl, means = np.array(pm), np.array(pl), np.array(means)
OUT['b_random_ticket_runs'] = {
    'runs': R, 'seconds': round(time.time() - t0, 1), 'n_per_run': n,
    'mean_of_mean_hits': float(means.mean()), 'sd_of_mean_hits': float(means.std()),
    'sd_expected': float(np.sqrt(OUT['a_pmf_sets']['var_exact'] / n)),
    'p_mean_lower': {'calibration': calib(pm), 'ks': ks_uniform(pm), 'mean_p': float(pm.mean())},
    'p_le3': {'calibration': calib(pl), 'ks': ks_uniform(pl), 'mean_p': float(pl.mean()),
              'note': 'binomial count, very discrete -> super-uniform (conservative), as it should be'},
    'frac_runs_min_p_of_30_below_0.014': None}
# how often does the smallest of 30 independent random rules reach p <= 0.0141 (A7 R2)?
g = pm[:(R // 30) * 30].reshape(-1, 30).min(1)
OUT['b_random_ticket_runs']['frac_runs_min_p_of_30_below_0.014'] = {
    'groups_of_30': int(len(g)), 'frac_min_p_le_0.01406': float((g <= 0.014058554460433236).mean()),
    'theory_indep': float(1 - (1 - 0.014058554460433236) ** 30)}

# ---------- (c) tail at the A7 R2 observed sum ----------
S_obs = int(round(5.363874345549738 * n))
sp = _sum_pmf(n)
rng = np.random.default_rng(777)
B = 2_000_000
sums = np.zeros(B, np.int64)
for _ in range(n):
    sums += rng.hypergeometric(11, 11, 11, size=B)
p_mc = float((sums <= S_obs).mean())
var1 = OUT['a_pmf_sets']['var_exact']
z = (S_obs + 0.5 - 5.5 * n) / np.sqrt(n * var1)
from math import erf, sqrt
OUT['c_tail_A7R2'] = {'S_obs': S_obs, 'p_exact_harness': float(sp[:S_obs + 1].sum()), 'p_mc_2e6': p_mc,
                      'mc_se': float(np.sqrt(p_mc * (1 - p_mc) / B)),
                      'p_normal_cc': float(0.5 * (1 + erf(z / sqrt(2)))), 'sum_pmf_total': float(sp.sum()),
                      'sum_pmf_mean': float((np.arange(len(sp)) * sp).sum()) / n}
del sums

# ---------- (d) past-dependent rules on synthetic i.i.d. histories ----------
NS = 5000
rng = np.random.default_rng(4242)
ND = len(DRAWS)
k = np.arange(n + 1)
binom = np.array([comb(n, int(i)) for i in k], float) * P_LOW ** k * (1 - P_LOW) ** (n - k)
# transform family of A7 R1 (0-based maps)
def rot(kk): return [((x - 1 + kk) % 22) for x in range(1, 23)]
def refl(c): return [((c - x) % 22) for x in range(1, 23)]
par = [(x + 1 if x % 2 == 1 else x - 1) - 1 for x in range(1, 23)]
G = np.array([rot(kk) for kk in range(1, 22)] + [refl(c) for c in range(22)] + [par])
pv_r2, pv_r1, pl_r2, pl_r1 = [], [], [], []
XREAL = np.zeros((ND, 22), np.int64)
for i_, d_ in enumerate(DRAWS): XREAL[i_, np.array(d_['main']) - 1] = 1
self_check = {}
for s in range(-1, NS):
    if s < 0:
        X = XREAL                                   # self-check of this re-implementation on the real draws
    else:
        X = np.zeros((ND, 22), np.int64)
        idx = np.argsort(rng.random((ND, 22)), axis=1)[:, :11]
        X[np.arange(ND)[:, None], idx] = 1
    # overlap of image g(D_{u-1}) with D_u for every transform: o[g, u-1]
    o = np.einsum('ux,gux->gu', X[:-1], X[1:][:, G].transpose(1, 0, 2))
    # --- A7 R2: mirror image/complement, direction from u = 1..29
    om = o[21]                                     # refl0 = 23-x is row 21 of G
    m0 = om[:29].mean()
    h2 = om[29:] if m0 <= 5.5 else 11 - om[29:]    # hits at draws t = 30..411
    # --- A7 R1: argmin cumulative score over 88 candidates, ties first in order
    cum = np.cumsum(o, axis=1)                     # cum[g, j] = sum_{u=1..j+1}
    h1 = np.empty(n, np.int64)
    for j, t in enumerate(range(30, ND)):
        sc_img = cum[:, t - 2]                     # transitions u = 1..t-1 inside past
        sc_cmp = 11 * (t - 1) - sc_img
        allsc = np.stack([sc_img, sc_cmp], 1).ravel()   # order (g1,img),(g1,cmp),(g2,img),...
        c = int(np.argmin(allsc)); g_, cmp_ = divmod(c, 2)
        hh = o[g_, t - 1]
        h1[j] = hh if cmp_ == 0 else 11 - hh
    if s < 0:
        self_check = {'A7_R2_mean_reimpl': float(h2.mean()), 'A7_R1_mean_reimpl': float(h1.mean()),
                      'A7_R2_mean_reported': 5.363874345549738, 'A7_R1_mean_reported': 5.390052356020942}
        continue
    for h, pv, pl_ in ((h2, pv_r2, pl_r2), (h1, pv_r1, pl_r1)):
        S = int(h.sum()); pv.append(float(sp[:S + 1].sum()))
        pl_.append(float(binom[int((h <= 3).sum()):].sum()))
OUT['d_past_dependent_null'] = {
    'synthetic_histories': NS, 'reimplementation_check_on_real_draws': self_check,
    'A7_R2_mirror': {'calibration': calib(pv_r2), 'ks': ks_uniform(pv_r2), 'mean_p': float(np.mean(pv_r2))},
    'A7_R1_adaptive88': {'calibration': calib(pv_r1), 'ks': ks_uniform(pv_r1), 'mean_p': float(np.mean(pv_r1))},
    'A7_R1_adaptive88_p_le3': {'calibration': calib(pl_r1), 'ks': ks_uniform(pl_r1)}}

pa = OUT['b_random_ticket_runs']['p_mean_lower']
ok = (abs(OUT['a_pmf_sets']['mean_mc'] - 5.5) < 0.005 and OUT['a_pmf_sets']['chi2'] < 30
      and pa['ks']['D_anticonservative'] < pa['ks']['crit_5pct_two_sided']
      and abs(OUT['c_tail_A7R2']['p_mc_2e6'] - OUT['c_tail_A7R2']['p_exact_harness']) < 4 * OUT['c_tail_A7R2']['mc_se']
      and all(OUT['d_past_dependent_null'][k_]['ks']['D_anticonservative'] < 1.358 / np.sqrt(NS)
              for k_ in ('A7_R2_mirror', 'A7_R1_adaptive88')))
OUT['verdict'] = 'HARNESS OK' if ok else 'HARNESS NOT OK'
json.dump(OUT, open(os.path.join(HERE, 'redteam_harness_mc.json'), 'w'), indent=1)
print(json.dumps(OUT, indent=1))
