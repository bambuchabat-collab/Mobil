"""S3 — CRYPTANALYSIS / RNG analysis (run 28.11.2026). Pre-registration: agents/S3_prereg.md.
F1 (VAN): Berlekamp–Massey over GF(2) on each number's hit/miss stream -> LFSR next-bit prediction.
F2 (EM):  Berlekamp–Massey over GF(37) on the Lehmer-code stream (outputs of 'draw from the remaining balls').
F3 (EM):  Berlekamp–Massey over GF(2) on the 6-bit binary expansion of the same Lehmer stream.
D0 data integrity, D1 NIST SP 800-22 battery, D2 exhaustive state search of 13 common 32-bit LCG variants.
Run: python3 -I S3.py [--skip-d2]
"""
import sys, json, math, time, os
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2811')
import numpy as np
from math import comb
from harness2 import evaluate, load

OUT = '/home/user/Mobil/tipos-all/lab/run_2811/agents/S3.json'
SEED = 2811

# ---------------------------------------------------------------- Berlekamp–Massey, online
class BM2:
    """Online Berlekamp–Massey over GF(2). Polynomials are Python ints (bit i = coefficient of D^i).
    S holds the stream reversed: bit i of S = s_{n-1-i}."""
    __slots__ = ('C', 'B', 'L', 'm', 'n', 'S')
    def __init__(self):
        self.C, self.B, self.L, self.m, self.n, self.S = 1, 1, 0, 1, 0, 0
    def push(self, s):
        self.S = (self.S << 1) | (s & 1)
        if (self.C & self.S).bit_count() & 1:          # discrepancy d = s_n + sum c_i s_{n-i}
            T = self.C
            self.C ^= self.B << self.m
            if 2 * self.L <= self.n:
                self.L, self.B, self.m = self.n + 1 - self.L, T, 1
            else:
                self.m += 1
        else:
            self.m += 1
        self.n += 1
    def predict(self, k):
        """continue the current LFSR k steps (state not modified)"""
        S, out = self.S, []
        for _ in range(k):
            b = (self.C & (S << 1)).bit_count() & 1
            out.append(b); S = (S << 1) | b
        return out

class BMp:
    """Online Berlekamp–Massey over GF(p), p prime. C, B numpy int64 coefficient arrays (C[0] = 1)."""
    def __init__(self, p, cap=16384):
        self.p = p; self.C = np.array([1], np.int64); self.B = np.array([1], np.int64)
        self.L = 0; self.m = 1; self.b = 1; self.n = 0; self.s = np.zeros(cap, np.int64)
    def push(self, x):
        p, n, L = self.p, self.n, self.L
        if n >= len(self.s):
            self.s = np.concatenate([self.s, np.zeros(len(self.s), np.int64)])
        self.s[n] = x % p
        k = min(len(self.C), L + 1)
        seg = self.s[n - k + 1:n + 1][::-1]                # seg[i] = s_{n-i}
        d = int(np.dot(self.C[:k], seg) % p)
        if d == 0:
            self.m += 1
        else:
            coef = d * pow(self.b, p - 2, p) % p
            T = self.C
            newlen = max(len(T), self.m + len(self.B))
            Cn = np.zeros(newlen, np.int64); Cn[:len(T)] = T
            Cn[self.m:self.m + len(self.B)] = (Cn[self.m:self.m + len(self.B)] - coef * self.B) % p
            if 2 * L <= n:
                self.L, self.B, self.b, self.m = n + 1 - L, T, d, 1
            else:
                self.m += 1
            self.C = Cn
        self.n += 1
    def predict(self, k):
        p, L = self.p, self.L
        c = self.C[1:L + 1] if len(self.C) > 1 else np.zeros(0, np.int64)
        c = np.concatenate([c, np.zeros(L - len(c), np.int64)])
        hist = list(self.s[max(0, self.n - L):self.n])       # last L symbols, oldest first
        out = []
        for _ in range(k):
            # s_n = -sum_{i=1..L} c_i s_{n-i}
            v = int(-np.dot(c, np.array(hist[::-1][:L], np.int64)) % p) if L > 0 else 0
            out.append(v); hist.append(v)
        return out

