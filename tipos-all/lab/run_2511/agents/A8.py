"""A8 — PSEUDO-RANDOM GENERATOR / SEED SEARCH (see A8_prereg.md). Run: python3 -I A8.py"""
import sys, json, random, datetime as dt
from math import comb
from zoneinfo import ZoneInfo
import numpy as np
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2511')
from harness import evaluate, DRAWS, PMF

OUT = '/home/user/Mobil/tipos-all/lab/run_2511/agents/A8.json'
NEXT_DATE = '2026-11-25'
GENS = ['PY', 'RS', 'PCG']
SEEDS = ['YMD', 'DMY', 'YMD6', 'UDAY', 'TS_LOC', 'TS_CET']
METHODS = ['SAMPLE', 'SHUF', 'SEQ', 'REJ']
COMBOS = [(g, s, m) for g in GENS for s in SEEDS for m in METHODS]
BRA = ZoneInfo('Europe/Bratislava')
CET = dt.timezone(dt.timedelta(hours=1))


def seed_of(fmt, date_str):
    d = dt.date.fromisoformat(date_str)
    if fmt == 'YMD': return int(d.strftime('%Y%m%d'))
    if fmt == 'DMY': return int(d.strftime('%d%m%Y'))
    if fmt == 'YMD6': return int(d.strftime('%y%m%d'))
    if fmt == 'UDAY': return (d - dt.date(1970, 1, 1)).days
    if fmt == 'TS_LOC': return int(dt.datetime(d.year, d.month, d.day, 18, 0, 0, tzinfo=BRA).timestamp())
    if fmt == 'TS_CET': return int(dt.datetime(d.year, d.month, d.day, 18, 0, 0, tzinfo=CET).timestamp())
    raise ValueError(fmt)


def gen_output(combo, date_str):
    g, s, m = combo
    seed = seed_of(s, date_str)
    if g == 'PY':
        r = random.Random(seed)
        if m == 'SAMPLE': out = r.sample(range(1, 23), 11)
        elif m == 'SHUF':
            a = list(range(1, 23)); r.shuffle(a); out = a[:11]
        elif m == 'SEQ':
            pool = list(range(1, 23)); out = []
            for _ in range(11):
                x = r.choice(pool); pool.remove(x); out.append(x)
        else:
            out = []
            while len(out) < 11:
                x = r.randint(1, 22)
                if x not in out: out.append(x)
    else:
        r = np.random.RandomState(seed) if g == 'RS' else np.random.default_rng(seed)
        ri = (lambda: int(r.randint(1, 23))) if g == 'RS' else (lambda: int(r.integers(1, 23)))
        if m == 'SAMPLE': out = r.choice(np.arange(1, 23), 11, replace=False).tolist()
        elif m == 'SHUF':
            a = np.arange(1, 23); r.shuffle(a); out = a[:11].tolist()
        elif m == 'SEQ':
            pool = list(range(1, 23)); out = []
            for _ in range(11):
                x = int(r.choice(pool)); pool.remove(x); out.append(x)
        else:
            out = []
            while len(out) < 11:
                x = ri()
                if x not in out: out.append(x)
    out = [int(x) for x in out]
    assert len(set(out)) == 11 and all(1 <= x <= 22 for x in out)
    return out


DATES = [d['date'] for d in DRAWS] + [NEXT_DATE]
CACHE = {c: [set(gen_output(c, D)) for D in DATES] for c in COMBOS}
MAINS = [set(d['main']) for d in DRAWS]
OV = {c: np.array([len(CACHE[c][t] & MAINS[t]) for t in range(len(DRAWS))]) for c in COMBOS}

# ---------------- Step 1: search on draws 0..29 only ----------------
P9 = float(PMF[9:].sum())       # P(overlap >= 9)
P2 = float(PMF[:3].sum())       # P(overlap <= 2)


def binom_sf(k, n, p):
    return float(sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1)))


