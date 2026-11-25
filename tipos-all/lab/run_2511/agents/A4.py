"""A4 - MACHINE LEARNING family (see A4_prereg.md). Run: python3 -I A4.py"""
import sys, json, datetime
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2511')
from harness import evaluate, DRAWS
import numpy as np

np.random.seed(2511)
N = 22
FIRST_TRAIN = 10
START = 30
REFIT = 10
LAMBDA = 10.0


def weekday_of(past, s):
    """weekday (0=Mon) of target draw s; for s == len(past) use last past date + 1 day."""
    if s < len(past):
        return datetime.date.fromisoformat(past[s]['date']).weekday()
    return (datetime.date.fromisoformat(past[-1]['date']) + datetime.timedelta(days=1)).weekday()


def base_features(past, s):
    """(22, 14) features for target draw s using only past[:s]."""
    F = np.zeros((N, 14))
    M = np.zeros((s, N))
    for i in range(s):
        M[i, np.array(past[i]['main']) - 1] = 1
    for k in range(1, 11):
        F[:, k - 1] = M[s - k] if s - k >= 0 else 0.5
    F[:, 10] = M[max(0, s - 20):s].mean(0) if s > 0 else 0.5
    F[:, 11] = M.mean(0) if s > 0 else 0.5
    for j in range(N):
        idx = np.nonzero(M[:, j])[0]
        g = (s - idx[-1]) if len(idx) else 10
        F[j, 12] = min(g, 10) / 10.0
    if s > 0:
        for p, x in enumerate(past[s - 1]['order']):
            F[x - 1, 13] = (p + 1 - 6) / 5.0
    return F


def labels(past, s):
    y = np.zeros(N)
    y[np.array(past[s]['main']) - 1] = 1
    return y


def full_features(past, s, with_num, with_wd):
    F = base_features(past, s)
    parts = [F]
    if with_num:
        parts.append(np.eye(N))
    if with_wd:
        w = np.zeros((N, 7)); w[:, weekday_of(past, s)] = 1
        parts.append(w)
    return np.hstack(parts)


# ---------------- L2 logistic regression (Newton / IRLS) ----------------
def fit_logreg(X, y, lam=LAMBDA, iters=50, tol=1e-8):
    mu = X.mean(0); sd = X.std(0); sd[sd == 0] = 1
    Z = np.hstack([np.ones((len(X), 1)), (X - mu) / sd])
    p_ = Z.shape[1]
    L = np.eye(p_) * lam; L[0, 0] = 0
    w = np.zeros(p_)
    for _ in range(iters):
        pr = 1 / (1 + np.exp(-Z @ w))
        g = Z.T @ (pr - y) + L @ w
        H = (Z * (pr * (1 - pr))[:, None]).T @ Z + L
        step = np.linalg.solve(H, g)
        w -= step
        if np.max(np.abs(step)) < tol:
            break
    return (mu, sd, w)


def predict_logreg(model, X):
    mu, sd, w = model
    Z = np.hstack([np.ones((len(X), 1)), (X - mu) / sd])
    return 1 / (1 + np.exp(-Z @ w))


# ---------------- gradient-boosted stumps ----------------
def fit_stumps(X, y, rounds=100, lr=0.1, lam=1.0, min_side=20, max_thr=16):
    cands = []
    for f in range(X.shape[1]):
        u = np.unique(X[:, f])
        mids = (u[:-1] + u[1:]) / 2
        if len(mids) > max_thr:
            mids = mids[np.round(np.linspace(0, len(mids) - 1, max_thr)).astype(int)]
        for th in mids:
            cands.append((f, th))
    B = np.stack([X[:, f] <= th for f, th in cands], 1).astype(float)
    cntL = B.sum(0); cntR = len(X) - cntL
    ok = (cntL >= min_side) & (cntR >= min_side)
    pbar = y.mean()
    f0 = np.log(pbar / (1 - pbar))
    Fx = np.full(len(X), f0)
    stumps = []
    for _ in range(rounds):
        pr = 1 / (1 + np.exp(-Fx))
        g = pr - y; h = pr * (1 - pr)
        G, H = g.sum(), h.sum()
        GL = B.T @ g; HL = B.T @ h
        GR = G - GL; HR = H - HL
        gain = GL ** 2 / (HL + lam) + GR ** 2 / (HR + lam) - G ** 2 / (H + lam)
        gain[~ok] = -np.inf
        c = int(np.argmax(gain))
        vl = -GL[c] / (HL[c] + lam) * lr
        vr = -GR[c] / (HR[c] + lam) * lr
        f, th = cands[c]
        stumps.append((f, th, vl, vr))
        Fx += np.where(B[:, c] > 0, vl, vr)
    return (f0, stumps)


