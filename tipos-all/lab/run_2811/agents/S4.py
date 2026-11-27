"""S4 - signal processing / time-series econometrics (28.11.2026). Pre-registration: S4_prereg.md.
F1 (EM): per-number generalized Lomb-Scargle on calendar days, dominant frequency, extrapolated to target date.
F2 (EM): Kalman local-level propensity per number, signal-to-noise ratio q chosen by pooled ML on past draws.
F3 (VAN): pooled multi-segment Burg (maximum-entropy) AR linear prediction, order by AIC.
Run: python3 -I S4.py   (numpy only, deterministic, no randomness)
"""
import sys, json, datetime, collections
import numpy as np
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2811')
from harness2 import evaluate, load, params

OUT = '/home/user/Mobil/tipos-all/lab/run_2811/agents/S4.json'
EPOCH = datetime.date(2000, 1, 1).toordinal()
DIAG = collections.defaultdict(list)
N_EM = params('EM')[1]  # game range as defined by the harness


def game_N(past):
    return N_EM if 'extra' in past[0] else 22


def day(s):
    return datetime.date.fromisoformat(s).toordinal() - EPOCH


def top_T(score, T):
    score = np.asarray(score, float)
    idx = np.lexsort((np.arange(len(score)), -score))  # highest score, ties -> smaller number
    return [int(i) + 1 for i in idx[:T]]


# ---------------- F1: generalized Lomb-Scargle (floating mean), ridge-stabilised ----------------
FREQS = np.concatenate([np.arange(1, 4001) / 8000.0, [1 / 7, 2 / 7, 3 / 7]])
OM = 2 * np.pi * FREQS
LAM = 1e-3


class LSCache:
    """Running sums over a prefix of the past draws (built only from `past`; reset if the prefix changes)."""

    def __init__(self, N):
        self.N = N
        self.reset()

    def reset(self):
        F = len(FREQS)
        self.keys = []
        self.n = 0
        self.sc = np.zeros(F); self.ss = np.zeros(F); self.scc = np.zeros(F); self.scs = np.zeros(F)
        self.sx = np.zeros(self.N); self.sxc = np.zeros((self.N, F)); self.sxs = np.zeros((self.N, F))
        self.d0 = None; self.dlast = None

    def sync(self, past):
        k = len(self.keys)
        if k > len(past) or any(self.keys[j] != (past[j]['date'], tuple(past[j]['main'])) for j in range(k)):
            self.reset(); k = 0
        for r in past[k:]:
            d = day(r['date'])
            c = np.cos(OM * d); s = np.sin(OM * d)
            self.n += 1; self.sc += c; self.ss += s; self.scc += c * c; self.scs += c * s
            for m in r['main']:
                self.sx[m - 1] += 1; self.sxc[m - 1] += c; self.sxs[m - 1] += s
            if self.d0 is None: self.d0 = d
            self.dlast = d
            self.keys.append((r['date'], tuple(r['main'])))


_LS = {}


def F1(past, date, T=None, N=None, log=True):
    if N is None:
        N = game_N(past)
    if T is None:
        T = len(past[0]['main'])
    cache = _LS.setdefault(N, LSCache(N))
    cache.sync(past)
    n = cache.n
    Y = cache.sx / n; C = cache.sc / n; S = cache.ss / n
    CC = cache.scc / n - C * C
    SS = (n - cache.scc) / n - S * S
    CS = cache.scs / n - C * S
    YC = cache.sxc / n - Y[:, None] * C
    YS = cache.sxs / n - Y[:, None] * S
    YY = Y - Y * Y
    a11 = CC + LAM; a22 = SS + LAM; det = a11 * a22 - CS * CS
    b = (YC * a22 - YS * CS) / det
    c = (YS * a11 - YC * CS) / det
    with np.errstate(divide='ignore', invalid='ignore'):
        P = (YC * b + YS * c) / YY[:, None]
    P[~np.isfinite(P)] = 0.0
    span = cache.dlast - cache.d0
    adm = FREQS >= 1.0 / span
    P[:, ~adm] = -np.inf
    ks = np.argmax(P, axis=1)
    tau = day(date)
    rows = np.arange(N)
    score = (Y + b[rows, ks] * (np.cos(OM[ks] * tau) - C[ks]) + c[rows, ks] * (np.sin(OM[ks] * tau) - S[ks]))
    if log:
        DIAG['F1_period'].extend((1 / FREQS[ks]).tolist())
        DIAG['F1_power'].extend(P[rows, ks].tolist())
    return top_T(score, T)