search = []
for i, c in enumerate(COMBOS):
    o = OV[c][:30]
    search.append({'combo': '/'.join(c), 'idx': i, 'n_ge9': int((o >= 9).sum()), 'n_le2': int((o <= 2).sum()),
                   'mean': float(o.mean()), 'dist': np.bincount(o, minlength=12).tolist()})
best = sorted(search, key=lambda r: (-r['n_ge9'], -r['mean'], r['idx']))[0]
best_mean = sorted(search, key=lambda r: (-r['mean'], r['idx']))[0]
worst_mean = sorted(search, key=lambda r: (r['mean'], r['idx']))[0]
max_ge9 = best['n_ge9']; max_le2 = max(r['n_le2'] for r in search)
p_best_single = binom_sf(max_ge9, 30, P9)
p_best_fw = 1 - (1 - p_best_single) ** len(COMBOS)
p_le2_single = binom_sf(max_le2, 30, P2)
p_le2_fw = 1 - (1 - p_le2_single) ** len(COMBOS)
# expected mean overlap 5.5, sd per draw
sd1 = float(np.sqrt(((np.arange(12) - 5.5) ** 2 * PMF).sum()))
step1 = {'n_combos': len(COMBOS), 'P_ge9': P9, 'expected_ge9_per_combo': 30 * P9,
         'combos_with_ge9': [r['combo'] + ':' + str(r['n_ge9']) for r in search if r['n_ge9'] > 0],
         'n_combos_with_any_ge9': sum(r['n_ge9'] > 0 for r in search),
         'expected_combos_with_any_ge9': len(COMBOS) * (1 - (1 - P9) ** 30),
         'max_ge9': max_ge9, 'p_max_ge9_single': p_best_single, 'p_max_ge9_familywise': p_best_fw,
         'max_le2': max_le2, 'p_max_le2_single': p_le2_single, 'p_max_le2_familywise': p_le2_fw,
         'best_combo': best, 'best_mean_combo': best_mean, 'worst_mean_combo': worst_mean,
         'mean_overlap_range': [min(r['mean'] for r in search), max(r['mean'] for r in search)],
         'null_sd_mean30': sd1 / np.sqrt(30)}

C1 = COMBOS[best['idx']]; C2 = COMBOS[best_mean['idx']]; C3 = COMBOS[worst_mean['idx']]


def date_for(past):          # only the date of the evaluated draw is read (public in advance)
    return DRAWS[len(past)]['date'] if len(past) < len(DRAWS) else NEXT_DATE


def make_rule(combo, complement):
    def rule(past):
        out = set(gen_output(combo, date_for(past)))
        return sorted(set(range(1, 23)) - out) if complement else sorted(out)
    return rule


R1 = make_rule(C1, True); R2 = make_rule(C2, True); R3 = make_rule(C3, False)
defs = {'R1': f'complement of {"/".join(C1)} output for draw date (best by #overlap>=9 on draws 0..29)',
        'R2': f'complement of {"/".join(C2)} output for draw date (highest mean overlap on draws 0..29)',
        'R3': f'direct output of {"/".join(C3)} for draw date (lowest mean overlap on draws 0..29)'}
rules = []
for name, f in [('R1', R1), ('R2', R2), ('R3', R3)]:
    r = evaluate(f, name); r['definition'] = defs[name]; rules.append(r)

# ---------------- distribution of the best combo vs hypergeometric ----------------
BINS = [(0, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 11)]
PB = np.array([PMF[a:b + 1].sum() for a, b in BINS])


def binned(o):
    return np.array([((o >= a) & (o <= b)).sum() for a, b in BINS])


def chi2(cnt, n):
    e = n * PB
    return float(((cnt - e) ** 2 / e).sum())


