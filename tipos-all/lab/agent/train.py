"""Discovery / tuning on TRAINING data only (2018-01-03..2023-12-31). Never loads holdout rows."""
import sys, json, math, time
sys.path.insert(0, "/tmp/claude-0/-home-user-Mobil/b5a09aa0-3ae1-547d-aca0-e9005dcfc1f6/scratchpad/agent_lab")
import numpy as np
from lab_common import load, ordered, indicator, shuffle_within, random_draws, mc_p, corr, LAB, N, K
import lab_stats as S

R = 4000
rng = np.random.default_rng(20261105)
rows = load("train")
assert max(r["date"] for r in rows).isoformat() <= "2023-12-31"
B = ordered(rows)
X = indicator(B)
nd = len(rows)
ctx = S.context(rows)
out = {"n_train_draws": nd}
t0 = time.time()


def two_sided_normal(z):
    return math.erfc(abs(z) / math.sqrt(2))


def mc_shuffle(fn, reps=R):
    return np.array([fn(shuffle_within(B, rng)) for _ in range(reps)])


def mc_uniform(fn, reps=R):
    return np.array([fn(random_draws(nd, rng)) for _ in range(reps)])


def mc_perm(fn, lab, reps=R):
    return np.array([fn(rng.permutation(lab)) for _ in range(reps)])


res = {}
# H01
obs = S.s_pos_chi2(B); null = mc_shuffle(S.s_pos_chi2)
res["H01"] = dict(effect=f"chi2={obs:.1f} (null mean {null.mean():.1f})", stat=obs, p=mc_p(obs, null, "greater"),
                  resid=S.pos_resid(B).tolist())
# H02
obs = S.s_meanpos(B); null = mc_shuffle(S.s_meanpos)
m, Nn = S.meanpos(B)
res["H02"] = dict(effect=f"S={obs:.1f} (null mean {null.mean():.1f}); earliest={np.argsort(m)[:5]+1}; latest={np.argsort(-m)[:5]+1}",
                  stat=obs, p=mc_p(obs, null, "greater"), meanpos=m.tolist())
# H03
obs = S.s_early_freq(B); null = mc_shuffle(S.s_early_freq)
res["H03"] = dict(effect=f"corr(meanpos,freq)={obs:+.3f}", stat=obs, p=mc_p(obs, null), sign=float(np.sign(obs)))
# H04a
z = S.z_single_count(B)
res["H04a"] = dict(effect=f"z={z:+.2f} (count {S.s_single_count(B):.0f} vs exp {nd*5*9/35:.1f})", stat=z, p=two_sided_normal(z), sign=float(np.sign(z)))
# H04b
obs = S.s_single_pos(B); null = mc_shuffle(S.s_single_pos)
res["H04b"] = dict(effect=f"mean pos of 1-9 = {obs:.3f} (null 3.000)", stat=obs, p=mc_p(obs, null), sign=float(np.sign(obs - null.mean())))
# H05a
obs = S.s_ink_freq(B); null = mc_uniform(S.s_ink_freq)
res["H05a"] = dict(effect=f"corr(ink,freq)={obs:+.3f}", stat=obs, p=mc_p(obs, null), sign=float(np.sign(obs)))
# H05b
obs = S.s_ink_pos(B); null = mc_shuffle(S.s_ink_pos)
res["H05b"] = dict(effect=f"corr(ink,meanpos)={obs:+.3f}", stat=obs, p=mc_p(obs, null), sign=float(np.sign(obs)))
# H06a
obs = S.s_seqdist(B); null = mc_shuffle(S.s_seqdist)
res["H06a"] = dict(effect=f"mean |b(k+1)-b(k)|={obs:.3f} (null {null.mean():.3f})", stat=obs, p=mc_p(obs, null), sign=float(np.sign(obs - null.mean())))
# H06b
Cc = S.cooc(B)
obs = S.s_trans_chi2(B, Cc); null = mc_shuffle(lambda b: S.s_trans_chi2(b, Cc), 2000)
res["H06b"] = dict(effect=f"chi2={obs:.1f} (null mean {null.mean():.1f})", stat=obs, p=mc_p(obs, null, "greater"), resid=S.trans_resid(B).tolist())
# H07a
obs = S.s_consec(B); null = mc_uniform(S.s_consec)
res["H07a"] = dict(effect=f"consecutive pairs={obs:.0f} (null {null.mean():.1f})", stat=obs, p=mc_p(obs, null), sign=float(np.sign(obs - null.mean())))
# H07b
obs = S.s_range(B); null = mc_uniform(S.s_range)
res["H07b"] = dict(effect=f"mean range={obs:.3f} (null {null.mean():.3f})", stat=obs, p=mc_p(obs, null), sign=float(np.sign(obs - null.mean())))
# H08 weekday (Wed=2 vs Sun=6)
mws = np.isin(ctx["wd"], [2, 6]); Bw = B[mws]; lw = ctx["wd"][mws]
obs = S.chi2_homog(Bw, lw); null = mc_perm(lambda l: S.chi2_homog(Bw, l), lw)
res["H08"] = dict(effect=f"chi2={obs:.1f} df=34 (null mean {null.mean():.1f})", stat=obs, p=mc_p(obs, null, "greater"), diff=S.diff2(Bw, lw, 2, 6).tolist())
# H09a year
obs = S.chi2_homog(B, ctx["year"]); null = mc_perm(lambda l: S.chi2_homog(B, l), ctx["year"])
res["H09a"] = dict(effect=f"chi2={obs:.1f} df=170 (null mean {null.mean():.1f})", stat=obs, p=mc_p(obs, null, "greater"))
# H09b persistence
obs = S.s_split_persist(B); null = mc_uniform(S.s_split_persist)
res["H09b"] = dict(effect=f"split-half corr of freq deviations={obs:+.3f}", stat=obs, p=mc_p(obs, null, "greater"), dev=S.freq_dev(B).tolist())
# H10 season
obs = S.chi2_homog(B, ctx["season"]); null = mc_perm(lambda l: S.chi2_homog(B, l), ctx["season"])
res["H10"] = dict(effect=f"chi2={obs:.1f} df=102 (null mean {null.mean():.1f})", stat=obs, p=mc_p(obs, null, "greater"),
                  resid=S.homog_resid(B, ctx["season"], [0, 1, 2, 3]).tolist())