# ---------------- F2: Kalman local level, ML signal-to-noise ratio ----------------
QGRID = np.array([0, 1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2])


def F2(past, date, N=None, K=None, log=True):
    if N is None:
        N = game_N(past)
    if K is None:
        K = len(past[0]['main'])
    p0 = K / N; R = p0 * (1 - p0); Q = QGRID * R
    G = len(QGRID)
    mu = np.full((G, N), p0); P = np.full(G, (0.1 * p0) ** 2); LL = np.zeros(G)
    x = np.zeros(N)
    for r in past:
        x[:] = 0.0; x[np.array(r['main']) - 1] = 1.0
        F = P + R
        v = x[None, :] - mu
        LL += -0.5 * N * np.log(F) - 0.5 * (v * v).sum(1) / F
        Kg = P / F
        mu += Kg[:, None] * v
        P = P * (1 - Kg) + Q
    g = int(np.argmax(LL))  # first maximum -> smaller q
    if log:
        DIAG['F2_q'].append(float(QGRID[g]))
    return top_T(mu[g], K)


# ---------------- F3: pooled Burg maximum-entropy AR, AIC order ----------------
PMAX = 14


def burg_pooled(Yc, pmax):
    """Multi-segment Burg: common reflection coefficients for all rows of Yc (centered)."""
    f = Yc.copy(); b = Yc.copy()
    a = np.array([1.0]); sig2 = float((Yc * Yc).mean())
    out = [(a.copy(), sig2)]
    for m in range(1, pmax + 1):
        ff = f[:, 1:]; bb = b[:, :-1]
        den = float((ff * ff).sum() + (bb * bb).sum())
        k = -2.0 * float((ff * bb).sum()) / den if den > 0 else 0.0
        ext = np.concatenate([a, [0.0]])
        a = ext + k * ext[::-1]
        f, b = ff + k * bb, bb + k * ff
        sig2 *= (1 - k * k)
        out.append((a.copy(), sig2))
    return out


def F3(past, date, N=None, log=True):
    if N is None:
        N = game_N(past)
    K = len(past[0]['main'])
    t = len(past)
    X = np.zeros((N, t))
    for j, r in enumerate(past):
        X[np.array(r['main']) - 1, j] = 1.0
    xbar = X.mean(1)
    Yc = X - xbar[:, None]
    fits = burg_pooled(Yc, min(PMAX, t - 2))
    n = N * t
    aic = [n * np.log(s2) + 2 * m for m, (a, s2) in enumerate(fits)]
    m = int(np.argmin(aic))
    a = fits[m][0]
    pred = np.zeros(N)
    for kk in range(1, m + 1):
        pred -= a[kk] * Yc[:, t - kk]
    if log:
        DIAG['F3_order'].append(m)
    return top_T(xbar + pred, K)


# ---------------- self-tests on synthetic data (no lottery data) ----------------
def selftest():
    rng = np.random.default_rng(12345)
    # Burg: recover AR(2) y_t = 0.5 y_{t-1} - 0.3 y_{t-2} + e
    y = np.zeros((5, 4000))
    for t in range(2, 4000):
        y[:, t] = 0.5 * y[:, t - 1] - 0.3 * y[:, t - 2] + rng.standard_normal(5)
    a2 = burg_pooled(y - y.mean(1, keepdims=True), 2)[2][0]
    assert abs(a2[1] + 0.5) < 0.03 and abs(a2[2] - 0.3) < 0.03, a2
    # LS: number 1 strongly periodic with period 7 days on a Tue/Fri schedule -> forecast follows phase
    N = 33; d0 = datetime.date(2020, 1, 7)
    past = []
    for w in range(200):
        for off in (0, 3):
            dt = d0 + datetime.timedelta(days=7 * w + off)
            main = [1] + list(rng.choice(np.arange(2, 34), 6, replace=False) + 0) if off == 0 else \
                list(rng.choice(np.arange(2, 34), 7, replace=False))
            past.append({'date': dt.isoformat(), 'main': sorted(int(v) for v in main), 'extra': 1})
    tue = (d0 + datetime.timedelta(days=1400)).isoformat(); fri = (d0 + datetime.timedelta(days=1403)).isoformat()
    _LS.clear()
    assert 1 in F1(past, tue, log=False) and 1 not in F1(past, fri, log=False)
    _LS.clear()
    print('selftest ok')


