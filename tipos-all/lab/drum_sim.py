"""'Point simulation of the drum' for Loto 5 z 35.
Part 1: virtual drum (xorshift32) seeds that replay history, rolled one draw forward.
Part 2: date-seeded standard generators.
Part 3: physical toy drum (chaotic billiard) and sensitivity to initial conditions.
Usage: python3 -I drum_sim.py l535.json out.json
"""
import json, sys, math, random, datetime, time
import numpy as np

raw = [r for r in json.load(open(sys.argv[1])) if r['raw'] and len(r['raw'].get('Zrebovanie', [])) == 5]
dates = [r['date'] for r in raw]
draws = [sorted(int(x) for x in r['raw']['Zrebovanie']) for r in raw]
T = len(draws)
def tomask(d):
    m = 0
    for v in d: m |= 1 << (v - 1)
    return m
hist = np.array([tomask(d) for d in draws], dtype=np.uint64)
out = {'draws': T, 'last': {'date': dates[-1], 'numbers': draws[-1]}}

# ---------------------------------------------------------------- Part 1: virtual drum
def drum_chunk(seeds, mult):
    s = (seeds.astype(np.uint64) * np.uint64(mult) + np.uint64(0x9E3779B9)) & np.uint64(0xFFFFFFFF)
    s = s.astype(np.uint32); s[s == 0] = 1
    for _ in range(4):  # warm-up
        s ^= s << np.uint32(13); s ^= s >> np.uint32(17); s ^= s << np.uint32(5)
    n = len(seeds)
    mA = np.zeros(n, np.uint64); cA = np.zeros(n, np.int8); mB = np.zeros(n, np.uint64); cB = np.zeros(n, np.int8)
    one = np.uint64(1)
    for _ in range(34):
        s ^= s << np.uint32(13); s ^= s >> np.uint32(17); s ^= s << np.uint32(5)
        bit = one << (s % np.uint32(35)).astype(np.uint64)
        inA = cA < 5
        addA = inA & ((mA & bit) == 0); mA |= np.where(addA, bit, np.uint64(0)); cA += addA
        inB = (~inA) & (cB < 5)
        addB = inB & ((mB & bit) == 0); mB |= np.where(addB, bit, np.uint64(0)); cB += addB
    ok = (cA == 5) & (cB == 5)
    return mA, mB, ok

def virtual_drum(mult, n_seeds=1 << 24, chunk=1 << 21):
    targets = np.unique(hist)
    found = []  # (seed, maskA, maskB)
    for start in range(0, n_seeds, chunk):
        seeds = np.arange(start + 1, start + chunk + 1, dtype=np.uint64)
        mA, mB, ok = drum_chunk(seeds, mult)
        hit = ok & np.isin(mA, targets)
        found.append(np.column_stack([seeds[hit], mA[hit], mB[hit]]))
    return np.vstack(found)

def popc(x): return int(bin(int(x)).count('1'))
res1 = {}
for label, mult in [('drum A', 2654435761), ('drum B', 2246822519)]:
    t0 = time.time()
    F = virtual_drum(mult)
    by_mask = {}
    for sd, a, b in F: by_mask.setdefault(int(a), []).append((int(sd), int(b)))
    covered = sum(1 for m in hist if int(m) in by_mask)
    # (a) any seed replaying two consecutive draws?
    pairs = {(int(hist[t]), int(hist[t + 1])) for t in range(T - 1)}
    chain2 = sum(1 for sd, a, b in F if (int(a), int(b)) in pairs)
    # (b) roll every matching seed one draw forward and compare with what really came next
    hits = []; cons_hits = []
    for t in range(T - 1):
        lst = by_mask.get(int(hist[t]), [])
        if not lst: continue
        nxt = int(hist[t + 1])
        hits += [popc(b & nxt) for _, b in lst]
        cnt = np.zeros(35)
        for _, b in lst:
            for j in range(35):
                if b >> j & 1: cnt[j] += 1
        top = np.argsort(-(cnt + np.random.default_rng(t).random(35) * 1e-6))[:5]
        cons_hits.append(sum(1 for j in top if nxt >> int(j) & 1))
    hits = np.array(hits); cons_hits = np.array(cons_hits)
    var1 = 5 * (5 / 35) * (30 / 35) * (30 / 34)
    z_cons = (cons_hits.sum() - len(cons_hits) * 25 / 35) / math.sqrt(len(cons_hits) * var1)
    # (c) prediction for 06.11.2026 from seeds replaying 04.11.2026
    last = by_mask.get(int(hist[-1]), [])
    cnt = np.zeros(35)
    for _, b in last:
        for j in range(35):
            if b >> j & 1: cnt[j] += 1
    pred = sorted((np.argsort(-cnt)[:5] + 1).tolist())
    res1[label] = {'seeds_scanned': 1 << 24, 'matches_total': int(len(F)), 'draws_with_a_matching_seed': covered,
                   'seeds_per_draw_avg': float(len(F) / max(1, covered)), 'seeds_replaying_two_draws_in_a_row': chain2,
                   'rolled_forward_mean_hits': float(hits.mean()), 'rolled_forward_n': int(len(hits)),
                   'consensus_mean_hits': float(cons_hits.mean()), 'consensus_z': float(z_cons),
                   'seeds_matching_last_draw': len(last), 'prediction_for_2026_11_06': pred,
                   'prediction_votes': {str(j + 1): int(cnt[j]) for j in np.argsort(-cnt)[:8]},
                   'max_vote_share': float(cnt.max() / max(1, len(last))), 'seconds': round(time.time() - t0, 1)}
    print(label, res1[label], file=sys.stderr)