# ---------------------------------------------------------------- encodings
def lehmer(order, N):
    rem = list(range(1, N + 1)); out = []
    for b in order:
        i = rem.index(b); out.append(i); rem.pop(i)
    return out

def decode(vals, N):
    rem = list(range(1, N + 1)); out = []
    for v in vals:
        out.append(rem.pop(int(v) % len(rem)))
    return out

def key(d):
    return (d['date'], tuple(d['order']), tuple(d['main']))

class Online:
    """Causal cache: state built only from the draws in `past`; rebuilt if `past` is not an extension."""
    def __init__(self, make, feed):
        self.make, self.feed, self.keys, self.state = make, feed, None, None
    def get(self, past):
        n = len(past)
        if self.keys is None or n < len(self.keys) or any(self.keys[i] != key(past[i]) for i in range(len(self.keys))):
            self.state, self.keys = self.make(), []
        for i in range(len(self.keys), n):
            self.feed(self.state, past[i]); self.keys.append(key(past[i]))
        return self.state

# ---------------------------------------------------------------- formulas
N_VAN, T_VAN, N_EM, T_EM, P_EM = 22, 11, 33, 7, 37
TAU = {x: int(np.where(np.random.default_rng(SEED).permutation(N_VAN) == x - 1)[0][0]) for x in range(1, N_VAN + 1)}

def _f1_feed(st, d):
    ms = set(d['main'])
    for x in range(1, N_VAN + 1):
        st[x - 1].push(1 if x in ms else 0)
_F1 = Online(lambda: [BM2() for _ in range(N_VAN)], _f1_feed)

def f1_scores(past):
    st = _F1.get(past); n = len(past); rows = []
    for x in range(1, N_VAN + 1):
        bm = st[x - 1]
        rows.append((bm.predict(1)[0], n - 2 * bm.L, -TAU[x], x, bm.L))
    rows.sort(reverse=True)
    return rows

def F1(past, date):
    return [r[3] for r in f1_scores(past)[:T_VAN]]

def _f2_feed(st, d):
    for r in lehmer(d['order'], N_EM):
        st.push(r)
_F2 = Online(lambda: BMp(P_EM), _f2_feed)

def F2(past, date):
    return decode(_F2.get(past).predict(T_EM), N_EM)

def _f3_feed(st, d):
    for r in lehmer(d['order'], N_EM):
        for j in range(5, -1, -1):
            st.push((r >> j) & 1)
_F3 = Online(BM2, _f3_feed)

def F3(past, date):
    bits = _F3.get(past).predict(6 * T_EM)
    vals = [int(''.join(map(str, bits[6 * k:6 * k + 6])), 2) for k in range(T_EM)]
    return decode(vals, N_EM)

