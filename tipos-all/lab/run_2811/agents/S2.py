"""S2 - information theory / algorithmic complexity (28.11.2026).
Universal sequence prediction by compression on the per-number binary drawn/not-drawn sequences.
F1: per-number CTW (depth 8, KT).  F2: per-number LZ78 predictor (Feder-Merhav-Gutman).
F3: prequential-MDL choice among M0 iid Bernoulli(K/N), M1 per-number KT, M2 pooled CTW, M3 per-number CTW, M4 per-number LZ78.
Secondary: entropy-rate test, compression gain vs iid maximum with a Monte-Carlo null.
Run: python3 -I S2.py   (plan: S2_prereg.md)
"""
import sys, json, math, time
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2811')
import numpy as np
from harness2 import evaluate, load, params

D = 8                                  # CTW depth (fixed a priori)
NNODES = 2 ** (D + 1) - 1
MAXC = 60000
LGH = np.array([math.lgamma(k + 0.5) for k in range(MAXC)])
LGI = np.array([math.lgamma(k + 1.0) for k in range(MAXC)])
LG0 = math.lgamma(0.5)
LN2 = math.log(2.0)
MODELS = ['M0_iid', 'M1_KT_freq', 'M2_pooled_CTW', 'M3_pernumber_CTW', 'M4_pernumber_LZ78']


def logpe(a, b):                       # natural log of KT block probability
    return LGH[a] + LGH[b] - 2 * LG0 - LGI[a + b]


def paths(ctx):
    """ctx: (D, M) int array, ctx[d] = x(s-1-d). returns (D+1, M) node indices root..leaf."""
    M = ctx.shape[1]
    p = np.zeros((D + 1, M), dtype=np.int64)
    for d in range(1, D + 1):
        p[d] = 2 * p[d - 1] + 1 + ctx[d - 1]
    return p


def ctw_hypo(a, b, lpw, path, ctx, rows):
    """Hypothetical root-to-leaf log Pw after adding symbol 0 / 1 at the given paths.
    a, b, lpw indexed [rows, node]; returns L0, L1 of shape (D+1, M)."""
    out = []
    for x in (0, 1):
        L = np.empty(path.shape)
        n = path[D]
        L[D] = logpe(a[rows, n] + (1 - x), b[rows, n] + x)
        for d in range(D - 1, -1, -1):
            n = path[d]
            sib = 2 * n + 1 + (1 - ctx[d])
            lpe = logpe(a[rows, n] + (1 - x), b[rows, n] + x)
            L[d] = np.logaddexp(lpe, L[d + 1] + lpw[rows, sib]) - LN2
        out.append(L)
    return out


class Engine:
    """Online state of all five models; fed only with draws from `past`."""

    def __init__(self, N, K):
        self.N, self.K = N, K
        self.hist = []                  # (date, tuple(main)) of processed draws
        self.L = np.zeros(len(MODELS))  # cumulative prequential code length, bits
        self.sel = []                   # MDL-selected model before each draw
        # M1
        self.n1 = np.zeros(N)
        # M3 per-number CTW
        self.a3 = np.zeros((N, NNODES), dtype=np.int64); self.b3 = np.zeros_like(self.a3)
        self.lpw3 = np.zeros((N, NNODES))
        # M2 pooled CTW (row 0 shared by all numbers)
        self.a2 = np.zeros((1, NNODES), dtype=np.int64); self.b2 = np.zeros_like(self.a2)
        self.lpw2 = np.zeros((1, NNODES))
        self.ctx = np.zeros((D, N), dtype=np.int64)
        # M4 LZ78 per number
        self.lz_ch = [[[-1, -1]] for _ in range(N)]
        self.lz_cnt = [[[0, 0]] for _ in range(N)]
        self.lz_cur = [0] * N
        self._prepare()

    def _prepare(self):
        N, t = self.N, len(self.hist)
        rowsN = np.arange(N); rows0 = np.zeros(N, dtype=np.int64)
        self.path = paths(self.ctx)
        P = np.empty((len(MODELS), N))
        P[0] = self.K / N
        P[1] = (self.n1 + 0.5) / (t + 1.0)
        self.h2 = ctw_hypo(self.a2, self.b2, self.lpw2, self.path, self.ctx, rows0)
        P[2] = 1.0 / (1.0 + np.exp(self.h2[0][0] - self.h2[1][0]))
        self.h3 = ctw_hypo(self.a3, self.b3, self.lpw3, self.path, self.ctx, rowsN)
        P[3] = 1.0 / (1.0 + np.exp(self.h3[0][0] - self.h3[1][0]))
        for i in range(N):
            c0, c1 = self.lz_cnt[i][self.lz_cur[i]]
            P[4, i] = (c1 + 0.5) / (c0 + c1 + 1.0)
        self.P = P

    def feed(self, draw):
        N = self.N
        x = np.zeros(N, dtype=np.int64); x[np.array(draw['main']) - 1] = 1
        self.sel.append(int(np.argmin(self.L)))
        P = np.clip(self.P, 1e-300, 1 - 1e-16)
        self.L += -np.where(x == 1, np.log2(P), np.log2(1 - P)).sum(axis=1)
        # M1
        self.n1 += x
        # M3 commit
        rowsN = np.arange(N)
        for d in range(D + 1):
            n = self.path[d]
            self.lpw3[rowsN, n] = np.where(x == 1, self.h3[1][d], self.h3[0][d])
            self.a3[rowsN, n] += 1 - x; self.b3[rowsN, n] += x
        # M2 batch update (CTW state is a function of node counts only -> exact)
        for d in range(D + 1):
            np.add.at(self.a2[0], self.path[d], 1 - x); np.add.at(self.b2[0], self.path[d], x)
        lo = 2 ** D - 1
        self.lpw2[0, lo:] = logpe(self.a2[0, lo:], self.b2[0, lo:])
        for d in range(D - 1, -1, -1):
            n = np.arange(2 ** d - 1, 2 ** (d + 1) - 1)
            self.lpw2[0, n] = np.logaddexp(logpe(self.a2[0, n], self.b2[0, n]),
                                           self.lpw2[0, 2 * n + 1] + self.lpw2[0, 2 * n + 2]) - LN2
        # M4 LZ78
        for i in range(N):
            c = self.lz_cur[i]; s = int(x[i])
            self.lz_cnt[i][c][s] += 1
            ch = self.lz_ch[i][c][s]
            if ch >= 0:
                self.lz_cur[i] = ch
            else:
                self.lz_ch[i].append([-1, -1]); self.lz_cnt[i].append([0, 0])
                self.lz_ch[i][c][s] = len(self.lz_ch[i]) - 1
                self.lz_cur[i] = 0
        # context shift
        self.ctx = np.vstack([x[None, :], self.ctx[:-1]])
        self.hist.append((draw['date'], tuple(draw['main'])))
        self._prepare()


