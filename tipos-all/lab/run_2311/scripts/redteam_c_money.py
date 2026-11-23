"""Red team, attack (c): independent money estimate for the final tickets (P3) + (f) ticket alternatives.
python3 -I redteam_c_money.py -> ../redteam_c.json   (about 1-3 min)"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from redteam_common import *
from redteam_model import *

T0 = time.time()
rng = np.random.default_rng(20261123)
ALL = np.arange(N)
NB = 400
out = {}

# ---------------- inputs
FPOOL = pool_shares((DATES >= '2026-01-01') & ~PREM)
out['pool_shares_2026_normal'] = FPOOL; out['pool_sum'] = sum(FPOOL.values())
SH = {'claim_pooled_all_eras(contaminated by 1-4 era)': None,
      'post_era_all': extra_shares(np.ones(N, bool)),
      '2026_only': extra_shares(DATES >= '2026-01-01'),
      '2026H2_only': extra_shares(DATES >= '2026-07-01')}
# reproduce the pooled-all-eras estimate used by P1 (pre-era draws counted with extras 1-4)
sh_pool = np.zeros(7)
for x in range(1, 8):
    ii = np.where(PB == x)[0]
    n1 = sum((W1[m][ii] * (POST[ii] | (m > 3))).sum() for m in (3, 4, 5))
    nt = sum((W[m][ii] * (POST[ii] | (m > 3))).sum() for m in (3, 4, 5))
    sh_pool[x - 1] = n1 / nt
SH['claim_pooled_all_eras(contaminated by 1-4 era)'] = sh_pool
out['extra_rel_popularity'] = {k: [round(float(v), 3) for v in 7 * s / s.sum()] for k, s in SH.items()}
print(out['extra_rel_popularity'])

# ---------------- models
VARIANTS = {'ridge_LOO_linear_pairs': dict(pairs='linear'),
            'ridge_LOO_dummy_pairs(saturating)': dict(pairs='dummy'),
            'ridge_LOO_no_pair_term': dict(pairs='none'),
            'ridge_LOO_linear_pairs_5match_numbers_from_4match': dict(pairs='linear', pool45=True)}
FITS = {k: fit_all(ALL, **v) for k, v in VARIANTS.items()}
FITS['ridge_LOO_linear_pairs_post_era_only'] = fit_all(np.where(POST)[0], pairs='linear')
FITS['ridge_LOO_linear_pairs_2025_2026_only'] = fit_all(np.where(DATES >= '2025-01-01')[0], pairs='linear')
out['lambda_chosen'] = {k: {m: f[m]['lam'] for m in (3, 4, 5)} for k, f in FITS.items()}
out['pair_gamma'] = {k: {m: [round(float(g), 4) for g in f[m]['gamma']] for m in (3, 4, 5)} for k, f in FITS.items()}
print('lambdas', out['lambda_chosen'])

TICKETS = {'FINAL': FINAL, 'RUNNER_UP': RUNNER,
           'agent_extra_earlier (1 2 14 20 22 23+6 / 8 10 15 16 18 19+5)': ([1, 2, 14, 20, 22, 23], 6, [8, 10, 15, 16, 18, 19], 5)}


def gain(fits, sh, tk, Acache=None):
    fa, xa, fb, xb = tk
    A, Ar = A_of_fields([fa, fb], fits) if Acache is None else Acache
    K = K_extra(sh, FPOOL); Kb = K.mean(1)
    ev = (A[0] @ K[:, xa - 1] + A[1] @ K[:, xb - 1]) / 2; evr = Ar @ Kb
    main_only = (A[0] @ Kb + A[1] @ Kb) / 2 / evr - 1
    return {'gain_vs_random_pct': float(100 * (ev / evr - 1)), 'main_numbers_only_pct': float(100 * main_only),
            'extra_only_pct': float(100 * ((A.mean(0) @ (K[:, xa - 1] + K[:, xb - 1]) / 2) / (A.mean(0) @ Kb) - 1)),
            'tier_factor_vs_random': [float(v) for v in A.mean(0) / Ar], 'EV_tiers3to5_per_EUR': float(ev),
            'EV_random_field': float(evr)}

# DP vs brute-force check
f0 = FITS['ridge_LOO_linear_pairs']
for fld in (FINAL[0], FINAL[2]):
    Sm = np.zeros((1, 27), bool); Sm[0, np.array(fld) - 1] = True
    a_dp = dp_A(Sm, f0)[0]; a_bf, _ = A_of_fields([fld], f0)
    assert np.allclose(a_dp, a_bf[0], rtol=1e-6), (a_dp, a_bf)
print('DP check ok', time.time() - T0)

res = {}
for vk, fits in FITS.items():
    for tk_name, tk in TICKETS.items():
        A = A_of_fields([tk[0], tk[2]], fits)
        for sk, sh in SH.items():
            if vk != 'ridge_LOO_linear_pairs' and sk not in ('2026_only',):
                continue
            res[f'{vk}|{sk}|{tk_name}'] = gain(fits, sh, tk, A)
for k, v in res.items():
    print(k, round(v['gain_vs_random_pct'], 2), round(v['main_numbers_only_pct'], 2), round(v['extra_only_pct'], 2),
          [round(x, 3) for x in v['tier_factor_vs_random']])
out['point_estimates'] = res

# ---------------- bootstrap over draws (lambda fixed at full-data value), final vs random and vs runner-up
lams = {m: f0[m]['lam'] for m in (3, 4, 5)}
bs = {'final': [], 'runner': [], 'final_main_only': [], 'final_extra_only': [], 'tier': []}
for b in range(NB):
    ib = rng.integers(0, N, N)
    fb = fit_all(ib, lams=lams)
    shb = extra_shares(np.isin(np.arange(N), ib[DATES[ib] >= '2026-01-01']))   # 2026 extra shares (set, not weights)
    # weights matter: recompute shares with multiplicity
    n1 = np.zeros(7); nt = np.zeros(7)
    for t in ib:
        if DATES[t] >= '2026-01-01':
            n1[PB[t] - 1] += sum(W1[m][t] for m in (3, 4, 5)); nt[PB[t] - 1] += sum(W[m][t] for m in (3, 4, 5))
    shb = np.where(nt > 0, n1 / np.maximum(nt, 1), SH['post_era_all'])   # extra 7: only 5 draws in 2026
    A = A_of_fields([FINAL[0], FINAL[2], RUNNER[0], RUNNER[2]], fb)
    gF = gain(fb, shb, FINAL, (A[0][:2], A[1])); gR = gain(fb, shb, RUNNER, (A[0][2:], A[1]))
    bs['final'].append(gF['gain_vs_random_pct']); bs['runner'].append(gR['gain_vs_random_pct'])
    bs['final_main_only'].append(gF['main_numbers_only_pct']); bs['final_extra_only'].append(gF['extra_only_pct'])
    bs['tier'].append(gF['tier_factor_vs_random'])
    if b % 100 == 0:
        print('boot', b, round(time.time() - T0), flush=True)
q = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
diff = np.array(bs['final']) - np.array(bs['runner'])
out['bootstrap'] = {'reps': NB, 'extras': '2026-only shares, resampled',
                    'final_gain_pct': {'mean': float(np.mean(bs['final'])), 'CI95': q(bs['final'])},
                    'final_main_only_pct': {'mean': float(np.mean(bs['final_main_only'])), 'CI95': q(bs['final_main_only'])},
                    'final_extra_only_pct': {'mean': float(np.mean(bs['final_extra_only'])), 'CI95': q(bs['final_extra_only'])},
                    'runner_gain_pct': {'mean': float(np.mean(bs['runner'])), 'CI95': q(bs['runner'])},
                    'final_minus_runner_pp': {'mean': float(diff.mean()), 'CI95': q(diff), 'P_final_better': float(np.mean(diff > 0))},
                    'tier_factors_CI95': [q(np.array(bs['tier'])[:, c]) for c in range(3)]}
print(json.dumps(out['bootstrap'], indent=0))

# ---------------- honest selection check: choose on one half, evaluate on the other
COMB1 = COMBS.astype(int) + 1
VALID = np.array([not ap3(c) for c in COMB1])   # no 3-term AP (implies no run of 3)
VID = np.where(VALID)[0]; SM = DB[VID]
NPF = NPAIR_ALL[VID]
MASK = (SM.astype(np.int64) * (1 << np.arange(27, dtype=np.int64))).sum(1)
out['valid_fields'] = int(len(VID))


def best_pair(EVX, allowed, top=2500):
    """EVX (nvalid, 7): EV per field and extra; allowed: bool over valid fields. extras distinct in {5,6,7}."""
    best = (-np.inf, None)
    for xa in (4, 5, 6):
        for xb in (4, 5, 6):
            if xb == xa:
                continue
            ea = np.where(allowed, EVX[:, xa], -np.inf); eb = np.where(allowed, EVX[:, xb], -np.inf)
            ia = np.argsort(-ea)[:top]; ib = np.argsort(-eb)[:top]
            tot = ea[ia][:, None] + eb[ib][None, :]
            tot = np.where((MASK[ia][:, None] & MASK[ib][None, :]) == 0, tot, -np.inf)
            i, j = np.unravel_index(np.argmax(tot), tot.shape)
            bound = max(ea[ia[0]] + eb[ib[-1]], ea[ia[-1]] + eb[ib[0]])
            if tot[i, j] > best[0]:
                best = (float(tot[i, j]), (ia[i], xa, ib[j], xb), bool(tot[i, j] >= bound))
    v, (i, xa, j, xb), ok = best
    return {'field1': [int(c) + 1 for c in np.where(SM[i])[0]], 'extra1': xa + 1,
            'field2': [int(c) + 1 for c in np.where(SM[j])[0]], 'extra2': xb + 1, 'EV_mean': v / 2, 'bound_ok': ok}


def ev_valid(fits, sh):
    A = dp_A(SM, fits); return A @ K_extra(sh, FPOOL), A


post = np.where(POST)[0]
halves = {'H1(2024-03..2025-07)': np.arange(0, N // 2), 'H2(2025-07..2026-11)': np.arange(N // 2, N)}
half_fits = {k: fit_all(v) for k, v in halves.items()}
half_sh = {k: extra_shares(np.isin(np.arange(N), v)) for k, v in halves.items()}
honest = {}
for a, b in (('H1(2024-03..2025-07)', 'H2(2025-07..2026-11)'), ('H2(2025-07..2026-11)', 'H1(2024-03..2025-07)')):
    EVa, _ = ev_valid(half_fits[a], half_sh[a])
    bp = best_pair(EVa, np.ones(len(VID), bool))
    tk = (bp['field1'], bp['extra1'], bp['field2'], bp['extra2'])
    honest[f'choose_on_{a}_eval_on_{b}'] = {'pair': tk, 'gain_on_choice_half': gain(half_fits[a], half_sh[a], tk)['gain_vs_random_pct'],
                                            'gain_on_eval_half': gain(half_fits[b], half_sh[b], tk)['gain_vs_random_pct'],
                                            'FINAL_gain_on_eval_half': gain(half_fits[b], half_sh[b], FINAL)['gain_vs_random_pct']}
    print(honest[f'choose_on_{a}_eval_on_{b}'], flush=True)
out['honest_split_half'] = honest

# ---------------- (f) alternatives under the red-team model (full data, 2026 extras)
sh26 = SH['2026_only']
EVX, AV = ev_valid(f0, sh26)
least12 = set(CLAIM_ORDER[:12]); least15 = set(CLAIM_ORDER[:15])
in12 = np.array([set(np.where(r)[0] + 1) <= least12 for r in SM]); in15 = np.array([set(np.where(r)[0] + 1) <= least15 for r in SM])
cons = {'user_constraints_only': np.ones(len(VID), bool),
        'max2_pairs_per_field': NPF <= 2,
        'max1_pair_per_field': NPF <= 1,
        'no_pairs': NPF == 0,
        'only_12_least_popular_numbers': in12,
        'only_12_least_popular_max2_pairs': in12 & (NPF <= 2),
        'only_15_least_popular_max2_pairs': in15 & (NPF <= 2)}
alts = {}
for k, allowed in cons.items():
    bp = best_pair(EVX, allowed)
    alts[k] = bp
EVr = float(sum(np.exp(-u_all(f0[m])).mean() * np.exp(u_all(f0[m])).mean() * K_extra(sh26, FPOOL)[c].mean()
                for c, m in enumerate((3, 4, 5))))
for k in alts:
    alts[k]['gain_vs_random_pct'] = 100 * (alts[k]['EV_mean'] / EVr - 1)
alts['FINAL'] = {'gain_vs_random_pct': gain(f0, sh26, FINAL)['gain_vs_random_pct']}
alts['RUNNER_UP'] = {'gain_vs_random_pct': gain(f0, sh26, RUNNER)['gain_vs_random_pct']}
for k, v in alts.items():
    print(k, {kk: vv for kk, vv in v.items() if kk != 'EV_mean'})
# bootstrap the difference FINAL - best alternative of each constraint class (fields fixed)
alt_tk = {k: (v['field1'], v['extra1'], v['field2'], v['extra2']) for k, v in alts.items() if 'field1' in v}
dif = {k: [] for k in alt_tk}
rng2 = np.random.default_rng(7)
for b in range(200):
    ib = rng2.integers(0, N, N); fb = fit_all(ib, lams=lams)
    n1 = np.zeros(7); nt = np.zeros(7)
    for t in ib:
        if DATES[t] >= '2026-01-01':
            n1[PB[t] - 1] += sum(W1[m][t] for m in (3, 4, 5)); nt[PB[t] - 1] += sum(W[m][t] for m in (3, 4, 5))
    shb = np.where(nt > 0, n1 / np.maximum(nt, 1), SH['post_era_all'])
    flds = [FINAL[0], FINAL[2]] + [f for tk in alt_tk.values() for f in (tk[0], tk[2])]
    A, Ar = A_of_fields(flds, fb)
    gF = gain(fb, shb, FINAL, (A[:2], Ar))['gain_vs_random_pct']
    for r, (k, tk) in enumerate(alt_tk.items()):
        dif[k].append(gF - gain(fb, shb, tk, (A[2 + 2 * r: 4 + 2 * r], Ar))['gain_vs_random_pct'])
for k in alt_tk:
    a = np.array(dif[k]); alts[k]['FINAL_minus_this_pp'] = {'mean': float(a.mean()), 'CI95': q(a), 'P_final_better': float(np.mean(a > 0))}
    print(k, alts[k]['FINAL_minus_this_pp'])
out['alternatives'] = alts

# ---------------- translate to return per 1 EUR (normal month, 6+1 at 3% PV)
top3 = 0.1802; top0 = 0.2006            # returns.md, Monday ~104.8k bets
base_low = out['pool_sum']               # population-average low tiers
g = res['ridge_LOO_linear_pairs|2026_only|FINAL']
evF = g['EV_tiers3to5_per_EUR']
out['return_per_EUR'] = {'population_average_3pct': base_low + top3, 'population_average_0pct': base_low + top0,
                         'random_field_3pct': g['EV_random_field'] + top3,
                         'FINAL_3pct': evF + top3, 'FINAL_0pct': evF + top0,
                         'FINAL_minus_population_avg_pp': 100 * (evF - base_low),
                         'note': 'top tiers without popularity bonus (~+0.003 more for unpopular fields per P3)'}
print(out['return_per_EUR'])
out['runtime_s'] = time.time() - T0
json.dump(out, open(os.path.join(BASE, 'redteam_c.json'), 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
