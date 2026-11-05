"""Exploratory: calibration of train-fitted 4-hit-prize model on holdout."""
import sys, math, itertools
sys.path.insert(0, "/tmp/claude-0/-home-user-Mobil/b5a09aa0-3ae1-547d-aca0-e9005dcfc1f6/scratchpad/agent_lab")
import numpy as np
from lab_common import load, ordered, indicator, corr, N
rows = load("all"); X = indicator(ordered(rows))
yrs = np.array([r["date"].year for r in rows]); uy = np.unique(yrs)
Y = np.stack([(yrs == u).astype(float) for u in uy], 1)
yp4 = np.log(np.array([r["p4"] for r in rows])); y3 = np.log(np.array([r["w3"] for r in rows]) / np.array([r["deposits"] for r in rows]))
tm = yrs <= 2023; hm = ~tm
def ridge(Xn, y, Yd, lam=1.0):
    D = np.hstack([Xn, Yd]); P = np.diag(np.r_[np.full(N, lam), np.full(Yd.shape[1], 1e-6)])
    c = np.linalg.solve(D.T @ D + P, D.T @ y); return c[:N] - c[:N].mean()
def dm(y, m):
    out = y.copy()
    for u in np.unique(yrs[m]): out[yrs[m] == u] -= out[yrs[m] == u].mean()
    return out
for name, yy in [("log p4", yp4), ("log W3/dep", y3)]:
    g = ridge(X[tm], yy[tm], Y[tm][:, np.isin(uy, np.unique(yrs[tm]))])
    pred = X[hm] @ g; act = dm(yy[hm], hm)
    slope = np.polyfit(pred, act, 1)[0]
    print(f"{name}: holdout corr={corr(pred, act):+.3f}, calibration slope={slope:.2f}, sd(pred)={pred.std():.3f}, sd(actual)={act.std():.3f}")
gam = ridge(X, yp4, Y); beta = ridge(X, y3, Y)
print("corr(beta, gamma) all data:", round(corr(beta, gam), 3))
pick = [1, 18, 30, 32, 35]
print("gamma pick:", np.round(gam[np.array(pick) - 1], 3), "sum", round(gam[np.array(pick) - 1].sum(), 3))
combs = np.array(list(itertools.combinations(range(1, 36), 5)))
s = gam[combs - 1].sum(1); print("sum gamma over random sets: mean", round(s.mean(), 3), "sd", round(s.std(), 3), "pick percentile", round((s < gam[np.array(pick)-1].sum()).mean(), 4))