# ---------------------------------------------------------------- self-tests (synthetic data only)
def selftest():
    rng = np.random.default_rng(SEED); res = {}
    # GF(2): LFSR s_n = s_{n-3} + s_{n-7} (L = 7) must be recovered and predicted exactly
    s = list(rng.integers(0, 2, 7))
    while len(s) < 120: s.append(s[-3] ^ s[-7])
    bm = BM2()
    for b in s[:40]: bm.push(int(b))
    res['gf2_lfsr_L'] = bm.L; res['gf2_lfsr_pred_ok'] = bm.predict(80) == [int(b) for b in s[40:120]]
    # GF(2): random bits -> L close to n/2
    bm = BM2(); r = rng.integers(0, 2, 2000)
    for b in r: bm.push(int(b))
    res['gf2_random_L_minus_n2'] = bm.L - 1000
    # GF(37): LCG x' = 5x + 3 and Knuth lagged Fibonacci (24, 55) mod 37
    x = [11]
    while len(x) < 60: x.append((5 * x[-1] + 3) % 37)
    bm = BMp(37)
    for v in x[:10]: bm.push(v)
    res['gfp_lcg_L'] = bm.L; res['gfp_lcg_pred_ok'] = bm.predict(50) == x[10:60]
    y = list(rng.integers(0, 37, 55))
    while len(y) < 300: y.append((y[-24] + y[-55]) % 37)
    bm = BMp(37)
    for v in y[:110]: bm.push(int(v))
    res['gfp_lfg_L'] = bm.L; res['gfp_lfg_pred_ok'] = bm.predict(190) == [int(v) for v in y[110:300]]
    # online prediction equals prediction from a fresh BM run on the same prefix
    z = list(rng.integers(0, 37, 400)); a = BMp(37); ok = True
    for i, v in enumerate(z):
        if i in (50, 199, 333):
            b = BMp(37)
            for w in z[:i]: b.push(int(w))
            ok &= (a.predict(7) == b.predict(7)) and a.L == b.L
        a.push(int(v))
    res['gfp_online_eq_offline'] = bool(ok)
    # Lehmer encode/decode round trip on a random order
    o = [int(v) + 1 for v in rng.permutation(33)[:7]]
    res['lehmer_roundtrip_ok'] = decode(lehmer(o, 33), 33) == o
    return res

# ---------------------------------------------------------------- NIST SP 800-22 tests
def igamc(a, x):
    if x <= 0: return 1.0
    lg = -x + a * math.log(x) - math.lgamma(a)
    if x < a + 1:
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(100000):
            ap += 1; d *= x / ap; s += d
            if abs(d) < abs(s) * 1e-16: break
        return max(0.0, 1.0 - s * math.exp(lg))
    b = x + 1 - a; c = 1e300; d = 1 / b; h = d
    for i in range(1, 100000):
        an = -i * (i - a); b += 2
        d = an * d + b; d = d if abs(d) > 1e-300 else 1e-300
        c = b + an / c; c = c if abs(c) > 1e-300 else 1e-300
        d = 1 / d; de = d * c; h *= de
        if abs(de - 1) < 1e-16: break
    return math.exp(lg) * h

def Phi(z): return 0.5 * math.erfc(-z / math.sqrt(2))

def t_freq(e):
    n = len(e); S = 2 * int(e.sum()) - n
    return math.erfc(abs(S) / math.sqrt(2 * n))

def t_blockfreq(e, M=128):
    Nb = len(e) // M; b = e[:Nb * M].reshape(Nb, M).mean(1)
    return igamc(Nb / 2, 4 * M * float(((b - 0.5) ** 2).sum()) / 2)

def t_runs(e):
    n = len(e); pi = float(e.mean())
    if abs(pi - 0.5) >= 2 / math.sqrt(n): return 0.0
    V = 1 + int((e[1:] != e[:-1]).sum())
    return math.erfc(abs(V - 2 * n * pi * (1 - pi)) / (2 * math.sqrt(2 * n) * pi * (1 - pi)))

def _counts(e, m):
    n = len(e)
    if m <= 0: return None
    ext = np.concatenate([e, e[:m - 1]]).astype(np.int64)
    idx = np.zeros(n, np.int64)
    for j in range(m): idx = (idx << 1) | ext[j:j + n]
    return np.bincount(idx, minlength=2 ** m)

def _psi2(e, m):
    if m <= 0: return 0.0
    n = len(e); c = _counts(e, m)
    return (2 ** m / n) * float((c.astype(float) ** 2).sum()) - n

def t_serial(e, m):
    p0, p1, p2 = _psi2(e, m), _psi2(e, m - 1), _psi2(e, m - 2)
    return igamc(2 ** (m - 2), (p0 - p1) / 2), igamc(2 ** (m - 3), (p0 - 2 * p1 + p2) / 2)

def _phi(e, m):
    if m <= 0: return 0.0
    n = len(e); c = _counts(e, m); c = c[c > 0] / n
    return float((c * np.log(c)).sum())

def t_apen(e, m):
    n = len(e); ap = _phi(e, m) - _phi(e, m + 1)
    return igamc(2 ** (m - 1), 2 * n * (math.log(2) - ap) / 2)

