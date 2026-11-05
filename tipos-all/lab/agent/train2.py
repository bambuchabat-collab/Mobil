"""Training-only tests for amendment 1 (H17a, H17b, H18). Appends to train_results.json."""
import sys, json, math
sys.path.insert(0, "/tmp/claude-0/-home-user-Mobil/b5a09aa0-3ae1-547d-aca0-e9005dcfc1f6/scratchpad/agent_lab")
import numpy as np
from lab_common import load, ordered, indicator, shuffle_within, random_draws, mc_p, corr, LAB, N, K
import lab_stats as S

rng = np.random.default_rng(777)
rows = load("train")
B = ordered(rows); X = indicator(B); nd = len(B)
tr = json.load(open(LAB + "/train_results.json"))
res = tr["results"]


def carry(Bc):
    """returns (mean pos in t of repeated numbers, corr(pos t-1, pos t))"""
    pp, pc = [], []
    for t in range(1, Bc.shape[0]):
        prev = {v: i + 1 for i, v in enumerate(Bc[t - 1])}
        for i, v in enumerate(Bc[t]):
            if v in prev:
                pp.append(prev[v]); pc.append(i + 1)
    return float(np.mean(pc)), corr(pp, pc), len(pc)


def carry_null(Bc, reps):
    a, b = [], []
    for _ in range(reps):
        m, c, _ = carry(shuffle_within(Bc, rng)); a.append(m); b.append(c)
    return np.array(a), np.array(b)


m, c, n = carry(B)
na, nb = carry_null(B, 3000)
res["H17a"] = dict(effect=f"mean pos of {n} repeated balls={m:.3f} (null {na.mean():.3f})", stat=m, p=mc_p(m, na), sign=float(np.sign(m - na.mean())))
res["H17b"] = dict(effect=f"corr(pos t-1, pos t)={c:+.3f}", stat=c, p=mc_p(c, nb), sign=float(np.sign(c - nb.mean())))

# H18: popularity beta vs frequency, parametric null
y = np.log(np.array([r["w3"] for r in rows]) / np.array([r["deposits"] for r in rows]))
years = np.array([r["date"].year for r in rows]); uy = np.unique(years)
Y = np.stack([(years == u).astype(float) for u in uy], 1)


def fit(Xn, yv, lam=1.0):
    D = np.hstack([Xn, Y])
    P = np.diag(np.r_[np.full(N, lam), np.full(len(uy), 1e-6)])
    coef = np.linalg.solve(D.T @ D + P, D.T @ yv)
    return coef


coef = fit(X, y)
beta = coef[:N] - coef[:N].mean()
resid = y - np.hstack([X, Y]) @ coef
obs = corr(beta, X.sum(0))
null = []
for _ in range(2000):
    Xs = indicator(random_draws(nd, rng))
    ys = np.hstack([Xs, Y]) @ coef + rng.choice(resid, nd)
    cs = fit(Xs, ys)
    null.append(corr(cs[:N] - cs[:N].mean(), Xs.sum(0)))
null = np.array(null)
res["H18"] = dict(effect=f"corr(popularity beta, train freq)={obs:+.3f} (null mean {null.mean():+.3f})", stat=obs, p=mc_p(obs, null), sign=float(np.sign(obs - null.mean())))
json.dump(tr, open(LAB + "/train_results.json", "w"), indent=1)
for k in ["H17a", "H17b", "H18"]:
    print(k, round(res[k]["p"], 4), res[k]["effect"])
