"""Round 2: consecutive-pair and repeat-from-previous terms in the popularity model; 5-field portfolio."""
import sys, json, math, itertools
sys.path.insert(0, "/tmp/claude-0/-home-user-Mobil/b5a09aa0-3ae1-547d-aca0-e9005dcfc1f6/scratchpad/agent_lab")
import numpy as np
from lab_common import load, ordered, indicator, corr, LAB, N, K

rng = np.random.default_rng(11)
rows = load("all"); B = ordered(rows); X = indicator(B); nd = len(B)
years = np.array([r["date"].year for r in rows]); uy = np.unique(years)
Y = np.stack([(years == u).astype(float) for u in uy], 1)
y = np.log(np.array([r["w3"] for r in rows]) / np.array([r["deposits"] for r in rows]))
Ssort = np.sort(B, 1)
consec = (np.diff(Ssort, 1) == 1).sum(1).astype(float)
rep = np.r_[0, [len(set(B[t]) & set(B[t - 1])) for t in range(1, nd)]].astype(float)
tm = years <= 2023; hm = ~tm


def fit(mask, extra, lam=1.0):
    Yd = Y[mask][:, np.isin(uy, np.unique(years[mask]))]
    D = np.hstack([X[mask], extra[mask], Yd])
    P = np.diag(np.r_[np.full(N, lam), np.full(extra.shape[1], 1e-6), np.full(Yd.shape[1], 1e-6)])
    c = np.linalg.solve(D.T @ D + P, D.T @ y[mask])
    b = c[:N] - c[:N].mean()
    e = c[N:N + extra.shape[1]]
    resid = y[mask] - D @ c
    se = np.sqrt(np.diag(np.linalg.inv(D.T @ D + P)) * resid.var())[N:N + extra.shape[1]]
    return b, e, se


def demean(v, mask):
    v = v.copy()
    for u in np.unique(years[mask]):
        m = years[mask] == u; v[m] -= v[m].mean()
    return v


E2 = np.stack([consec, rep], 1)
out = {}
b_tr, e_tr, se_tr = fit(tm, E2)
b_ho, e_ho, se_ho = fit(hm, E2)
out["train_coef"] = dict(consec=[round(e_tr[0], 4), round(se_tr[0], 4)], repeat_prev=[round(e_tr[1], 4), round(se_tr[1], 4)])
out["holdout_only_coef"] = dict(consec=[round(e_ho[0], 4), round(se_ho[0], 4)], repeat_prev=[round(e_ho[1], 4), round(se_ho[1], 4)])
# predictive holdout check: train-fitted models with/without extra terms
b0, _, _ = fit(tm, np.zeros((nd, 0)))
act = demean(y[hm], hm)
p0 = X[hm] @ b0
p1 = X[hm] @ b_tr + E2[hm] @ e_tr
# one-sided permutation test of the extra terms: permute their holdout values
gain = corr(p1, act) - corr(p0, act)
null = []
for _ in range(4000):
    Ep = E2[hm][rng.permutation(hm.sum())]
    null.append(corr(X[hm] @ b_tr + Ep @ e_tr, act) - corr(p0, act))
out["holdout_corr_numbers_only"] = round(corr(p0, act), 4)
out["holdout_corr_with_consec_repeat"] = round(corr(p1, act), 4)
out["holdout_gain_p_one_sided"] = round(float((1 + np.sum(np.array(null) >= gain)) / 4001), 4)
for j, nm in enumerate(["consec", "repeat_prev"]):
    r0 = act - np.polyval(np.polyfit(p0, act, 1), p0)
    c = corr(E2[hm][:, j], r0)
    nl = np.array([corr(rng.permutation(E2[hm][:, j]), r0) for _ in range(4000)])
    side = np.sign(e_tr[j])
    out[f"holdout_partial_corr_{nm}"] = [round(c, 4), round(float((1 + np.sum(side * nl >= side * c)) / 4001), 4)]

