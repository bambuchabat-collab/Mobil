"""Test statistics, null generators and models. Shared by train.py and holdout.py."""
import math
import numpy as np
from lab_common import N, K, indicator, ink, moon_age, date_root, digital_root, corr

NUMS = np.arange(1, N + 1)
INK = np.array([ink(n) for n in NUMS], float)
HYPER_VF = (N - K) / (N - 1)  # finite-population factor for 5 of 35


# ---------------- per-draw context ----------------
def context(rows):
    dates = [r["date"] for r in rows]
    doy = np.array([d.timetuple().tm_yday for d in dates], float)
    age = np.array([moon_age(d) for d in dates])
    years = np.array([d.year for d in dates])
    dep = np.array([r["deposits"] for r in rows])
    hi = np.zeros(len(rows), int)
    for y in np.unique(years):
        m = years == y
        hi[m] = (dep[m] > np.median(dep[m])).astype(int)
    season = np.array([{12: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2, 9: 3, 10: 3, 11: 3}[d.month] for d in dates])
    return dict(
        wd=np.array([r["wd"] for r in rows]),
        year=years,
        season=season,
        hi_sales=hi,
        moonq=np.floor(age / 29.530588853 * 4).astype(int) % 4,
        illum=(1 - np.cos(2 * np.pi * age / 29.530588853)) / 2,
        temp=-np.cos(2 * np.pi * (doy - 15) / 365.25),
        droot=np.array([date_root(d) for d in dates]),
        dom=np.array([d.day for d in dates]),
        joker=[set(r["joker"]) for r in rows],
    )


# ---------------- order statistics ----------------
def pos_table(B):
    C = np.zeros((N, K))
    for p in range(K):
        C[:, p] = np.bincount(B[:, p] - 1, minlength=N)
    return C


def meanpos(B):
    C = pos_table(B)
    Nn = C.sum(1)
    return (C * np.arange(1, K + 1)).sum(1) / np.maximum(Nn, 1), Nn


def s_pos_chi2(B):
    C = pos_table(B)
    E = C.sum(1, keepdims=True) / K
    return float(((C - E) ** 2 / np.maximum(E, 1e-9)).sum())


def pos_resid(B):
    C = pos_table(B)
    E = C.sum(1, keepdims=True) / K
    return ((C - E) / np.sqrt(np.maximum(E, 1e-9))).ravel()


def s_meanpos(B):
    m, Nn = meanpos(B)
    return float((Nn * (m - 3) ** 2 / 2).sum())


def s_early_freq(B):
    m, Nn = meanpos(B)
    return corr(m, Nn)


def s_single_pos(B):
    pos = np.tile(np.arange(1, K + 1), (B.shape[0], 1))
    return float(pos[B <= 9].mean())


def s_ink_pos(B):
    m, _ = meanpos(B)
    return corr(INK, m)


def s_seqdist(B):
    return float(np.abs(np.diff(B, axis=1)).mean())


def trans_counts(B):
    T = np.zeros((N, N))
    for p in range(K - 1):
        np.add.at(T, (B[:, p] - 1, B[:, p + 1] - 1), 1)
    return T


def cooc(B):
    X = indicator(B)
    Cc = X.T @ X
    np.fill_diagonal(Cc, 0)
    return Cc


def s_trans_chi2(B, Cc=None):
    if Cc is None:
        Cc = cooc(B)
    T = trans_counts(B)
    E = Cc / K
    m = E > 0
    return float(((T[m] - E[m]) ** 2 / E[m]).sum())


def trans_resid(B):
    Cc = cooc(B)
    T = trans_counts(B)
    E = Cc / K
    R = np.zeros_like(E)
    m = E > 0
    R[m] = (T[m] - E[m]) / np.sqrt(E[m])
    return R.ravel()


# ---------------- set statistics ----------------
def freq(B):
    return np.bincount(B.ravel() - 1, minlength=N).astype(float)


def s_single_count(B):
    return float((B <= 9).sum())