def t_cusum(e, backward=False):
    n = len(e); X = 2 * e.astype(np.int64) - 1
    if backward: X = X[::-1]
    z = int(np.abs(np.cumsum(X)).max()); sq = math.sqrt(n)
    td = lambda a, b: int(a / b)                      # C integer division (truncation), as in the NIST sts code
    s1 = sum(Phi((4 * k + 1) * z / sq) - Phi((4 * k - 1) * z / sq)
             for k in range(td(td(-n, z) + 1, 4), td(td(n, z) - 1, 4) + 1))
    s2 = sum(Phi((4 * k + 3) * z / sq) - Phi((4 * k + 1) * z / sq)
             for k in range(td(td(-n, z) - 3, 4), td(td(n, z) - 1, 4) + 1))
    return min(1.0, max(0.0, 1 - s1 + s2))

def lc_pvalue(L, n, q=2):
    """exact two-sided P(|2L'-n| >= |2L-n|) for an i.i.d. uniform sequence over GF(q) (Rueppel / Niederreiter)."""
    lq = math.log(q); tot = 0.0; dev = abs(2 * L - n)
    for Lp in range(0, n + 1):
        if abs(2 * Lp - n) < dev: continue
        if Lp == 0: lp = -n * lq
        elif 2 * Lp <= n: lp = math.log(q - 1) + (2 * Lp - 1) * lq - n * lq
        else: lp = math.log(q - 1) + 2 * (n - Lp) * lq - n * lq
        if lp > -745: tot += math.exp(lp)
    return min(1.0, tot)

def lc2(e):
    bm = BM2()
    for b in e: bm.push(int(b))
    return bm.L

def battery_long(e):
    L = lc2(e); n = len(e)
    s1, s2 = t_serial(e, 4)
    return {'n_bits': n, 'Frequency': t_freq(e), 'BlockFrequency_M128': t_blockfreq(e, 128), 'Runs': t_runs(e),
            'Serial_m4_p1': s1, 'Serial_m4_p2': s2, 'ApEn_m4': t_apen(e, 4),
            'CuSum_fwd': t_cusum(e), 'CuSum_bwd': t_cusum(e, True),
            'LinearComplexity_exact': lc_pvalue(L, n), 'L': L, 'L_minus_n_over_2': L - n / 2}

def battery_short(e):
    L = lc2(e); n = len(e); s1, s2 = t_serial(e, 3)
    return {'Frequency': t_freq(e), 'Runs': t_runs(e), 'Serial_m3_p1': s1, 'Serial_m3_p2': s2,
            'ApEn_m2': t_apen(e, 2), 'CuSum_fwd': t_cusum(e), 'LinearComplexity_exact': lc_pvalue(L, n),
            'L': L, 'L_minus_n_over_2': L - n / 2}

def set_rank(main):
    return sum(comb(c - 1, i + 1) for i, c in enumerate(sorted(main)))

def ord_rank(order, N):
    R = 0
    for k, r in enumerate(lehmer(order, N)): R = R * (N - k) + r
    return R

def bits_from(ranks, limit, w):
    out = []
    for R in ranks:
        if R < limit:
            out.extend((R >> j) & 1 for j in range(w - 1, -1, -1))
    return np.array(out, np.uint8)

def binom_sf(k, n, p):
    return sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))

