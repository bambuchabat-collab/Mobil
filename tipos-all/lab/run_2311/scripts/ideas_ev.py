"""Subagent 5: pre-registered EV hypotheses H1-H8, H10 (see ../ideas_prereg.md) + money effects.
python3 -I ideas_ev.py  -> ../ideas_ev_results.json
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from ideas_common import *

R = int(os.environ.get('IDEAS_R', '1999'))
T0 = 40
d = load_ev()
n, D = d['n'], d['D']
Y = np.column_stack([np.log(d['n3'] / d['bets']), np.log(d['n4'] / d['bets'])])
C = np.column_stack([np.ones(n), d['old'], d['thu'], d['prem'], np.log(d['bets']) - np.log(1e5)])
NUM = ind27(D)
EPS = 1e-8
STRATA = d['old'].astype(int)

# history features for H4 (draw t uses draws < t only)
H4F = np.zeros((n, 3))
for t in range(n):
    prev, jp, hot = history_sets(D, d['top'], t)
    for j, S in enumerate((prev, jp, hot)):
        H4F[t, j] = len(set(D[t]) & S)


def walk(X, pen, Ycols, t0):
    nn, p = X.shape
    XtX = np.zeros((p, p)); XtY = np.zeros((p, Ycols.shape[1])); P = np.diag(pen)
    preds = np.empty((nn - t0, Ycols.shape[1]))
    for t in range(nn):
        if t >= t0:
            preds[t - t0] = X[t] @ np.linalg.solve(XtX + P, XtY)
        XtX += np.outer(X[t], X[t]); XtY += np.outer(X[t], Ycols[t])
    return preds


def fit(X, pen, Ycols):
    return np.linalg.solve(X.T @ X + np.diag(pen), X.T @ Ycols)


def fl_perms(Xred, penred, Yobs, R, seed, strata):
    beta = fit(Xred, penred, Yobs); fitv = Xred @ beta; e = Yobs - fitv
    rng = np.random.default_rng(seed); cols = [Yobs]
    idx0 = np.arange(len(Yobs))
    for _ in range(R):
        idx = idx0.copy()
        for s in np.unique(strata):
            ii = np.where(strata == s)[0]; idx[ii] = rng.permutation(ii)
        cols.append(fitv + e[idx])
    return np.concatenate(cols, axis=1)


def mse_cols(preds, Yall, t0):
    err = preds - Yall[t0:]
    return (err ** 2).mean(0)


def run_test(name, Xred, penred, variants, seed, Yobs=Y, t0=T0, strata=STRATA):
    """variants: list of (label, Xadd, penadd). Returns dict with T_obs per variant, max-T p."""
    t_start = time.time()
    nresp = Yobs.shape[1]
    Yall = fl_perms(Xred, penred, Yobs, R, seed, strata)
    m0 = mse_cols(walk(Xred, penred, Yall, t0), Yall, t0).reshape(R + 1, nresp)
    Ts = []; out = {}
    for lab, Xa, pa in variants:
        X1 = np.column_stack([Xred, Xa]); p1 = np.concatenate([penred, pa])
        m1 = mse_cols(walk(X1, p1, Yall, t0), Yall, t0).reshape(R + 1, nresp)
        T = ((m0 - m1) / m0).sum(1)
        Ts.append(T)
        out[lab] = dict(T_obs=float(T[0]), rel_mse_gain_by_resp=[float(x) for x in ((m0[0] - m1[0]) / m0[0])],
                        p_single=float((1 + (T[1:] >= T[0]).sum()) / (R + 1)))
    Tmax = np.max(np.array(Ts), axis=0)
    p = float((1 + (Tmax[1:] >= Tmax[0]).sum()) / (R + 1))
    best = max(out, key=lambda k: out[k]['T_obs'])
    print(f'{name}: Tmax={Tmax[0]:.4f} p={p:.4f} best={best} null_mean={Tmax[1:].mean():.4f} '
          f'({time.time() - t_start:.0f}s)', flush=True)
    return dict(T_max_obs=float(Tmax[0]), p=p, best_variant=best, variants=out,
                null_Tmax_mean=float(Tmax[1:].mean()), null_Tmax_q95=float(np.quantile(Tmax[1:], 0.95)),
                mse_reduced_obs=[float(x) for x in m0[0]], R=R, seed=seed)


pen0 = np.array([EPS] * 5 + [2.0] * 27)
X0 = np.column_stack([C, NUM])
cons = f_consec(D)[:, None]
res = {}
SPEC = {}

# H1
SPEC['H1'] = (X0, pen0, [('consec_pairs', cons, np.array([EPS]))])
# H2 (reduced = M0 + consecutive pairs)
X0c = np.column_stack([X0, cons]); pen0c = np.concatenate([pen0, [EPS]])
v2 = []
for w in (5, 6, 7, 9, 10):
    v2.append((f'row_w{w}', f_row(D, w)[:, None], np.array([EPS])))
    v2.append((f'col_w{w}', f_col(D, w)[:, None], np.array([EPS])))
SPEC['H2'] = (X0c, pen0c, v2)
SPEC['H3'] = (X0, pen0, [('low12_pairs', f_lowpairs(D)[:, None], np.array([EPS]))])
SPEC['H4'] = (X0, pen0, [('overlap_prev', H4F[:, [0]], np.array([EPS])),
                         ('overlap_last_jackpot', H4F[:, [1]], np.array([EPS])),
                         ('overlap_hot6_last10', H4F[:, [2]], np.array([EPS]))])
SPEC['H5'] = (X0, pen0, [('sd_numbers', f_sd(D)[:, None], np.array([EPS]))])
SPEC['H6'] = (X0, pen0, [('ap3_count', f_ap3(D)[:, None], np.array([EPS])),
                         ('mult5_pairs', f_m5pairs(D)[:, None], np.array([EPS]))])
SPEC['H7'] = (X0, pen0, [('thursday_x_number', NUM * d['thu'][:, None], np.array([4.0] * 27))])
SPEC['H8'] = (X0, pen0, [('premium_x_number', NUM * d['prem'][:, None], np.array([4.0] * 27))])

for i, h in enumerate(['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8']):
    Xr, pr, var = SPEC[h]
    res[h] = run_test(h, Xr, pr, var, 20261123 + int(h[1:]))

# H10: main-extra coupling, new era only
new = np.where(d['old'] == 0)[0]
ev = d['ev']
tw = lambda dd, k: dd['tiers'].get(k, [0.0, 0])[1]
U = np.array([[np.log(max(tw(ev[t], '3+1'), 0.5) / max(tw(ev[t], '3+0'), 0.5)),
               np.log(max(tw(ev[t], '4+1'), 0.5) / max(tw(ev[t], '4+0'), 0.5))] for t in new])
PB = np.zeros((len(new), 7)); PB[np.arange(len(new)), d['pb'][new] - 1] = 1
Xu = np.column_stack([np.ones(len(new)), d['thu'][new], d['prem'][new], PB])
penu = np.array([EPS] * 3 + [2.0] * 7)
coup = np.array([float(d['pb'][t] in set(D[t])) for t in new])[:, None]
res['H10'] = run_test('H10', Xu, penu, [('extra_in_main', coup, np.array([EPS]))], 20261133, Yobs=U, t0=30,
                      strata=np.zeros(len(new), dtype=int))
res['H10']['n_draws'] = int(len(new)); res['H10']['n_eval'] = int(len(new) - 30)
res['H10']['share_extra_in_main_obs'] = float(coup.mean()); res['H10']['share_expected'] = 6 / 27

# ---------------- full-sample coefficients (descriptive) ----------------
coef = {}
for h in ['H1', 'H2', 'H3', 'H4', 'H5', 'H6']:
    Xr, pr, var = SPEC[h]
    lab = res[h]['best_variant']
    Xa = [v for v in var if v[0] == lab][0]
    b = fit(np.column_stack([Xr, Xa[1]]), np.concatenate([pr, Xa[2]]), Y)
    coef[h] = dict(feature=lab, gamma_y3=float(b[-1, 0]), gamma_y4=float(b[-1, 1]))
b = fit(np.column_stack([Xu, coup]), np.concatenate([penu, [EPS]]), U)
coef['H10'] = dict(feature='extra_in_main', delta_u3=float(b[-1, 0]), delta_u4=float(b[-1, 1]))
res['coefficients_full_sample'] = coef

# ---------------- money effects (pre-registered method) ----------------
if os.environ.get('IDEAS_MONEY', '1') == '0':
    json.dump(res, open(os.path.join(BASE, 'ideas_ev_results_smoke.json'), 'w'), indent=1); sys.exit(0)
COMB = all_combos()
MEM = ind27(COMB).astype(np.int8)
S3 = (EV_SHARE['3+0'] + EV_SHARE['3+1']) * EV_FUND
S4 = (EV_SHARE['4+0'] + EV_SHARE['4+1']) * EV_FUND
S5 = (EV_SHARE['5+0'] + EV_SHARE['5+1']) * EV_FUND
from math import comb as nCk
CNT = np.array([nCk(6, k) * nCk(21, 6 - k) for k in range(7)], dtype=float)


def combo_features(h, lab):
    """feature column for all 296010 combos at the target draw (Monday 23.11.2026, history = all 170 draws)."""
    if lab == 'consec_pairs': return f_consec(COMB)
    if lab.startswith('row_w'): return f_row(COMB, int(lab[5:]))
    if lab.startswith('col_w'): return f_col(COMB, int(lab[5:]))
    if lab == 'low12_pairs': return f_lowpairs(COMB)
    if lab == 'sd_numbers': return f_sd(COMB.astype(float))
    if lab == 'ap3_count': return f_ap3(COMB)
    if lab == 'mult5_pairs': return f_m5pairs(COMB)
    if lab.startswith('overlap_'):
        prev, jp, hot = history_sets(D, d['top'], n)
        S = {'overlap_prev': prev, 'overlap_last_jackpot': jp, 'overlap_hot6_last10': hot}[lab]
        return f_overlap(COMB, S)
    raise KeyError(lab)


def logpop(beta_num, extra_cols=(), extra_coef=()):
    f = MEM.astype(np.float32) @ beta_num.astype(np.float32)
    f = f.astype(float)
    for col, g in zip(extra_cols, extra_coef):
        f = f + g * col
    return f - np.log(np.mean(np.exp(f)))


class Field:
    def __init__(self, f3, f4):
        self.w3 = np.exp(-f3); self.w4 = np.exp(-f4)

    def ret_from_h(self, hvec):
        s3 = np.bincount(hvec, weights=self.w3, minlength=7)
        s4 = np.bincount(hvec, weights=self.w4, minlength=7)
        return S3 * s3[3] / CNT[3] + S4 * s4[4] / CNT[4] + S5 * s4[5] / CNT[5]

    def ret(self, T):
        return self.ret_from_h(MEM[:, np.array(sorted(T)) - 1].sum(1).astype(np.int64))


def field_ok(F):
    """post-hoc support constraint: <= 2 consecutive pairs and no run of 3 (draw data rarely go beyond)."""
    F = sorted(F); dif = np.diff(F)
    if (dif == 1).sum() > 2: return False
    return not any(dif[i] == 1 and dif[i + 1] == 1 for i in range(len(dif) - 1))


def optimise(model, seed, starts=5, constrained=False):
    rng = np.random.default_rng(seed)
    inits = [] if constrained else [([14, 15, 20, 18, 16, 1], [2, 10, 23, 22, 24, 4])]
    while len(inits) < starts:
        p = rng.permutation(np.arange(1, 28)); A0, B0 = list(p[:6]), list(p[6:12])
        if constrained and not (field_ok(A0) and field_ok(B0)): continue
        inits.append((A0, B0))
    best = None
    for A, B in inits:
        A, B = [int(x) for x in A], [int(x) for x in B]
        cur = model.ret(A) + model.ret(B)
        while True:
            used = set(A) | set(B); free = [x for x in range(1, 28) if x not in used]
            bestmove = None; bestval = cur
            for which in (0, 1):
                F = A if which == 0 else B; other = B if which == 0 else A
                hF = MEM[:, np.array(F) - 1].sum(1).astype(np.int64)
                rother = model.ret(other)
                for i, out in enumerate(F):
                    for inn in free:
                        if constrained and not field_ok(F[:i] + [inn] + F[i + 1:]): continue
                        h2 = hF - MEM[:, out - 1] + MEM[:, inn - 1]
                        v = model.ret_from_h(h2) + rother
                        if v > bestval + 1e-12:
                            bestval = v; bestmove = (which, i, inn)
            if bestmove is None: break
            which, i, inn = bestmove
            (A if which == 0 else B)[i] = inn; cur = bestval
        if best is None or cur > best[0]:
            best = (float(cur), sorted(A), sorted(B))
    return best


bfull0 = fit(X0, pen0, Y)
f0_3 = logpop(bfull0[5:32, 0]); f0_4 = logpop(bfull0[5:32, 1])
M_red0 = Field(f0_3, f0_4)
money = {}
best0 = optimise(M_red0, 7)
money['baseline_M0'] = dict(best_pair=[best0[1], best0[2]], return_per_eur=best0[0] / 2,
                            uniform_return=S3 + S4 + S5)
print('M0 best', best0, flush=True)

for h in ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8']:
    Xr, pr, var = SPEC[h]
    lab = res[h]['best_variant']
    Xa = [v for v in var if v[0] == lab][0]
    br = fit(Xr, pr, Y)
    bf = fit(np.column_stack([Xr, Xa[1]]), np.concatenate([pr, Xa[2]]), Y)
    if h in ('H7', 'H8'):
        # target = Monday, non-premium: interaction block is zero; Monday profile = main effects of full model
        fr = [logpop(br[5:32, r]) for r in (0, 1)]
        ff = [logpop(bf[5:32, r]) for r in (0, 1)]
        # descriptive: profile for the interaction population (Thursday / premium)
        fi = [logpop(bf[5:32, r] + bf[-27:, r]) for r in (0, 1)]
    else:
        red_extra = [(f_consec(COMB), 32)] if h == 'H2' else []
        colf = combo_features(h, lab)
        fr = [logpop(br[5:32, r], [c for c, _ in red_extra], [br[j, r] for _, j in red_extra]) for r in (0, 1)]
        ff = [logpop(bf[5:32, r], [c for c, _ in red_extra] + [colf],
                     [bf[j, r] for _, j in red_extra] + [bf[-1, r]]) for r in (0, 1)]
    Mr, Mf = Field(*fr), Field(*ff)
    br_best = optimise(Mr, 11); bf_best = optimise(Mf, 13)
    val_red_under_full = Mf.ret(br_best[1]) + Mf.ret(br_best[2])
    eff = 100 * (bf_best[0] - val_red_under_full) / 2
    money[h] = dict(variant=lab, best_pair_full=[bf_best[1], bf_best[2]], best_pair_reduced=[br_best[1], br_best[2]],
                    ret_full_best=bf_best[0] / 2, ret_full_of_reduced_best=val_red_under_full / 2,
                    effect_pp_per_eur=eff, ticket_changes=[br_best[1], br_best[2]] != [bf_best[1], bf_best[2]])
    if h in ('H7', 'H8'):
        Mi = Field(*fi); bi = optimise(Mi, 17)
        money[h]['other_population_best_pair'] = [bi[1], bi[2]]
        money[h]['other_population_gain_pp_vs_monday_ticket'] = 100 * (bi[0] - (Mi.ret(bf_best[1]) + Mi.ret(bf_best[2]))) / 2
    print(h, money[h], flush=True)

# H10 money: +1 tiers, extra number inside vs outside own main field
d3, d4 = coef['H10']['delta_u3'], coef['H10']['delta_u4']
q = 6 / 27
def plus1_ret(inside, delta, k):
    pin = k / 6 if inside else (6 - k) / 21
    norm = (1 - q) + q * np.exp(delta)
    return pin * np.exp(-delta) * norm + (1 - pin) * norm
s1 = {3: EV_SHARE['3+1'] * EV_FUND, 4: EV_SHARE['4+1'] * EV_FUND, 5: EV_SHARE['5+1'] * EV_FUND}
ins = sum(s1[k] * plus1_ret(True, d3 if k == 3 else d4, k) for k in (3, 4, 5))
outs = sum(s1[k] * plus1_ret(False, d3 if k == 3 else d4, k) for k in (3, 4, 5))
money['H10'] = dict(ret_plus1_inside=ins, ret_plus1_outside=outs, effect_pp_per_eur=100 * abs(ins - outs),
                    better='extra outside own field' if outs > ins else 'extra inside own field')
print('H10', money['H10'])

# ---- POST-HOC (not pre-registered): H1 money effect restricted to the data support ----
Xr, pr, var = SPEC['H1']
br = fit(Xr, pr, Y); bf = fit(np.column_stack([Xr, cons]), np.concatenate([pr, [EPS]]), Y)
cc = f_consec(COMB)
Mr = Field(logpop(br[5:32, 0]), logpop(br[5:32, 1]))
Mf = Field(logpop(bf[5:32, 0], [cc], [bf[-1, 0]]), logpop(bf[5:32, 1], [cc], [bf[-1, 1]]))
rb = optimise(Mr, 21, constrained=True); fb = optimise(Mf, 23, constrained=True)
money['H1_posthoc_constrained'] = dict(
    constraint='each field <= 2 consecutive pairs, no run of 3', best_pair_full=[fb[1], fb[2]],
    best_pair_reduced=[rb[1], rb[2]], ret_full_best=fb[0] / 2,
    ret_full_of_reduced_best=(Mf.ret(rb[1]) + Mf.ret(rb[2])) / 2,
    effect_pp_per_eur=100 * (fb[0] - (Mf.ret(rb[1]) + Mf.ret(rb[2]))) / 2,
    gain_vs_uniform_pp=100 * (fb[0] / 2 - (S3 + S4 + S5)),
    gamma_consec_y3=float(bf[-1, 0]), gamma_consec_y4=float(bf[-1, 1]))
print('H1 posthoc', money['H1_posthoc_constrained'], flush=True)
res['money'] = money
json.dump(res, open(os.path.join(BASE, 'ideas_ev_results.json'), 'w'), indent=1)
print('saved')