def z_single_count(B):
    nd = B.shape[0]
    p = 9 / N
    e = nd * K * p
    v = nd * K * p * (1 - p) * HYPER_VF
    return (s_single_count(B) - e) / math.sqrt(v)


def s_ink_freq(B):
    return corr(INK, freq(B))


def s_consec(B):
    S = np.sort(B, axis=1)
    X = indicator(S)
    return float((X[:, :-1] * X[:, 1:]).sum())


def s_range(B):
    return float((B.max(1) - B.min(1)).mean())


def chi2_homog(B, labels):
    X = indicator(B)
    labs = np.unique(labels)
    O = np.stack([X[labels == l].sum(0) for l in labs], 1)  # 35 x L
    E = O.sum(1, keepdims=True) * O.sum(0, keepdims=True) / O.sum()
    return float(((O - E) ** 2 / np.maximum(E, 1e-9)).sum())


def homog_resid(B, labels, labs):
    X = indicator(B)
    O = np.stack([X[labels == l].sum(0) for l in labs], 1)
    E = O.sum(1, keepdims=True) * O.sum(0, keepdims=True) / O.sum()
    return ((O - E) / np.sqrt(np.maximum(E, 1e-9))).ravel()


def diff2(B, labels, a, b):
    X = indicator(B)
    return X[labels == a].mean(0) - X[labels == b].mean(0)


def freq_dev(B):
    f = freq(B)
    return f - f.mean()


def s_split_persist(B):
    h = B.shape[0] // 2
    return corr(freq_dev(B[:h]), freq_dev(B[h:]))


def s_temp_ink(B, temp):
    return corr(temp, INK[B - 1].mean(1))


def s_illum_sum(B, illum):
    return corr(illum, B.sum(1))


def z_droot(B, droot):
    roots = np.array([digital_root(n) for n in NUMS])
    obs = 0.0; e = 0.0; v = 0.0
    for t in range(B.shape[0]):
        c = (roots == droot[t]).sum(); p = c / N
        obs += (roots[B[t] - 1] == droot[t]).sum()
        e += K * p; v += K * p * (1 - p) * HYPER_VF
    return (obs - e) / math.sqrt(v), obs - e


def z_dom(B, dom):
    hit = np.array([dom[t] in B[t] for t in range(B.shape[0])], float)
    p = K / N
    e = len(hit) * p
    return (hit.sum() - e) / math.sqrt(len(hit) * p * (1 - p)), hit.sum() - e


def z_joker(B, joker):
    last = NUMS % 10
    obs = 0.0; e = 0.0; v = 0.0
    for t in range(B.shape[0]):
        J = joker[t]
        inJ = np.array([l in J for l in last])
        p = inJ.sum() / N
        obs += inJ[B[t] - 1].sum()
        e += K * p; v += K * p * (1 - p) * HYPER_VF
    return (obs - e) / math.sqrt(v), obs - e


# ---------------- conditional-Bernoulli mixture (H16) ----------------
def esym(theta, kmax=K):
    """elementary symmetric polynomials e_0..e_kmax of theta (last axis)."""
    e = [np.ones(theta.shape[:-1])] + [np.zeros(theta.shape[:-1]) for _ in range(kmax)]
    for i in range(theta.shape[-1]):
        th = theta[..., i]
        for k in range(kmax, 0, -1):
            e[k] = e[k] + th * e[k - 1]
    return e


def cb_incl(theta):
    """inclusion probabilities under conditional Bernoulli(theta) with |S|=5."""
    e = esym(theta)
    # e_k without item i: recursion
    em = [np.ones_like(theta)]
    for k in range(1, K):
        em.append(e[k][..., None] - theta * em[k - 1])
    return theta * em[K - 1] / e[K][..., None]


def cb_loglik_rows(X, logtheta):
    """log P(S_t) for each draw under CB(theta). X (nd,35), logtheta (35,)"""
    th = np.exp(logtheta)
    return X @ logtheta - math.log(esym(th)[K])