# H11 temperature vs ink
obs = S.s_temp_ink(B, ctx["temp"]); null = mc_perm(lambda l: S.s_temp_ink(B, l), ctx["temp"])
res["H11"] = dict(effect=f"corr(temp proxy, mean ink)={obs:+.3f}", stat=obs, p=mc_p(obs, null), sign=float(np.sign(obs)))
# H12 sales
obs = S.chi2_homog(B, ctx["hi_sales"]); null = mc_perm(lambda l: S.chi2_homog(B, l), ctx["hi_sales"])
res["H12"] = dict(effect=f"chi2={obs:.1f} df=34 (null mean {null.mean():.1f})", stat=obs, p=mc_p(obs, null, "greater"),
                  diff=S.diff2(B, ctx["hi_sales"], 1, 0).tolist())
# H13a moon quarter
obs = S.chi2_homog(B, ctx["moonq"]); null = mc_perm(lambda l: S.chi2_homog(B, l), ctx["moonq"])
res["H13a"] = dict(effect=f"chi2={obs:.1f} df=102 (null mean {null.mean():.1f})", stat=obs, p=mc_p(obs, null, "greater"),
                   resid=S.homog_resid(B, ctx["moonq"], [0, 1, 2, 3]).tolist())
# H13b illumination vs sum
obs = S.s_illum_sum(B, ctx["illum"]); null = mc_perm(lambda l: S.s_illum_sum(B, l), ctx["illum"])
res["H13b"] = dict(effect=f"corr(illumination, sum)={obs:+.3f}", stat=obs, p=mc_p(obs, null), sign=float(np.sign(obs)))
# H14a numerology
z, ex = S.z_droot(B, ctx["droot"])
res["H14a"] = dict(effect=f"excess matches={ex:+.1f}, z={z:+.2f}", stat=z, p=two_sided_normal(z), sign=float(np.sign(z)))
# H14b day of month
z, ex = S.z_dom(B, ctx["dom"])
res["H14b"] = dict(effect=f"excess draws containing day-of-month={ex:+.1f}, z={z:+.2f}", stat=z, p=two_sided_normal(z), sign=float(np.sign(z)))
# H15 joker
z, ex = S.z_joker(B, ctx["joker"])
res["H15"] = dict(effect=f"excess last-digit matches={ex:+.1f}, z={z:+.2f}", stat=z, p=two_sided_normal(z), sign=float(np.sign(z)))
print("basic tests done", round(time.time() - t0, 1), "s", flush=True)

# H16 latent ball-set mixture (parametric bootstrap)
def lrt(Xm, r):
    l1 = S.fit_cb_mixture(Xm, 1, r, iters=40, restarts=1)
    l2 = S.fit_cb_mixture(Xm, 2, r, iters=80, restarts=3)
    return l2[0] - l1[0], l2

obs, fit2 = lrt(X, rng)
nullL = []
for b in range(300):
    nullL.append(lrt(indicator(random_draws(nd, rng)), rng)[0])
nullL = np.array(nullL)
res["H16"] = dict(effect=f"LRT 2 vs 1 comp = {obs:.2f} (null mean {nullL.mean():.2f}), pi={np.round(fit2[2],3).tolist()}",
                  stat=float(obs), p=mc_p(obs, nullL, "greater"), lt=fit2[1].tolist(), pi=fit2[2].tolist())
