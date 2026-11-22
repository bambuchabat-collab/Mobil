"""Shared helpers for subagent-5 'ideas' tests (see ../ideas_prereg.md). Run scripts with python3 -I from scripts/."""
import json, os
from itertools import combinations
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
DATA = os.path.join(BASE, 'data')

# EV tier shares of the prize fund (herny plan cl. 29) and prize fund = 57.90 % of stakes
EV_SHARE = {'5+1': 0.015, '5+0': 0.043, '4+1': 0.044, '4+0': 0.108, '3+1': 0.062, '3+0': 0.270}
EV_FUND = 0.579


def load_ev():
    ev = json.load(open(os.path.join(DATA, 'ev.json')))
    n = len(ev)
    D = np.array([sorted(d['main']) for d in ev], dtype=int)
    pb = np.array([d['pb'] for d in ev], dtype=int)
    bets = np.array([d['bets'] for d in ev], dtype=float)
    tw = lambda d, k: d['tiers'].get(k, [0.0, 0])[1]
    n3 = np.array([tw(d, '3+0') + tw(d, '3+1') for d in ev], dtype=float)
    n4 = np.array([tw(d, '4+0') + tw(d, '4+1') for d in ev], dtype=float)
    old = np.array(['3+1' not in d['tiers'] for d in ev], dtype=float)
    thu = np.array([d['day'] != 'Pondelok' for d in ev], dtype=float)
    low = np.array([sum(v[0] * v[1] for k, v in d['tiers'].items() if k not in ('6+1', '6+0')) / d['deposits']
                    for d in ev])
    prem = (low > 0.45).astype(float)
    top = np.array([d['tiers']['6+0'][1] + d['tiers']['6+1'][1] for d in ev], dtype=int)
    return dict(ev=ev, n=n, D=D, pb=pb, bets=bets, n3=n3, n4=n4, old=old, thu=thu, prem=prem, payout=low,
                top=top, dates=[d['date'] for d in ev])


def ind27(D):
    X = np.zeros((len(D), 27))
    for j in range(D.shape[1]):
        X[np.arange(len(D)), D[:, j] - 1] = 1.0
    return X


# ---------- pattern features (D: N x 6 sorted, values 1..27) ----------
def f_consec(D):
    return (np.diff(D, axis=1) == 1).sum(1).astype(float)


def _pairs_same(lab):
    out = np.zeros(len(lab))
    for a, b in combinations(range(lab.shape[1]), 2):
        out += (lab[:, a] == lab[:, b])
    return out


def f_row(D, w):
    return _pairs_same((D - 1) // w)


def f_col(D, w):
    return _pairs_same((D - 1) % w)


def f_lowpairs(D):
    m = (D <= 12).sum(1)
    return m * (m - 1) / 2.0


def f_sd(D):
    return D.std(axis=1)


def f_ap3(D):
    out = np.zeros(len(D))
    for a, b, c in combinations(range(D.shape[1]), 3):
        out += (D[:, b] - D[:, a] == D[:, c] - D[:, b])
    return out


def f_m5pairs(D):
    m = (D % 5 == 0).sum(1)
    return m * (m - 1) / 2.0


def f_overlap(D, S):
    S = np.asarray(sorted(S))
    return np.isin(D, S).sum(1).astype(float)


def history_sets(Dhist, tophist, t):
    """Sets used by H4 for a draw at position t (uses draws < t only)."""
    prev = set(Dhist[t - 1]) if t >= 1 else set()
    jp = set()
    for s in range(t - 1, -1, -1):
        if tophist[s] > 0:
            jp = set(Dhist[s]); break
    if t >= 1:
        cnt = np.zeros(28)
        for s in range(max(0, t - 10), t):
            cnt[Dhist[s]] += 1
        order = sorted(range(1, 28), key=lambda x: (-cnt[x], x))
        hot = set(order[:6])
    else:
        hot = set()
    return prev, jp, hot


def holm(pdict):
    items = sorted(pdict.items(), key=lambda kv: kv[1])
    k = len(items); out = {}; run = 0.0
    for i, (h, p) in enumerate(items):
        run = max(run, min(1.0, (k - i) * p))
        out[h] = run
    return out


def all_combos():
    return np.array(list(combinations(range(1, 28), 6)), dtype=np.int16)