def dist_report(o, label, rng):
    n = len(o); cnt = binned(o); stat = chi2(cnt, n)
    sims = rng.hypergeometric(11, 11, 11, size=(20000, n))
    sc = np.stack([((sims >= a) & (sims <= b)).sum(1) for a, b in BINS], 1)
    ss = (((sc - n * PB) ** 2) / (n * PB)).sum(1)
    return {'sample': label, 'n': n, 'counts_by_overlap_0..11': np.bincount(o, minlength=12).tolist(),
            'expected_by_overlap_0..11': [round(float(n * p), 2) for p in PMF],
            'bins': ['0-3', '4', '5', '6', '7', '8-11'], 'binned_obs': cnt.tolist(),
            'binned_exp': [round(float(n * p), 2) for p in PB], 'chi2': stat,
            'p_chi2_mc': float((ss >= stat - 1e-12).mean()), 'mean_overlap': float(o.mean()),
            'n_ge9': int((o >= 9).sum()), 'expected_ge9': n * P9}


rng = np.random.default_rng(12345)
dist = [dist_report(OV[C1][30:], 'draws 30..411', rng), dist_report(OV[C1], 'all 412 draws', rng)]

# ---------------- descriptive: all 72 combos on draws 30..411 ----------------
allc = [{'combo': '/'.join(c), 'n_ge9_eval': int((OV[c][30:] >= 9).sum()), 'mean_eval': float(OV[c][30:].mean())}
        for c in COMBOS]
desc = {'expected_ge9_per_combo_eval': 382 * P9, 'total_ge9_all_combos_eval': sum(r['n_ge9_eval'] for r in allc),
        'expected_total_ge9_eval': 72 * 382 * P9, 'max_ge9_eval': max(r['n_ge9_eval'] for r in allc),
        'mean_eval_range': [min(r['mean_eval'] for r in allc), max(r['mean_eval'] for r in allc)],
        'per_combo': allc}

ticket = sorted(int(x) for x in R1(DRAWS))
res = {'id': 'A8', 'family': 'PSEUDO-RANDOM GENERATOR / SEED SEARCH', 'rules': rules, 'ticket_25_11': ticket,
       'step1_search_draws_0_29': step1, 'best_combo_overlap_distribution': dist, 'descriptive_all_combos': desc,
       'tickets_25_11_all_rules': {'R1': ticket, 'R2': sorted(R2(DRAWS)), 'R3': sorted(R3(DRAWS))},
       'seeds_25_11': {s: seed_of(s, NEXT_DATE) for s in SEEDS}}


def plain(x):
    if isinstance(x, dict): return {k: plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [plain(v) for v in x]
    if isinstance(x, np.integer): return int(x)
    if isinstance(x, np.floating): return float(x)
    return x


json.dump(plain(res), open(OUT, 'w'), indent=1, ensure_ascii=False)
s1 = step1
print('Step1: combos with >=9 in 0..29:', s1['combos_with_ge9'], f"(expected {s1['expected_combos_with_any_ge9']:.1f} combos)")
print(f"max_ge9={max_ge9} p_single={p_best_single:.3f} p_fw={p_best_fw:.3f}; max_le2={max_le2} p_fw={p_le2_fw:.3f}")
print('best', best['combo'], best['n_ge9'], round(best['mean'], 3), '| best_mean', best_mean['combo'], round(best_mean['mean'], 3),
      '| worst_mean', worst_mean['combo'], round(worst_mean['mean'], 3))
for r in rules:
    print(r['rule'], r['definition'], f"mean={r['mean_hits']:.3f} p_mean={r['p_mean_lower']:.4f} le3={r['n_hits_le3']} p_le3={r['p_le3']:.4f} "
          f"zero={r['n_zero']} won={r['won_eur']} cost={r['cost_eur']}")
for d in dist:
    print(d['sample'], d['binned_obs'], d['binned_exp'], f"chi2={d['chi2']:.2f} p={d['p_chi2_mc']:.3f} mean={d['mean_overlap']:.3f} ge9={d['n_ge9']}")
print('desc:', {k: v for k, v in desc.items() if k != 'per_combo'})
print('ticket 25.11 (R1):', ticket, '| all:', res['tickets_25_11_all_rules'])