def predict_stumps(model, X):
    f0, stumps = model
    Fx = np.full(len(X), f0)
    for f, th, vl, vr in stumps:
        Fx += np.where(X[:, f] <= th, vl, vr)
    return 1 / (1 + np.exp(-Fx))


# ---------------- rules ----------------
def refit_point(t):
    return START + REFIT * ((t - START) // REFIT) if t >= START else t


def lowest11(prob):
    return [int(i) + 1 for i in np.argsort(prob, kind='stable')[:11]]


def make_rule(kind):
    cache = {}
    with_num = kind in ('R1', 'R3')
    with_wd = kind in ('R2', 'R3')

    def get_model(past, R):
        if R in cache:
            return cache[R]
        hist = past[:R]                      # only draws < R <= t
        Xs, ys = [], []
        for s in range(FIRST_TRAIN, R):
            Xs.append(full_features(hist, s, with_num, with_wd))
            ys.append(labels(hist, s))
        X = np.stack(Xs)                     # (draws, 22, p)
        Y = np.stack(ys)
        if kind == 'R1':
            m = fit_logreg(X.reshape(-1, X.shape[2]), Y.reshape(-1))
        elif kind == 'R2':
            m = [fit_logreg(X[:, j, :], Y[:, j]) for j in range(N)]
        else:
            m = fit_stumps(X.reshape(-1, X.shape[2]), Y.reshape(-1))
        cache[R] = m
        return m

    def rule(past):
        t = len(past)
        m = get_model(past, refit_point(t))
        Xt = full_features(past, t, with_num, with_wd)
        if kind == 'R1':
            p = predict_logreg(m, Xt)
        elif kind == 'R2':
            p = np.array([predict_logreg(m[j], Xt[j:j + 1])[0] for j in range(N)])
        else:
            p = predict_stumps(m, Xt)
        return lowest11(p)
    return rule


DEFS = {
    'R1': 'PRIMARY. Pooled L2 logistic regression (lambda=10, Newton) over (draw,number) rows; features L1..L10 '
          'last-10-draw indicators, freq last 20, freq all, gap(min 10)/10, position in last draw order, + 22 '
          'number dummies; standardized; refit every 10 draws on targets 10..R-1; ticket = 11 lowest prob.',
    'R2': 'Per-number L2 logistic regression (22 models, lambda=10, Newton); same 14 lag features + 7 weekday '
          'dummies of target draw; refit every 10 draws; ticket = 11 lowest prob.',
    'R3': 'Gradient-boosted stumps (pooled, 100 rounds, lr 0.1, leaf L2=1, min 20 rows/side, <=16 thresholds) on '
          '14 lag features + 22 number dummies + 7 weekday dummies; refit every 10 draws; ticket = 11 lowest prob.',
}

if __name__ == '__main__':
    out = {'id': 'A4', 'family': 'MACHINE LEARNING', 'rules': []}
    tickets = {}
    for k in ('R1', 'R2', 'R3'):
        r = make_rule(k)
        res = evaluate(r, k)
        res = {a: (float(b) if isinstance(b, (np.floating, float)) else int(b) if isinstance(b, (np.integer,)) else b)
               for a, b in res.items()}
        res['definition'] = DEFS[k]
        out['rules'].append(res)
        tickets[k] = sorted(r(DRAWS))
        print(res, 'ticket25.11:', tickets[k], flush=True)
    out['ticket_25_11'] = tickets['R1']
    out['tickets_all_rules_25_11'] = tickets
    json.dump(out, open('/home/user/Mobil/tipos-all/lab/run_2511/agents/A4.json', 'w'), indent=1, ensure_ascii=False)