# ---------------------------------------------------------------- D2: exhaustive 32-bit LCG state search
M32, M31, MS = 2 ** 32, 2 ** 31, 2 ** 31 - 1
GENS = [  # name, a, c, true modulus, search modulus, mapping
    ('G1_delphi_mul', 134775813, 1, M32, M32, 'mul32'),
    ('G2_msvc_o15_mod', 214013, 2531011, M32, M31, 'o15mod'),
    ('G2_msvc_o15_mul', 214013, 2531011, M32, M31, 'o15mul'),
    ('G3a_ansi_x_mod', 1103515245, 12345, M31, M31, 'mod'),
    ('G3a_ansi_x_mul', 1103515245, 12345, M31, M31, 'mul31'),
    ('G3b_ansi_o15_mod', 1103515245, 12345, M31, M31, 'o15mod'),
    ('G3b_ansi_o15_mul', 1103515245, 12345, M31, M31, 'o15mul'),
    ('G4_nr_mod', 1664525, 1013904223, M32, M32, 'mod'),
    ('G4_nr_mul', 1664525, 1013904223, M32, M32, 'mul32'),
    ('G5_minstd16807_mod', 16807, 0, MS, MS, 'mod'),
    ('G5_minstd16807_mul', 16807, 0, MS, MS, 'msmul'),
    ('G6_minstd48271_mod', 48271, 0, MS, MS, 'mod'),
    ('G6_minstd48271_mul', 48271, 0, MS, MS, 'msmul'),
]
PROCS = ['P1', 'P2', 'P3', 'P4', 'P5']

def rand_s(x, n, mp):
    if mp == 'mul32': return (x * n) >> 32
    if mp == 'mul31': return (x * n) >> 31
    if mp == 'mod': return x % n
    if mp == 'o15mod': return ((x >> 16) & 0x7FFF) % n
    if mp == 'o15mul': return (((x >> 16) & 0x7FFF) * n) >> 15
    if mp == 'msmul': return (x * n) // MS

def rand_v(y, n, mp):
    n = np.uint64(n)
    if mp == 'mul32': return (y * n) >> np.uint64(32)
    if mp == 'mul31': return (y * n) >> np.uint64(31)
    if mp == 'mod': return y % n
    if mp == 'o15mod': return ((y >> np.uint64(16)) & np.uint64(0x7FFF)) % n
    if mp == 'o15mul': return (((y >> np.uint64(16)) & np.uint64(0x7FFF)) * n) >> np.uint64(15)
    if mp == 'msmul': return (y * n) // np.uint64(MS)

def synth_draw(g, x0, proc, N=22, K=11):
    """scalar reference implementation (independent of the vectorised search). Returns (order, x1)."""
    _, a, c, m, _, mp = g; st = [x0]; first = []
    def rnd(n):
        st[0] = (a * st[0] + c) % m
        if not first: first.append(st[0])
        return rand_s(st[0], n, mp)
    arr = list(range(1, N + 1)); out = []
    if proc == 'P1':
        for k in range(K): out.append(arr.pop(rnd(len(arr))))
    elif proc == 'P2':
        for k in range(K):
            j = rnd(len(arr)); out.append(arr[j]); arr[j] = arr[-1]; arr.pop()
    elif proc == 'P3':
        while len(out) < K:
            v = rnd(N) + 1
            if v not in out: out.append(v)
    elif proc == 'P4':
        for k in range(K):
            j = k + rnd(N - k); arr[k], arr[j] = arr[j], arr[k]; out.append(arr[k])
    elif proc == 'P5':
        for k in range(K):
            i = N - 1 - k; j = rnd(i + 1); arr[i], arr[j] = arr[j], arr[i]; out.append(arr[i])
    return out, first[0]

def required_indices(order, proc, N=22):
    arr = list(range(1, N + 1)); req = []
    for k, b in enumerate(order):
        if proc == 'P1':
            j = arr.index(b); req.append(j); arr.pop(j)
        elif proc == 'P2':
            j = arr.index(b); req.append(j); arr[j] = arr[-1]; arr.pop()
        elif proc == 'P4':
            j = arr.index(b); req.append(j - k); arr[k], arr[j] = arr[j], arr[k]
        elif proc == 'P5':
            i = N - 1 - k; j = arr.index(b); req.append(j); arr[i], arr[j] = arr[j], arr[i]
    return req