def fit_cb_mixture(X, ncomp, rng, iters=150, restarts=3):
    nd = X.shape[0]
    best = None
    for r in range(restarts):
        lt = np.log(np.exp(rng.normal(0, 0.3, (ncomp, N))))
        pi = np.ones(ncomp) / ncomp
        for it in range(iters):
            L = np.stack([cb_loglik_rows(X, lt[k]) for k in range(ncomp)], 1) + np.log(pi)
            mx = L.max(1, keepdims=True)
            ll = float((mx[:, 0] + np.log(np.exp(L - mx).sum(1))).sum())
            R = np.exp(L - mx); R /= R.sum(1, keepdims=True)
            pi = R.mean(0) + 1e-12
            for k in range(ncomp):
                target = (R[:, k] @ X) / R[:, k].sum()  # weighted inclusion freq
                target = np.clip(target, 1e-4, 1 - 1e-4)
                for _ in range(3):
                    inc = cb_incl(np.exp(lt[k]))
                    lt[k] += np.log(target / inc)
                lt[k] -= lt[k].mean()
        if best is None or ll > best[0]:
            best = (ll, lt.copy(), pi.copy())
    return best


def cb_mix_logpred(X, lt, pi):
    L = np.stack([cb_loglik_rows(X, lt[k]) for k in range(len(pi))], 1) + np.log(pi)
    mx = L.max(1, keepdims=True)
    return mx[:, 0] + np.log(np.exp(L - mx).sum(1))


LOG_UNIF_SET = -math.log(math.comb(N, K))
LOG_UNIF_ORD = -sum(math.log(N - k) for k in range(K))


# ---------------- Plackett-Luce (M2) ----------------
def pl_fit(B, alpha, w0=None, iters=60):
    w = np.ones(N) if w0 is None else w0.copy()
    c = freq(B)
    for _ in range(iters):
        Wd = w[B - 1]  # nd x 5
        tot = w.sum()
        cum = np.concatenate([np.zeros((B.shape[0], 1)), np.cumsum(Wd, 1)[:, :-1]], 1)
        inv = 1.0 / (tot - cum)  # nd x 5, stage k denominator
        S_total = inv.sum()
        tail = np.cumsum(inv[:, ::-1], 1)[:, ::-1]  # sum_{k>=p}
        tail_after = np.concatenate([tail[:, 1:], np.zeros((B.shape[0], 1))], 1)  # sum_{k>p}
        D = S_total - np.bincount((B - 1).ravel(), weights=tail_after.ravel(), minlength=N)
        w = (c + alpha) / (D + alpha)
        w *= N / w.sum()
    return w


def pl_logscore(B, w):
    Wd = w[B - 1]
    cum = np.concatenate([np.zeros((B.shape[0], 1)), np.cumsum(Wd, 1)[:, :-1]], 1)
    return (np.log(Wd) - np.log(w.sum() - cum)).sum(1)


# ---------------- picks / hits ----------------
def top5(score, rng):
    jit = rng.random(N) * 1e-9
    return np.argsort(-(score + jit))[:K] + 1


def hits(pick, draw):
    return len(set(pick.tolist()) & set(draw.tolist()))


HIT_MEAN = K * K / N
HIT_VAR = K * (K / N) * (1 - K / N) * HYPER_VF


def hits_z(h):
    h = np.asarray(h, float)
    return (h.mean() - HIT_MEAN) / math.sqrt(HIT_VAR / len(h))


# ---------------- Dirichlet / exponential forgetting (M1) ----------------
def disc_scores(X, half):
    """walk-forward discounted counts: row t uses draws < t. returns (nd,35)."""
    lam = 1.0 if half is None else 0.5 ** (1.0 / half)
    S = np.zeros_like(X)
    acc = np.zeros(N)
    for t in range(X.shape[0]):
        S[t] = acc
        acc = lam * acc + X[t]
    return S


def bern_logscore(X, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return (X * np.log(p) + (1 - X) * np.log(1 - p)).sum(1)


def tilt_probs(S, beta):
    z = (S - S.mean(1, keepdims=True)) / (S.std(1, keepdims=True) + 1e-9)
    w = np.exp(beta * z)
    return K / N * w / w.mean(1, keepdims=True)