print("H16 done", round(time.time() - t0, 1), "s", flush=True)

# M1 Dirichlet forgetting: tune (half-life, beta) by walk-forward Bernoulli log-score on train (t>=104)
START = 104
halves = [3, 5, 10, 20, 40, 80, 160, 320, None]
betas = [-0.4, -0.2, -0.1, -0.05, 0.05, 0.1, 0.2, 0.4]
grid = []
for h in halves:
    Sc = S.disc_scores(X, h)
    for b in betas:
        ls = S.bern_logscore(X[START:], S.tilt_probs(Sc[START:], b)).mean()
        grid.append((ls, h, b))
base_ls = S.bern_logscore(X[START:], np.full((nd - START, N), K / N)).mean()
best = max(grid, key=lambda g: g[0])
Sc = S.disc_scores(X, best[1])
hh = [S.hits(S.top5(best[2] * Sc[t], rng), B[t]) for t in range(START, nd)]
res["M1"] = dict(effect=f"tuned half-life={best[1]}, beta={best[2]}; train walk-forward logscore gain={best[0]-base_ls:+.4f} nats/draw; train hits={np.mean(hh):.4f}",
                 stat=S.hits_z(hh), p=two_sided_normal(S.hits_z(hh)), half=best[1], beta=best[2], train_hits=float(np.mean(hh)))

# M2 Plackett-Luce: tune alpha by walk-forward ordered log-score on train
alphas = [1, 5, 20, 50, 200, 1000]
m2 = []
for a in alphas:
    w = None; ls = []; hm = []
    for t in range(START, nd):
        w = S.pl_fit(B[:t], a, w, iters=60 if w is None else 15)
        ls.append(S.pl_logscore(B[t:t + 1], w)[0] - S.LOG_UNIF_ORD)
        hm.append(S.hits(S.top5(w, rng), B[t]))
    m2.append((float(np.mean(ls)), a, hm))
    print("  PL alpha", a, "logscore gain", round(np.mean(ls), 4), "hits", round(np.mean(hm), 4), flush=True)
bm2 = max(m2, key=lambda g: g[0])
wfull = S.pl_fit(B, bm2[1], iters=200)
res["M2"] = dict(effect=f"tuned alpha={bm2[1]}; train walk-forward ordered logscore gain={bm2[0]:+.4f} nats/draw; train hits={np.mean(bm2[2]):.4f}; top weights={(np.argsort(-wfull)[:5]+1).tolist()}",
                 stat=S.hits_z(bm2[2]), p=two_sided_normal(S.hits_z(bm2[2])), alpha=bm2[1], train_hits=float(np.mean(bm2[2])),
                 w_train=wfull.tolist())
print("M done", round(time.time() - t0, 1), "s", flush=True)

# P1 popularity: ridge of log(W3/deposits) on number indicators + year dummies
y = np.log(np.array([r["w3"] for r in rows]) / np.array([r["deposits"] for r in rows]))
years = ctx["year"]; uy = np.unique(years)
Y = np.stack([(years == u).astype(float) for u in uy], 1)


def ridge_beta(Xn, y, lam=1.0):
    D = np.hstack([Xn, Y])
    P = np.diag(np.r_[np.full(N, lam), np.full(len(uy), 1e-6)])
    coef = np.linalg.solve(D.T @ D + P, D.T @ y)
    b = coef[:N]
    return b - b.mean(), coef


def r2_numbers(Xn, y):
    b, coef = ridge_beta(Xn, y)
    yd = y - Y @ np.linalg.lstsq(Y, y, rcond=None)[0]
    pred = Xn @ b
    return corr(pred, yd) ** 2


obs = r2_numbers(X, y)
null = []
for _ in range(1000):
    Xp = X.copy()
    for u in uy:
        idx = np.where(years == u)[0]
        Xp[idx] = X[rng.permutation(idx)]
    null.append(r2_numbers(Xp, y))
bpop, _ = ridge_beta(X, y)
res["P1"] = dict(effect=f"in-sample R2 of numbers on year-demeaned log(W3/dep)={obs:.3f} (null {np.mean(null):.3f}); least popular={(np.argsort(bpop)[:8]+1).tolist()}; most popular={(np.argsort(-bpop)[:8]+1).tolist()}",
                 stat=obs, p=mc_p(obs, np.array(null), "greater"), beta=bpop.tolist())

out["results"] = res
json.dump(out, open(LAB + "/train_results.json", "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
for k, v in res.items():
    print(f"{k:5s} p={v['p']:.4f}  {v['effect']}")
print("total", round(time.time() - t0, 1), "s")