_ENG = {}


def engine_for(game, past):
    """Engine state after exactly the draws in `past` (rebuilt if `past` is not an extension of what was fed)."""
    _, N, K, T = params(game)
    e = _ENG.get(game)
    ok = e is not None and len(e.hist) <= len(past) and all(
        e.hist[j] == (past[j]['date'], tuple(past[j]['main'])) for j in range(len(e.hist)))
    if not ok:
        e = _ENG[game] = Engine(N, K)
    for r in past[len(e.hist):]:
        e.feed(r)
    return e


def top_T(p, date, T):
    N = len(p)
    key = np.random.default_rng(int(date.replace('-', ''))).random(N)
    order = np.lexsort((key, -np.round(p, 12)))
    return sorted(int(i) + 1 for i in order[:T])


def make_f(game, which):
    T = params(game)[3]

    def f(past, date):
        e = engine_for(game, past)
        if which == 'F1': p = e.P[3]
        elif which == 'F2': p = e.P[4]
        else: p = e.P[int(np.argmin(e.L))]
        return top_T(p, date, T)
    return f


def scratch_check(game, ts):
    """Recompute from scratch (fresh engine) and compare with the cached walk-forward state."""
    d = load(game); _, N, K, T = params(game)
    bad = 0
    for t in ts:
        fresh = Engine(N, K)
        for r in d[:t]: fresh.feed(r)
        cached = engine_for(game, d[:t])
        bad += int(not (np.allclose(fresh.P, cached.P) and np.allclose(fresh.L, cached.L)))
    return bad


def code_lengths(draws, N, K):
    e = Engine(N, K)
    for r in draws: e.feed(r)
    return e.L.copy(), e


def entropy_test(game, nsim, seed):
    d = load(game); _, N, K, T = params(game); n = len(d)
    Lobs, e = code_lengths(d, N, K)
    Gobs = Lobs[0] - Lobs[1:]
    rng = np.random.default_rng(seed)
    Gsim = []
    for s in range(nsim):
        sim = [{'date': r['date'], 'main': sorted((rng.choice(N, K, replace=False) + 1).tolist())} for r in d]
        Ls, _ = code_lengths(sim, N, K)
        Gsim.append(Ls[0] - Ls[1:])
    Gsim = np.array(Gsim)
    pE = [(1 + int((Gsim[:, m] >= Gobs[m]).sum())) / (nsim + 1) for m in range(4)]
    h = -(K / N) * math.log2(K / N) - (1 - K / N) * math.log2(1 - K / N)
    return {'game': game, 'n_draws': n, 'nsim': nsim, 'seed': seed,
            'iid_max_bits_per_symbol': h, 'log2_C(N,K)_bits_per_draw': math.log2(math.comb(N, K)),
            'bits_per_symbol': {MODELS[m]: float(Lobs[m] / (n * N)) for m in range(5)},
            'bits_per_draw': {MODELS[m]: float(Lobs[m] / n) for m in range(5)},
            'gain_bits_vs_iid': {MODELS[m + 1]: float(Gobs[m]) for m in range(4)},
            'null_gain_mean': {MODELS[m + 1]: float(Gsim[:, m].mean()) for m in range(4)},
            'null_gain_sd': {MODELS[m + 1]: float(Gsim[:, m].std(ddof=1)) for m in range(4)},
            'p_E': {MODELS[m + 1]: float(pE[m]) for m in range(4)},
            'mdl_final_choice': MODELS[int(np.argmin(Lobs))]}


