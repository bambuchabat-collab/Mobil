"""Red team: independent prize-factor model for EV tiers 3-5 (written from scratch, not imported from popularity.py).
Per tier m: ridge of y_m = log(W_m / (bets*P_m)) on [1, pre-era, thu, premium, log bets, #pairs, 27 numbers];
u_m(D) = sum_{i in D} beta_i + gamma_m * npairs(D);  co-winners of a field S in tier m  ~  exp(u_m(D)) / E_D exp(u_m).
A_m(S) = E[ E exp(u) / exp(u(D)) | |S∩D| = m ]  (relative prize when S wins tier m), random field = E[exp(-u)] E[exp(u)].
Return per 1 EUR, tiers 3-5 = sum_m A_m(S) * K_m(x),  K_m(x) = f_{m+1}/(7 s_x) + f_{m+0} (1/7) sum_{q!=x} 1/(1-s_q)."""
import numpy as np
from redteam_common import *

logB = np.log(B)
COV = np.column_stack([np.ones(N), PRE, THU, PREM, logB - logB.mean()]).astype(float)
LGRID = [0.3, 1, 3, 10, 30, 100]
C_M = {m: m / 6 - (6 - m) / 21 for m in range(7)}


def fit_tier(idx, m, lam=None, pairs='linear'):
    cov = COV[idx]
    keep = [0] + [c for c in range(1, 5) if np.ptp(cov[:, c]) > 0]
    if pairs == 'linear':
        P = NPAIR[idx][:, None]
    elif pairs == 'dummy':
        P = np.column_stack([NPAIR[idx] == 1, NPAIR[idx] == 2, NPAIR[idx] >= 3]).astype(float)
    else:
        P = np.zeros((len(idx), 0))
    X = np.column_stack([cov[:, keep], P, Z[idx]]); y = Y[m][idx]
    k = len(keep) + P.shape[1]
    if lam is None:
        lam = loo_ridge_lambda(X, y, 27, LGRID)
    th, _ = ridge(X, y, np.r_[np.full(k, 1e-9), np.full(27, lam)])
    b = th[k:] - th[k:].mean()
    g = th[len(keep):k]
    return {'beta': b, 'gamma': g, 'lam': lam, 'pairs': pairs}


def u_all(f):
    u = DALL.astype(np.float64) @ f['beta']
    if f['pairs'] == 'linear':
        u = u + f['gamma'][0] * NPAIR_ALL
    elif f['pairs'] == 'dummy':
        u = u + f['gamma'][0] * (NPAIR_ALL == 1) + f['gamma'][1] * (NPAIR_ALL == 2) + f['gamma'][2] * (NPAIR_ALL >= 3)
    return u


def A_of_fields(fields, fits):
    """exact enumeration over all 296010 draws for a short list of fields -> array (n_fields, 3) and random-field A (3,)"""
    S = np.zeros((len(fields), 27), np.float32)
    for r, f in enumerate(fields):
        S[r, np.array(f) - 1] = 1
    ov = (DALL @ S.T).astype(np.int8)                    # (NC, n_fields)
    A = np.zeros((len(fields), 3)); Ar = np.zeros(3)
    for c, m in enumerate((3, 4, 5)):
        u = u_all(fits[m]); eu = np.exp(u); emu = np.exp(-u); ebar = eu.mean()
        Ar[c] = emu.mean() * ebar
        for r in range(len(fields)):
            A[r, c] = emu[ov[:, r] == m].mean() * ebar
    return A, Ar


def dp_A(Smask, fits, m_list=(3, 4, 5)):
    """exact A_m for many fields at once (chain DP over numbers 1..27, linear pair term only)."""
    Nf = len(Smask); out = np.zeros((Nf, len(m_list)))
    for c, m in enumerate(m_list):
        f = fits[m]; w = np.exp(-f['beta']); th = np.exp(-f['gamma'][0]) if f['pairs'] == 'linear' else 1.0
        ebar = np.exp(u_all(f)).mean()
        # V[f, k chosen, s overlap, prev chosen]
        V = np.zeros((Nf, 7, 7, 2)); V[:, 0, 0, 0] = 1.0
        for j in range(27):
            inS = Smask[:, j]
            Vn = np.zeros_like(V)
            Vn[..., 0] = V[..., 0] + V[..., 1]                      # j not chosen
            add = w[j] * (V[..., 0] + th * V[..., 1])               # j chosen (pair factor if j-1 chosen)
            Vn[~inS, 1:, :, 1] += add[~inS, :-1, :]
            Vn[inS, 1:, 1:, 1] += add[inS, :-1, :-1]
            V = Vn
        tot = V[:, 6, :, 0] + V[:, 6, :, 1]                        # (Nf, 7) sums of exp(-u) by overlap
        out[:, c] = tot[:, m] / NM[m] * ebar
    return out


def K_extra(sh, fpool):
    sh = sh / sh.sum(); K = np.zeros((3, 7))
    for c, m in enumerate((3, 4, 5)):
        for x in range(7):
            K[c, x] = fpool[f'{m}+1'] / (7 * sh[x]) + fpool[f'{m}+0'] * sum(1 / (1 - sh[q]) for q in range(7) if q != x) / 7
    return K


def fit_all(idx, lams=None, pairs='linear', pool45=False):
    fits = {m: fit_tier(idx, m, None if lams is None else lams[m], pairs) for m in (3, 4, 5)}
    if pool45:   # borrow strength: 5-match number effects scaled from 4-match (log-linear player model)
        fits[5] = dict(fits[5]); fits[5]['beta'] = fits[4]['beta'] * C_M[5] / C_M[4]
    return fits
