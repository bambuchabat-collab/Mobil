"""Red-team helpers (independent of popularity.py / ideas_*.py). python3 -I, numpy only.
Data: ../data/ev.json (170 EV draws, oldest first). Nothing here is fitted on anything."""
import json, os, itertools
from math import comb
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
EV = json.load(open(os.path.join(BASE, 'data', 'ev.json')))
N = len(EV)
PM = {m: comb(6, m) * comb(21, 6 - m) / comb(27, 6) for m in range(7)}
NM = {m: comb(6, m) * comb(21, 6 - m) for m in range(7)}


def tw(x, k):
    return x['tiers'].get(k, [0.0, 0])


DATES = np.array([x['date'] for x in EV])
MAIN = np.array([sorted(x['main']) for x in EV], int)
PB = np.array([x['pb'] for x in EV], int)
B = np.array([x['deposits'] / 1.5 for x in EV])
PRE = np.array(['3+1' not in x['tiers'] for x in EV])            # extra drawn from 1-4, no 3+1 tier
THU = np.array([not x['day'].startswith('P') for x in EV])
PREM = np.array([x['date'][:7] in ('2026-05', '2026-10') for x in EV])
Z = np.zeros((N, 27))
Z[np.arange(N)[:, None], MAIN - 1] = 1
NPAIR = (np.diff(MAIN, axis=1) == 1).sum(1).astype(float)
W = {m: np.array([tw(x, f'{m}+0')[1] + tw(x, f'{m}+1')[1] for x in EV], float) for m in (3, 4, 5)}
W1 = {m: np.array([tw(x, f'{m}+1')[1] for x in EV], float) for m in (3, 4, 5)}
W0 = {m: np.array([tw(x, f'{m}+0')[1] for x in EV], float) for m in (3, 4, 5)}
# y_m = log(winners / (bets * P_m)); pre-era 3-match lacks the 3+1 tier -> only usable with an era dummy
Y = {m: np.log(W[m] / (B * PM[m])) for m in (3, 4, 5)}
POST = ~PRE

# all 296010 possible draws
COMBS = np.array(list(itertools.combinations(range(27), 6)), dtype=np.int8)
NC = len(COMBS)
DALL = np.zeros((NC, 27), dtype=np.float32)
DALL[np.arange(NC)[:, None], COMBS] = 1
DB = DALL.astype(bool)
NPAIR_ALL = (np.diff(COMBS, axis=1) == 1).sum(1).astype(np.float64)

# least -> most popular order claimed by subagent 4 (P1)
CLAIM_ORDER = [20, 14, 15, 1, 16, 18, 2, 10, 23, 22, 26, 19, 8, 24, 21, 4, 5, 6, 27, 12, 17, 9, 13, 25, 3, 7, 11]
FINAL = ([1, 2, 14, 15, 20, 21], 6, [10, 16, 18, 19, 23, 24], 7)
RUNNER = ([1, 2, 15, 16, 18, 19], 6, [10, 14, 20, 21, 23, 24], 7)


def npairs(f):
    f = sorted(f)
    return sum(1 for a, b in zip(f, f[1:]) if b == a + 1)


def has_run3(f):
    s = set(f)
    return any(i in s and i + 1 in s and i + 2 in s for i in s)


def ap3(f):
    f = sorted(f)
    return [(a, b, c) for a, b, c in itertools.combinations(f, 3) if b - a == c - b]


def ridge(X, y, pen, w=None):
    w = np.ones(len(y)) if w is None else w
    XtW = X.T * w
    A = np.linalg.inv(XtW @ X + np.diag(pen))
    return A @ (XtW @ y), A


def loo_ridge_lambda(X, y, npen_cols, grid, w=None):
    """closed-form LOO CV for ridge with the last npen_cols columns penalised by lambda; returns best lambda"""
    w = np.ones(len(y)) if w is None else w
    k = X.shape[1] - npen_cols
    best = None
    for l in grid:
        th, A = ridge(X, y, np.r_[np.full(k, 1e-9), np.full(npen_cols, l)], w)
        h = np.einsum('ij,jk,ik->i', X, A, X) * w
        e = (y - X @ th) / (1 - h)
        cv = float(np.mean(e ** 2))
        if best is None or cv < best[0]:
            best = (cv, l)
    return best[1]


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1])


def extra_shares(sel):
    """share of m-match (m=3,4,5 in the post era) winners holding the drawn extra, pooled by drawn extra x=1..7"""
    out = np.full(7, np.nan)
    for x in range(1, 8):
        ii = np.where(sel & (PB == x) & POST)[0]
        if len(ii):
            n1 = sum(W1[m][ii].sum() for m in (3, 4, 5)); nt = sum(W[m][ii].sum() for m in (3, 4, 5))
            out[x - 1] = n1 / nt
    return out


def pool_shares(sel):
    """realised share of deposits paid per tier (mean over selected draws)"""
    out = {}
    for m in (3, 4, 5):
        for e in (1, 0):
            k = f'{m}+{e}'
            out[k] = float(np.mean([tw(EV[t], k)[0] * tw(EV[t], k)[1] / EV[t]['deposits'] for t in np.where(sel)[0]]))
    return out