DEFS = {
    'F1': ('Per-number context-tree weighting (CTW, depth 8, KT estimator) on each number\'s binary drawn/not-drawn '
           'sequence; predicted set = 7 numbers with highest CTW probability P(drawn next | own past).',
           'p_i = Pw(x_i^{t-1} 1) / Pw(x_i^{t-1}),  Pw = 1/2 Pe(KT) + 1/2 Pw(c0) Pw(c1), D = 8;  pick top-7 p_i'),
    'F2': ('Per-number LZ78 incremental-parsing predictor (Feder-Merhav-Gutman): P(1) = (n1+1/2)/(n0+n1+1) '
           'at the current node of the LZ78 parse tree; predicted set = 7 numbers with highest P(1).',
           'p_i = (n1(cur_i)+1/2)/(n0(cur_i)+n1(cur_i)+1) on LZ78 tree of x_i;  pick top-7 p_i'),
    'F3': ('Prequential MDL: before each draw choose, among M0 iid Bernoulli(7/33), M1 per-number KT frequency, '
           'M2 pooled CTW(8), M3 per-number CTW(8), M4 per-number LZ78, the model with the smallest cumulative code '
           'length on all past draws (ties -> lower index); predict top-7 by its probabilities (M0 -> fixed tie key).',
           'm* = argmin_m sum_{s<t} sum_i -log2 P_m(x_i(s) | <s);  pick top-7 P_{m*}(x_i(t)=1)'),
}


def main():
    t0 = time.time()
    game = 'EM'
    out = {'id': 'S2', 'science': 'information theory / algorithmic complexity (universal prediction by compression: '
           'CTW, LZ78, MDL; entropy-rate test)', 'game': game, 'formulas': []}
    for F in ('F1', 'F2', 'F3'):
        _ENG.clear()
        r = evaluate(make_f(game, F), game, 'S2_' + F)
        r['definition'], r['formula_text'] = DEFS[F]
        if F == 'F3':
            e = _ENG[game]   # engine fed with d[:n-1] at the end of the walk-forward
            sel = np.array(e.sel[30:])
            r['mdl_selection_share'] = {MODELS[m]: float((sel == m).mean()) for m in range(5)}
        out['formulas'].append(r)
        print(F, {k: r[k] for k in ('n', 'mean_hits', 'expected', 'p_upper', 'p_lower')}, r['hist'],
              round(time.time() - t0, 1), 's', flush=True)
    out['scratch_check_mismatches'] = scratch_check(game, [31, 200, 777])
    print('scratch check mismatches:', out['scratch_check_mismatches'], flush=True)
    # prediction for 28.11.2026 by F1 on the whole history
    d = load(game)
    _ENG.clear()
    e = engine_for(game, d)
    pred = make_f(game, 'F1')(d, '2026-11-28')
    out['prediction_28_11'] = {'game': game, 'numbers': pred, 'formula': 'F1',
                               'F1_probabilities_top7': {str(i): float(e.P[3][i - 1]) for i in pred},
                               'F2_numbers': make_f(game, 'F2')(d, '2026-11-28'),
                               'F3_numbers': make_f(game, 'F3')(d, '2026-11-28'),
                               'F3_model_now': MODELS[int(np.argmin(e.L))]}
    print('prediction', out['prediction_28_11'], flush=True)
    # secondary: entropy-rate tests
    out['entropy_rate_test'] = [entropy_test('EM', 200, 2811)]
    print(json.dumps(out['entropy_rate_test'][0], indent=1), round(time.time() - t0, 1), 's', flush=True)
    out['entropy_rate_test'].append(entropy_test('VAN', 200, 2812))
    print(json.dumps(out['entropy_rate_test'][1], indent=1), round(time.time() - t0, 1), 's', flush=True)
    json.dump(out, open('/home/user/Mobil/tipos-all/lab/run_2811/agents/S2.json', 'w'), indent=1, ensure_ascii=False)
    print('done', round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