def main():
    selftest()
    defs = {
        'F1': ('EM', F1,
               'Generalized (floating-mean) Lomb-Scargle per number on calendar days; freq grid k/8000 (k=1..4000) '
               '+ 1/7,2/7,3/7 cycles/day, admissible f>=1/span; ridge lam=1e-3; dominant f = argmax explained-variance '
               'power on past draws only; score = fitted sinusoid at the target date; top 7.',
               'score_i = Y_i + b_i(f*)[cos(2pi f* tau)-C] + c_i(f*)[sin(2pi f* tau)-S],  f*_i = argmax_f P_i(f) on past'),
        'F2': ('EM', F2,
               'Kalman local-level per number: x=mu+eps (R=p0(1-p0)), mu random walk (Q=qR), mu0=p0, P0=(0.1p0)^2; '
               'q in {0,1e-6,3e-6,1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2} by pooled prediction-error log-likelihood on '
               'past draws; score = one-step predicted propensity; top 7.',
               'score_i = mu_i(t|t-1; q_hat),  q_hat = argmax_q sum_j sum_i log N(v_ij; 0, P_j+R)'),
        'F3': ('VAN', F3,
               'Pooled multi-segment Burg (max-entropy) AR on the 22 centered indicator series, orders 0..14, '
               'order by AIC n ln sigma2_m + 2m (n=22t); score = own past mean + AR one-step forecast; top 11.',
               'score_i = xbar_i - sum_{k<=m_hat} a_k (x_i(t-k) - xbar_i),  a = Burg PEF, m_hat = argmin AIC'),
    }
    results = []
    for name, (game, f, definition, ftext) in defs.items():
        _LS.clear()
        res = evaluate(f, game, 'S4_' + name)
        res.update({'formula': name, 'definition': definition, 'formula_text': ftext})
        results.append(res)
        print(name, game, 'n=%d mean=%.4f exp=%.4f p_upper=%.4f p_lower=%.4f' %
              (res['n'], res['mean_hits'], res['expected'], res['p_upper'], res['p_lower']), res['hist'])
    # diagnostics
    per = np.array(DIAG['F1_period'])
    diag = {
        'F1_share_weekday_freqs': float(np.mean(np.isin(np.round(per, 6), np.round([7, 3.5, 7 / 3], 6)))),
        'F1_median_period_days': float(np.median(per)),
        'F1_median_power': float(np.median(DIAG['F1_power'])),
        'F2_q_hat_counts': {str(k): int(v) for k, v in collections.Counter(DIAG['F2_q']).items()},
        'F3_order_counts': {str(k): int(v) for k, v in sorted(collections.Counter(DIAG['F3_order']).items())},
    }
    print(diag)
    # predictions for Saturday 28.11.2026 (full history)
    em = load('EM'); van = load('VAN')
    _LS.clear()
    p1 = sorted(F1(em, '2026-11-28', log=False))
    p2 = sorted(F2(em, '2026-11-28', log=False))
    p3 = sorted(F3(van, '2026-11-28', log=False))
    print('28.11 F1 EM', p1, ' F2 EM', p2, ' F3 VAN', p3)
    out = {'id': 'S4', 'science': 'signal processing / time-series econometrics',
           'game': 'EM (F1, F2) + VAN (F3)', 'formulas': results,
           'prediction_28_11': {'game': 'EM', 'numbers': p1, 'formula': 'F1'},
           'extra_predictions_28_11': {'F2': {'game': 'EM', 'numbers': p2}, 'F3': {'game': 'VAN', 'numbers': p3}},
           'diagnostics': diag}
    json.dump(out, open(OUT, 'w'), indent=1, ensure_ascii=False)
    print('written', OUT)


if __name__ == '__main__':
    main()