bits = T * math.log2(math.comb(35, 5))
out['virtual_drum'] = res1
out['information'] = {'history_bits': bits, 'expected_32bit_seeds_replaying_2_draws': 2 ** 32 / math.comb(35, 5) ** 2,
                      'expected_32bit_seeds_replaying_3_draws': 2 ** 32 / math.comb(35, 5) ** 3,
                      'expected_64bit_seeds_replaying_4_draws': 2 ** 64 / math.comb(35, 5) ** 4}

# ---------------------------------------------------------------- Part 2: date-seeded generators
gens = {}
def check(fn):
    m3 = 0; m5 = 0
    for d, dr in zip(dates, draws):
        p = set(fn(d)); k = len(p & set(dr)); m3 += k >= 3; m5 += k == 5
    return {'ge3': m3, 'exact': m5}
ymd = lambda d: int(d.replace('-', ''))
ordn = lambda d: datetime.date.fromisoformat(d).toordinal()
def py_sample(seed): r = random.Random(seed); return r.sample(range(1, 36), 5)
gens['python random, seed YYYYMMDD'] = check(lambda d: py_sample(ymd(d)))
gens['python random, seed day ordinal'] = check(lambda d: py_sample(ordn(d)))
gens['numpy default_rng, seed YYYYMMDD'] = check(lambda d: (np.random.default_rng(ymd(d)).choice(35, 5, replace=False) + 1).tolist())
gens['numpy RandomState, seed YYYYMMDD'] = check(lambda d: (np.random.RandomState(ymd(d) % 2 ** 32).choice(35, 5, replace=False) + 1).tolist())
p3 = (math.comb(5, 3) * math.comb(30, 2) + math.comb(5, 4) * 30 + 1) / math.comb(35, 5)
out['date_seeded'] = {'results': gens, 'expected_ge3_by_chance': T * p3, 'expected_exact_by_chance': T / math.comb(35, 5)}

# ---------------------------------------------------------------- Part 3: physical toy drum (chaotic billiard)
R, OC, OR = 1.0, (0.32, 0.05), 0.27      # drum radius, off-centre obstacle -> chaotic mixing
WIN, TMIX = 0.035, 150.0                   # exit window half-width (rad) at the bottom, mixing time
def step(px, py, dx, dy):
    b = px * dx + py * dy; c = px * px + py * py - R * R
    t_out = -b + math.sqrt(max(b * b - c, 0.0))
    qx, qy = px - OC[0], py - OC[1]; b2 = qx * dx + qy * dy; c2 = qx * qx + qy * qy - OR * OR; disc = b2 * b2 - c2
    t_in = -b2 - math.sqrt(disc) if disc > 0 else -1.0
    if t_in > 1e-12 and t_in < t_out:
        hx, hy = px + t_in * dx, py + t_in * dy; nx, ny = (hx - OC[0]) / OR, (hy - OC[1]) / OR; t = t_in; wall = False
    else:
        hx, hy = px + t_out * dx, py + t_out * dy; nr = math.hypot(hx, hy); nx, ny = hx / nr, hy / nr; t = t_out; wall = True
    dn = dx * nx + dy * ny; dx, dy = dx - 2 * dn * nx, dy - 2 * dn * ny; nd = math.hypot(dx, dy)
    return hx, hy, dx / nd, dy / nd, t, wall

def run_ball(px, py, ang, max_b=6000):
    dx, dy = math.cos(ang), math.sin(ang); t = 0.0; path = []
    for b in range(max_b):
        px, py, dx, dy, dt, wall = step(px, py, dx, dy); t += dt; path.append((px, py))
        if wall and t > TMIX and abs(math.atan2(py, px) + math.pi / 2) < WIN:
            return t, path
    return float('inf'), path

def drum_draw(eps):
    rng = random.Random(20261106); res = []; paths = []
    for i in range(35):
        x0 = -0.5 + (i % 7) * 0.15 + eps; y0 = 0.2 + (i // 7) * 0.12; ang = rng.uniform(0, 2 * math.pi)
        texit, path = run_ball(x0, y0, ang); res.append((texit, i + 1)); paths.append(path)
    res.sort(); return sorted(n for _, n in res[:5]), paths

base, P0 = drum_draw(0.0)
phys = {'base_draw': base, 'perturbations': {}}
for eps in (1e-6, 1e-9, 1e-12, 1e-15):
    d, P1 = drum_draw(eps)
    # separation growth for ball 1
    sep = [math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(P0[0], P1[0])]
    first_big = next((k for k, s in enumerate(sep) if s > 0.1), None)
    phys['perturbations'][f'{eps:g}'] = {'draw': d, 'same_as_base': d == base, 'bounces_until_divergence': first_big}
# Lyapunov exponent per bounce from the 1e-12 run
d, P1 = drum_draw(1e-12)
sep = np.array([math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(P0[0], P1[0])])
k = np.arange(len(sep)); good = (sep > 1e-11) & (sep < 1e-2)
lam = float(np.polyfit(k[good], np.log(sep[good]), 1)[0]) if good.sum() > 5 else float('nan')
phys['lyapunov_per_bounce'] = lam
for B in (100, 1000):
    phys[f'precision_needed_m_for_{B}_bounces'] = float(0.3 * math.exp(-lam * B))  # drum radius ~0.3 m
out['physical_drum'] = phys
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