def first_candidates(g, r, N=22, chunk=1 << 23):
    """yield uint64 chunks of ALL search-modulus states x with rand(x, N) == r"""
    _, a, c, m, ms, mp = g
    def ranges(lo, hi):
        for s in range(lo, hi, chunk): yield np.arange(s, min(hi, s + chunk), dtype=np.uint64)
    if mp in ('mul32', 'mul31'):
        B = 32 if mp == 'mul32' else 31
        yield from ranges(-(-r * 2 ** B // N), -(-(r + 1) * 2 ** B // N))
    elif mp == 'msmul':
        yield from ranges(max(1, -(-r * MS // N)), min(MS, -(-(r + 1) * MS // N)))
    elif mp == 'mod':
        j0 = 1 if (ms == MS and r == 0) else 0; jmax = (ms - 1 - r) // N
        for s in range(j0, jmax + 1, chunk):
            yield np.uint64(r) + np.uint64(N) * np.arange(s, min(jmax + 1, s + chunk), dtype=np.uint64)
    else:  # o15mod / o15mul : o determines bits 16..30, low 16 bits free, bit 31 irrelevant (search mod 2^31)
        if mp == 'o15mod': os_ = np.arange(r, 32768, N, dtype=np.uint64)
        else: os_ = np.arange(-(-r * 32768 // N), -(-(r + 1) * 32768 // N), dtype=np.uint64)
        low = np.arange(65536, dtype=np.uint64); step = max(1, chunk // 65536)
        for s in range(0, len(os_), step):
            yield ((os_[s:s + step, None] << np.uint64(16)) | low[None, :]).ravel()

def lcg_step(y, a, c, ms):
    if ms == M32: return (y * np.uint64(a) + np.uint64(c)) & np.uint64(M32 - 1)
    if ms == M31: return (y * np.uint64(a) + np.uint64(c)) & np.uint64(M31 - 1)
    return (y * np.uint64(a) + np.uint64(c)) % np.uint64(ms)

def search_draw(g, order, N=22, K=11):
    """all states x1 (search modulus) that reproduce the full ordered draw under each procedure"""
    _, a, c, m, ms, mp = g
    req = {p: required_indices(order, p, N) for p in ('P1', 'P2', 'P4', 'P5')}
    pos = np.full(N + 2, 99, np.int64)
    for i, b in enumerate(order): pos[b] = i
    found = {p: [] for p in PROCS}; ncand = 0
    for x in first_candidates(g, order[0] - 1, N):
        ncand += len(x)
        y2 = lcg_step(x, a, c, ms)
        v21 = rand_v(y2, N - 1, mp)
        for p in ('P1', 'P2', 'P4', 'P5'):
            msk = v21 == np.uint64(req[p][1]); y = y2[msk]; x1 = x[msk]
            for k in range(2, K):
                if len(y) == 0: break
                y = lcg_step(y, a, c, ms); msk = rand_v(y, N - k, mp) == np.uint64(req[p][k]); y = y[msk]; x1 = x1[msk]
            found[p].extend(int(v) for v in x1)
        # P3: rand(N)+1 each call, duplicates rejected
        v = (rand_v(y2, N, mp) + np.uint64(1)).astype(np.int64)
        pv = pos[v]; kk = np.ones(len(x), np.int64)
        keep = (pv < kk) | (pv == kk)
        y, x1, kk = y2[keep], x[keep], kk[keep] + (pv[keep] == 1)
        it = 0
        while len(y) and it < 400:
            done = kk == K
            if done.any(): found['P3'].extend(int(t) for t in x1[done]); y, x1, kk = y[~done], x1[~done], kk[~done]
            if not len(y): break
            y = lcg_step(y, a, c, ms); pv = pos[(rand_v(y, N, mp) + np.uint64(1)).astype(np.int64)]
            keep = (pv < kk) | (pv == kk)
            y, x1, kk = y[keep], x1[keep], kk[keep] + (pv[keep] == kk[keep]); it += 1
    return found, ncand

def run_d2(van):
    rng = np.random.default_rng(SEED); res = {'controls': [], 'real': []}
    t0 = time.time()
    for gi, g in enumerate(GENS):
        proc = PROCS[gi % 5]
        x0 = int(rng.integers(1, g[3] - 1))
        order, x1 = synth_draw(g, x0, proc)
        f, nc = search_draw(g, order)
        ok = (x1 % g[4]) in f[proc]
        res['controls'].append({'gen': g[0], 'proc': proc, 'order': order, 'found_true_state': bool(ok),
                                'n_states_found': {p: len(v) for p, v in f.items()}, 'n_candidates': nc})
        print('  control', g[0], proc, ok, {p: len(v) for p, v in f.items()}, f'{time.time() - t0:.0f}s', flush=True)
    for di in range(5):
        order = van[di]['order']
        for g in GENS:
            f, nc = search_draw(g, order)
            res['real'].append({'draw': di, 'date': van[di]['date'], 'gen': g[0], 'n_candidates': nc,
                                'n_states_found': {p: len(v) for p, v in f.items()},
                                'states': {p: v[:10] for p, v in f.items() if v}})
        print('  real draw', di, f'{time.time() - t0:.0f}s', flush=True)
    hyp = {}
    for r in res['real']:
        for p, cnt in r['n_states_found'].items():
            hyp.setdefault(f"{r['gen']}/{p}", 0); hyp[f"{r['gen']}/{p}"] += int(cnt > 0)
    res['draws_matched_per_hypothesis'] = hyp
    res['confirmed_hypotheses'] = [h for h, v in hyp.items() if v >= 2]
    res['seconds'] = time.time() - t0
    return res

# ---------------------------------------------------------------- main
def clean(o):
    if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(v) for v in o]
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, np.bool_): return bool(o)
    return o

def main():
    t0 = time.time()
    van, em = load('VAN'), load('EM')
    out = {'id': 'S3', 'science': 'cryptanalysis / RNG analysis (Berlekamp–Massey linear-complexity attacks, '
           'NIST SP 800-22 battery, exhaustive 32-bit LCG state recovery)', 'game': 'both (F1 VAN; F2, F3 EM)'}
    out['selftest'] = selftest(); print('selftest', out['selftest'], flush=True)

    # D0
    from collections import Counter
    d0 = {}
    for nm, D, N in (('VAN', van, 22), ('EM', em, 33)):
        d0[nm] = {'n': len(D), 'order_equals_sorted': sum(d['order'] == sorted(d['main']) for d in D),
                  'order_is_perm_of_main': sum(sorted(d['order']) == sorted(d['main']) for d in D),
                  'days': dict(Counter(d['day'].lower() for d in D))}
    out['D0'] = d0; print('D0', d0, flush=True)

    # formulas
    defs = {
        'F1': ('VAN', F1, 'BM over GF(2) on each number\'s hit stream; ticket = 11 numbers whose shortest LFSR predicts 1, '
               'ranked by (predicted bit, n-2L, fixed seeded tiebreak 2811)',
               'F1(past) = top11_x [ BM_GF2(1[x in main_j], j<t).next_bit, t-2L_x, -tau_x ]'),
        'F2': ('EM', F2, 'BM over GF(37) on the Lehmer-code stream r_k (index of ball among remaining sorted balls), full history; '
               'continue recurrence 7 symbols, decode v_k mod (34-k)',
               'F2(past) = decode( LFSR_GF37(lehmer stream).next7 )'),
        'F3': ('EM', F3, 'BM over GF(2) on the 6-bit MSB-first expansion of the Lehmer stream (42 bits/draw), full history; '
               'continue LFSR 42 bits -> 7 six-bit values, decode v_k mod (34-k)',
               'F3(past) = decode( LFSR_GF2(bits(lehmer stream)).next42 )'),
    }
    out['formulas'] = []
    for name, (game, f, definition, text) in defs.items():
        r = evaluate(f, game, name); r['definition'] = definition; r['formula_text'] = text
        out['formulas'].append(r); print(name, {k: r[k] for k in ('game', 'n', 'mean_hits', 'expected', 'p_upper', 'p_lower')}, flush=True)

    # linear complexity of the full formula streams (descriptive)
    st1 = _F1.get(van); st2 = _F2.get(em); st3 = _F3.get(em)
    out['linear_complexity_full_streams'] = {
        'F1_VAN_per_number': {x: {'n': st1[x - 1].n, 'L': st1[x - 1].L, 'p_exact': lc_pvalue(st1[x - 1].L, st1[x - 1].n)}
                              for x in range(1, 23)},
        'F2_EM_lehmer_GF37': {'n': st2.n, 'L': st2.L, 'L_minus_n_over_2': st2.L - st2.n / 2, 'p_exact': lc_pvalue(st2.L, st2.n, 37)},
        'F3_EM_lehmer_bits_GF2': {'n': st3.n, 'L': st3.L, 'L_minus_n_over_2': st3.L - st3.n / 2, 'p_exact': lc_pvalue(st3.L, st3.n, 2)},
    }
    print('LC', out['linear_complexity_full_streams']['F2_EM_lehmer_GF37'], out['linear_complexity_full_streams']['F3_EM_lehmer_bits_GF2'], flush=True)

    # predictions for 28.11.2026
    pred1 = sorted(F1(van, '2026-11-28'))
    out['prediction_28_11'] = {'game': 'VAN', 'numbers': pred1, 'formula': 'F1',
                               'f1_table': [{'x': r[3], 'pred_bit': r[0], 'n_minus_2L': r[1], 'L': r[4]} for r in f1_scores(van)]}
    out['other_predictions_28_11'] = {'EM_F2': sorted(F2(em, '2026-11-28')), 'EM_F3': sorted(F3(em, '2026-11-28'))}
    print('pred', out['prediction_28_11']['numbers'], out['other_predictions_28_11'], flush=True)

    # D1 NIST battery
    d1 = {}
    d1['VAN_set'] = battery_long(bits_from([set_rank(d['main']) for d in van], 2 ** 19, 19))
    d1['EM_set'] = battery_long(bits_from([set_rank(d['main']) for d in em], 2 ** 22, 22))
    d1['VAN_ord'] = battery_long(bits_from([ord_rank(d['order'], 22) for d in van], 2 ** 44, 44))
    d1['EM_ord'] = battery_long(bits_from([ord_rank(d['order'], 33) for d in em], 2 ** 34, 34))
    d1['VAN_per_number'] = {x: battery_short(np.array([1 if x in d['main'] else 0 for d in van], np.uint8)) for x in range(1, 23)}
    pv = []
    for k in ('VAN_set', 'EM_set', 'VAN_ord', 'EM_ord'):
        pv += [v for t, v in d1[k].items() if t not in ('n_bits', 'L', 'L_minus_n_over_2')]
    for x in range(1, 23):
        pv += [v for t, v in d1['VAN_per_number'][x].items() if t not in ('L', 'L_minus_n_over_2')]
    nlow = sum(p < 0.01 for p in pv)
    d1['summary'] = {'n_pvalues': len(pv), 'n_below_0.01': nlow, 'expected_below_0.01': 0.01 * len(pv),
                     'binom_p_n_below_0.01': binom_sf(nlow, len(pv), 0.01), 'min_p': min(pv),
                     'n_below_0.05': sum(p < 0.05 for p in pv)}
    out['D1_NIST'] = d1; print('D1', d1['summary'], flush=True)
    for k in ('VAN_set', 'EM_set', 'VAN_ord', 'EM_ord'): print('  ', k, {t: round(v, 4) for t, v in d1[k].items()})

    if '--skip-d2' not in sys.argv:
        out['D2_LCG_bruteforce'] = run_d2(van)
        print('D2 confirmed:', out['D2_LCG_bruteforce']['confirmed_hypotheses'],
              'matched:', {h: v for h, v in out['D2_LCG_bruteforce']['draws_matched_per_hypothesis'].items() if v}, flush=True)
    out['runtime_s'] = time.time() - t0
    json.dump(clean(out), open(OUT, 'w'), ensure_ascii=False, indent=1)
    print('saved', OUT, f'{time.time() - t0:.0f}s')

if __name__ == '__main__':
    main()