# final model on all data
b_all, e_all, se_all = fit(np.ones(nd, bool), E2)
out["all_data_coef"] = dict(consec=[round(e_all[0], 4), round(se_all[0], 4)], repeat_prev=[round(e_all[1], 4), round(se_all[1], 4)])
prev = set(B[-1].tolist())  # 2026-11-04 draw, players may copy it on 6.11
combs = np.array(list(itertools.combinations(range(1, N + 1), K)))
d = np.diff(combs, 1)
cc = (d == 1).sum(1); run3 = ((d[:, :-1] == 1) & (d[:, 1:] == 1)).any(1); ap = (d == d[:, :1]).all(1)
prevmask = np.zeros(N + 1); prevmask[list(prev)] = 1
repc = prevmask[combs].sum(1)


def score(c_arr, use_extra=True):
    s = b_all[c_arr - 1].sum(-1)
    if use_extra:
        dd = np.diff(np.sort(c_arr, -1), axis=-1)
        s = s + e_all[0] * (dd == 1).sum(-1) + e_all[1] * prevmask[c_arr].sum(-1)
    return s


s_all = score(combs)
lse = lambda v: v.max() + math.log(np.exp(v - v.max()).mean())
norm = lse(s_all)
factor = lambda c: float(math.exp(score(np.array(c)) - norm))
ok = ~run3 & ~ap
best = combs[ok][np.argmin(s_all[ok])]
ok_noconsec = (cc == 0) & ~ap
best_nc = combs[ok_noconsec][np.argmin(s_all[ok_noconsec])]
out["prev_draw_2026_11_04"] = sorted(prev)
out["best_single_consec_allowed"] = dict(set=best.tolist(), factor=round(factor(best), 3))
out["best_single_no_consec"] = dict(set=best_nc.tolist(), factor=round(factor(best_nc), 3))
out["old_pick_1_18_30_32_35"] = round(factor([1, 18, 30, 32, 35]), 3)

# ---- 5 fields ----
coord = [[1, 14, 20, 26, 31], [2, 15, 22, 27, 32], [6, 16, 23, 28, 33], [10, 17, 24, 29, 34], [12, 18, 25, 30, 35]]
Xall = np.zeros((len(combs), N + 1), bool); Xall[np.arange(len(combs))[:, None], combs] = True


def p_any3(fields):
    h = np.stack([Xall[:, f].sum(1) for f in fields], 1)
    return float((h.max(1) >= 3).mean())


out["coordinator_fields"] = dict(factors=[round(factor(f), 3) for f in coord], mean_factor=round(np.mean([factor(f) for f in coord]), 3),
                                  sum_log_factor=round(sum(math.log(factor(f)) for f in coord), 3), p_any_ge3=round(p_any3(coord), 5))
# overlap check: best 5 fields sharing one number
ov = [coord[0], coord[1], coord[2], coord[3], [12, 18, 25, 30, 1]]
out["p_any_ge3_if_one_number_shared"] = round(p_any3(ov), 5)

# Disjoint fields are required for P>=6.9%; partition the 25 least-popular numbers to minimise sum of log factors.
pool = sorted((np.argsort(b_all)[:25] + 1).tolist())
out["pool_25_least_popular"] = pool
# local search over partitions (swap moves), objective = sum of field scores, fields must avoid run3 and AP


def valid(f):
    f = sorted(f); dd = np.diff(f)
    return not (((dd[:-1] == 1) & (dd[1:] == 1)).any() or (dd == dd[0]).all())


def obj(P):
    return sum(score(np.array(f)) for f in P) if all(valid(f) for f in P) else 1e9


best_P, best_o = None, 1e9
for restart in range(60):
    perm = rng.permutation(pool).tolist(); P = [perm[i * 5:(i + 1) * 5] for i in range(5)]
    o = obj(P)
    improved = True
    while improved:
        improved = False
        for i in range(5):
            for j in range(i + 1, 5):
                for a in range(5):
                    for bb in range(5):
                        Q = [f[:] for f in P]; Q[i][a], Q[j][bb] = P[j][bb], P[i][a]
                        oq = obj(Q)
                        if oq < o - 1e-12:
                            P, o, improved = Q, oq, True
    if o < best_o:
        best_P, best_o = [sorted(f) for f in P], o
best_P = sorted(best_P)
out["proposed_fields"] = dict(fields=best_P, factors=[round(factor(f), 3) for f in best_P], mean_factor=round(np.mean([factor(f) for f in best_P]), 3),
                              sum_log_factor=round(sum(math.log(factor(f)) for f in best_P), 3), p_any_ge3=round(p_any3(best_P), 5))
json.dump(out, open(LAB + "/round2.json", "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
