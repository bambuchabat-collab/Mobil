"""Prize arithmetic for Extra vyplata (EV, 6/27 + 1/7) and Vsetko alebo nic (VAN, 11/22).

No number prediction here: exact odds by full enumeration + average return per 1 EUR from
published prize tables (data/ev.json, data/van.json).  Writes ../returns.json and ../returns.md.

Run:  python3 -I lab/run_2311/scripts/returns.py
Rules used (herny plan ciselnych loterii 2026, ucinny od 18.03.2026, cl. 29 a 34):
  EV : 1.50 EUR/field; prize fund 57.90 % of stakes; tiers 3..8 parimutuel 1.5/4.3/4.4/10.8/6.2/27.0 %
       of the fund; 6+1 = 480 000 EUR (2 winners: 480 000/2 each; >=3 winners: 720 000/n each),
       paid monthly over 10 years (lump sum if >=7 winners); 6+0 = 30 000 EUR shared (cap 30 000).
  VAN: 1.50 EUR; 11 or 0 hits share one 100 000 EUR; 10/1 -> 200, 9/2 -> 20, 8/3 -> 3 EUR fixed.
Note: field 'wins' in the data is the nominal prize FUND (57.9 % / 50.35 % of deposits), not money paid;
paid money is sum(prize * winners) over tiers.
"""
import json, math, os, statistics as st
from fractions import Fraction as F
from math import comb
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ev = json.load(open(os.path.join(RUN, 'data', 'ev.json')))
van = json.load(open(os.path.join(RUN, 'data', 'van.json')))
rng = np.random.default_rng(20261123)
OUT = {}

# ----------------------------------------------------------------------------- EV exact odds
NEV = comb(27, 6)            # 296 010 main combinations
TOT = NEV * 7                # 2 072 070 outcomes incl. extra number
TIERS = ['6+1', '6+0', '5+1', '5+0', '4+1', '4+0', '3+1', '3+0']   # best -> worst
LOW = TIERS[2:]
RANK = {t: i for i, t in enumerate(TIERS)}


def pmain(k, n=27):
    return F(comb(6, k) * comb(n - 6, 6 - k), comb(n, 6))


def ptier(t, m=7):            # m = size of extra-number drum
    k, e = int(t[0]), int(t[2])
    return pmain(k) * (F(1, m) if e else F(m - 1, m))


P1 = {t: ptier(t) for t in TIERS}
p_any_1 = sum(P1.values())


def tier(a, e):
    return f'{a}+{e}' if a >= 3 else None


def ev_pair(c, same_extra):
    """Two fields sharing c main numbers; extra numbers equal or different. Exact joint law."""
    joint = {}
    extra = [((1, 1), 1), ((0, 0), 6)] if same_extra else [((1, 0), 1), ((0, 1), 1), ((0, 0), 5)]
    for x in range(c + 1):
        for y in range(7 - c):
            for z in range(7 - c):
                w = 6 - x - y - z
                if w < 0 or w > 15 + c:
                    continue
                cnt = comb(c, x) * comb(6 - c, y) * comb(6 - c, z) * comb(15 + c, w)
                if not cnt:
                    continue
                a, b = x + y, x + z
                for (ea, eb), m in extra:
                    key = (tier(a, ea), tier(b, eb))
                    joint[key] = joint.get(key, 0) + cnt * m
    assert sum(joint.values()) == TOT
    return {k: F(v, TOT) for k, v in joint.items()}


def best(k):
    ts = [t for t in k if t]
    return min(ts, key=RANK.get) if ts else None


def summarize_pair(joint, prize=None):
    r = {}
    r['p_any'] = sum(p for k, p in joint.items() if best(k))
    r['p_both'] = sum(p for k, p in joint.items() if k[0] and k[1])
    r['p_6p1_either'] = sum(p for k, p in joint.items() if '6+1' in k)
    r['p_6main_either'] = sum(p for k, p in joint.items() if '6+1' in k or '6+0' in k)
    r['p_ge_5p0_either'] = sum(p for k, p in joint.items() if best(k) and RANK[best(k)] <= RANK['5+0'])
    r['p_ge_4p0_either'] = sum(p for k, p in joint.items() if best(k) and RANK[best(k)] <= RANK['4+0'])
    r['p_any_plus1_tier'] = sum(p for k, p in joint.items() if any(t and t.endswith('+1') for t in k))
    out = {k: float(v) for k, v in r.items()}
    out['p_any_frac'] = str(r['p_any'])
    out['one_in_6p1_either'] = round(1 / float(r['p_6p1_either'])) if r['p_6p1_either'] else None
    if prize:   # payout moments with given EUR value per tier
        def pay(k, keys):
            return sum(prize[t] for t in k if t in keys)
        for lab, keys in (('low', LOW), ('all', TIERS)):
            m1 = sum(float(p) * pay(k, keys) for k, p in joint.items())
            m2 = sum(float(p) * pay(k, keys) ** 2 for k, p in joint.items())
            out[f'mean_pay_{lab}'] = m1
            out[f'sd_pay_{lab}'] = math.sqrt(max(m2 - m1 * m1, 0))
        out['p_pay_ge_4eur'] = sum(float(p) for k, p in joint.items() if pay(k, TIERS) >= 4.0)
    return out


# ----------------------------------------------------------------------------- VAN exact odds
NV = comb(22, 11)            # 705 432
VP = {11: 100000, 10: 200, 9: 20, 8: 3, 3: 3, 2: 20, 1: 200, 0: 100000}


def van_pair(s, top_value=100000.0):
    r = 11 - s
    anyc = topc = ge20 = ge200 = ge4 = 0
    m1 = m2 = m1l = m2l = 0.0
    for x in range(s + 1):
        for y in range(r + 1):
            for z in range(r + 1):
                w = 11 - x - y - z
                if w < 0 or w > s:
                    continue
                c = comb(s, x) * comb(r, y) * comb(r, z) * comb(s, w)
                a, b = x + y, x + z
                pa = {**VP, 11: top_value, 0: top_value}
                pay = pa.get(a, 0) + pa.get(b, 0)
                payl = sum(VP[h] for h in (a, b) if h in VP and h not in (0, 11))
                anyc += c * (a in VP or b in VP)
                topc += c * (a in (0, 11) or b in (0, 11))
                ge20 += c * (max(VP.get(a, 0), VP.get(b, 0)) >= 20)
                ge200 += c * (max(VP.get(a, 0), VP.get(b, 0)) >= 200)
                ge4 += c * (VP.get(a, 0) + VP.get(b, 0) >= 4)
                m1 += c * pay; m2 += c * pay * pay; m1l += c * payl; m2l += c * payl * payl
    out = {'s': s, 'p_any': anyc / NV, 'p_any_frac': str(F(anyc, NV)), 'p_top_either': topc / NV,
           'one_in_top': round(NV / topc), 'p_ge20': ge20 / NV, 'p_ge200': ge200 / NV, 'p_pay_ge4': ge4 / NV,
           'mean_pay_all': m1 / NV, 'sd_pay_all': math.sqrt(m2 / NV - (m1 / NV) ** 2),
           'mean_pay_low': m1l / NV, 'sd_pay_low': math.sqrt(m2l / NV - (m1l / NV) ** 2)}
    return out


def pv_factor(i, n_years=10, per_year=12, due=False):
    """PV of equal instalments / nominal total, annual effective rate i."""
    n = n_years * per_year
    v = (1 + i) ** (-1 / per_year)
    ks = range(0, n) if due else range(1, n + 1)
    return sum(v ** k for k in ks) / n


def pois_pmf(k, lam):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def pois_upper(k, lam):   # P(X >= k)
    return 1 - sum(pois_pmf(j, lam) for j in range(k))


def pois_lower(k, lam):   # P(X <= k)
    return sum(pois_pmf(j, lam) for j in range(k + 1))


def poisbin_upper(k, qs):  # P(sum Bernoulli(q) >= k), exact DP
    d = np.zeros(len(qs) + 1); d[0] = 1
    for q in qs:
        d[1:] = d[1:] * (1 - q) + d[:-1] * q; d[0] *= (1 - q)
    return float(d[k:].sum())


def boot_se(x, reps=20000):
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), size=(reps, len(x)))
    return float(x[idx].mean(axis=1).std(ddof=1))


# ============================================================================ 1a EV pairs
OUT['ev_single_field'] = {'p_tier': {t: float(p) for t, p in P1.items()},
                          'p_tier_one_in': {t: round(1 / float(p), 1) for t, p in P1.items()},
                          'p_any': float(p_any_1), 'p_any_frac': str(p_any_1),
                          'p_6main_one_in': NEV, 'p_6p1_one_in': TOT}

# ============================================================================ 2a EV realized returns
PREM_DECLARED = {'2026-05', '2026-10'}
rows = []
for d in ev:
    t = d['tiers']; dep = d['deposits']
    low = sum(t[k][0] * t[k][1] for k in LOW if k in t)
    top = sum(t[k][0] * t[k][1] for k in ('6+1', '6+0'))
    old = '3+1' not in t           # before 07.10.2024: old rules (extra drum 1..4, no 3+1 tier)
    y = d['date'][:4]
    era = 'old_2024_to_Sep' if old else ('2024_Oct_Dec' if y == '2024' else y)
    rows.append(dict(date=d['date'], month=d['date'][:7], dow='Mon' if d['day'].startswith('Pon') else 'Thu',
                     era=era, old=old, dep=dep, bets=d['bets'], low=low / dep, top=top / dep, t=t, pb=d['pb']))
detected = sorted({r['month'] for r in rows if r['low'] > 0.45})
assert set(detected) == PREM_DECLARED, detected
for r in rows:
    r['prem'] = r['month'] in PREM_DECLARED


def grp(sel):
    s = [r for r in rows if sel(r)]
    if not s:
        return None
    low = [r['low'] for r in s]
    return {'draws': len(s), 'from': s[0]['date'], 'to': s[-1]['date'], 'mean_bets': round(st.mean(r['bets'] for r in s)),
            'low_share_mean': st.mean(low), 'low_share_pooled': sum(r['low'] * r['dep'] for r in s) / sum(r['dep'] for r in s),
            'low_share_sd_draw': st.stdev(low) if len(s) > 1 else 0.0, 'low_share_boot_se': boot_se(low) if len(s) > 1 else None,
            'top_share_realized_nominal': sum(r['top'] * r['dep'] for r in s) / sum(r['dep'] for r in s)}


groups = {}
for era in ('old_2024_to_Sep', '2024_Oct_Dec', '2025', '2026'):
    groups[era] = grp(lambda r, e=era: r['era'] == e and not r['prem'])
groups['2026_normal_Mon'] = grp(lambda r: r['era'] == '2026' and not r['prem'] and r['dow'] == 'Mon')
groups['2026_normal_Thu'] = grp(lambda r: r['era'] == '2026' and not r['prem'] and r['dow'] == 'Thu')
groups['2026_premium_May_Oct'] = grp(lambda r: r['prem'])
groups['2026_premium_Mon'] = grp(lambda r: r['prem'] and r['dow'] == 'Mon')
groups['2026_premium_Thu'] = grp(lambda r: r['prem'] and r['dow'] == 'Thu')
groups['post_Oct2024_all_normal'] = grp(lambda r: not r['old'] and not r['prem'])
groups['post_Oct2024_incl_premium'] = grp(lambda r: not r['old'])
OUT['ev_realized_groups'] = groups
OUT['ev_rule_low_share'] = {'normal': 0.579 * 0.542, 'premium_if_doubled': 2 * 0.579 * 0.542,
                            'note': 'tiers 3..8 = 54.2 % of a 57.9 % prize fund; realized is lower by rounding down to 0.10 EUR'}

# -- tier counts: is deposits/1.5 the right column count?  (post Oct 2024 rules: extra 1..7)
post = [r for r in rows if not r['old']]
oldr = [r for r in rows if r['old']]


def tier_check(rs, m):
    B = sum(r['bets'] for r in rs); res = {}
    for t in TIERS:
        if t not in rs[-1]['t']:
            continue
        obs = sum(r['t'][t][1] for r in rs)
        exp = B * float(ptier(t, m))
        lam_d = [r['bets'] * float(ptier(t, m)) for r in rs]
        disp = sum((r['t'][t][1] - l) ** 2 / l for r, l in zip(rs, lam_d)) / len(rs)
        res[t] = {'obs': obs, 'exp': round(exp, 1), 'ratio': round(obs / exp, 4), 'dispersion_index': round(disp, 2)}
        if t in ('6+1', '6+0'):
            res[t]['poisson_p_ge_obs'] = pois_upper(obs, exp)
            dw = sum(1 for r in rs if r['t'][t][1] > 0)
            qs = [1 - math.exp(-l) for l in lam_d]
            res[t]['draws_with_winner'] = dw
            res[t]['draws_with_winner_exp'] = round(sum(qs), 1)
            res[t]['p_draws_ge_obs'] = poisbin_upper(dw, qs)
    lowtiers = [t for t in LOW if t in rs[-1]['t']]
    est = [sum(r['t'][t][1] for t in lowtiers) / sum(float(ptier(t, m)) for t in lowtiers) for r in rs]
    res['bets_from_low_tier_counts_over_deposits_div_1_5'] = round(sum(est) / B, 4)
    return res


OUT['ev_tier_count_check'] = {
    'post_Oct2024_extra_1_7': tier_check(post, 7),
    'old_2024_extra_1_4': tier_check(oldr, 4),
    'old_2024_if_wrongly_1_7': {t: v for t, v in tier_check(oldr, 7).items() if t in ('4+1', '4+0', '6+1', '6+0')},
    'old_pb_values_seen': sorted({r['pb'] for r in oldr}),
    'history_naive_1_7_all_eras': {t: {'obs': sum(r['t'][t][1] for r in rows),
                                       'exp': round(sum(r['bets'] for r in rows) * float(P1[t]), 1),
                                       'poisson_p_ge_obs': pois_upper(sum(r['t'][t][1] for r in rows),
                                                                      sum(r['bets'] for r in rows) * float(P1[t]))}
                                   for t in ('6+1', '6+0')},
    'history_correct_rules': {t: {'obs': sum(r['t'][t][1] for r in rows),
                                  'exp': round(sum(r['bets'] for r in post) * float(ptier(t, 7))
                                               + sum(r['bets'] for r in oldr) * float(ptier(t, 4)), 1)}
                              for t in ('6+1', '6+0')},
    'multi_winner_draws': [{'date': r['date'], '6+1': r['t']['6+1'], '6+0': r['t']['6+0']} for r in rows
                           if r['t']['6+1'][1] > 1 or r['t']['6+0'][1] > 1],
}
for t in ('6+1', '6+0'):
    h = OUT['ev_tier_count_check']['history_correct_rules'][t]
    h['poisson_p_ge_obs'] = pois_upper(h['obs'], h['exp'])

# -- top tiers, current rules, expected value per field with Poisson co-winners
mon = [r for r in rows if r['dow'] == 'Mon'][-8:]
thu = [r for r in rows if r['dow'] == 'Thu'][-8:]
BETS_MON = st.mean(r['bets'] for r in mon)
BETS_THU = st.mean(r['bets'] for r in thu)


def f61(n):                      # EUR per 6+1 winner when n winners (current plan)
    return 480000.0 if n == 1 else (240000.0 if n == 2 else 720000.0 / n)


PV = {'0%': 1.0}
for i in (0.03, 0.05):
    PV[f'{int(i*100)}%'] = pv_factor(i)
PV_TABLE = {f'{int(i*100)}%': {'monthly_immediate': pv_factor(i), 'monthly_due': pv_factor(i, due=True),
                               'yearly_immediate': pv_factor(i, per_year=1), 'yearly_due': pv_factor(i, per_year=1, due=True)}
            for i in (0.0, 0.03, 0.05)}


def top_ev(bets, pv):
    lam1 = bets * float(P1['6+1']); lam0 = bets * float(P1['6+0'])
    e1 = 0.0
    for k in range(40):
        n = k + 1
        e1 += pois_pmf(k, lam1) * f61(n) * (1.0 if n >= 7 else pv)
    e0 = 30000.0 * (1 - math.exp(-lam0)) / lam0
    ev61 = float(P1['6+1']) * e1; ev60 = float(P1['6+0']) * e0
    return {'bets': round(bets), 'lambda_6p1': lam1, 'lambda_6p0': lam0,
            'mean_6p1_prize_if_won_pv': e1, 'share_factor_6p1': e1 / (480000 * pv),
            'mean_6p0_prize_if_won': e0, 'share_factor_6p0': e0 / 30000,
            'ev_per_field_6p1': ev61, 'ev_per_field_6p0': ev60,
            'per_1eur_6p1': ev61 / 1.5, 'per_1eur_6p0': ev60 / 1.5, 'per_1eur_top': (ev61 + ev60) / 1.5}


OUT['ev_top_tiers'] = {
    'rule': '6+1: 480000 (1 winner), 240000 each (2), 720000/n (>=3); 120 monthly instalments of prize/120 over 10 years, '
            'lump sum if >=7 winners. 6+0: 30000/n lump sum. Old rules (to Sep 2024): 6+1 480000 for 1-2 winners, 320000 x3.',
    'bets_target_monday_mean_last8_mondays': round(BETS_MON), 'bets_mean_last8_thursdays': round(BETS_THU),
    'pv_factors': PV_TABLE,
    'by_pv_rate': {k: top_ev(BETS_MON, v) for k, v in PV.items()},
    'sensitivity_bets_3pct': {str(b): top_ev(b, PV['3%'])['per_1eur_top'] for b in (60000, 80000, 100000, 120000, 200000)},
    'monthly_instalment_1_winner': 4000.0,
    'tax': 'Winnings from lotteries operated under the Slovak gambling act are fully exempt from income tax '
           '(par. 9 ods. 2 pism. l) zakona 595/2003 Z.z., Financna sprava FAQ).',
}

# realized prize per tier (effective, consistent with pooled share) for payout distributions
def eff_prizes(sel):
    s = [r for r in rows if sel(r)]
    D = sum(r['dep'] for r in s); pr = {}
    for t in LOW:
        share = sum(r['t'][t][0] * r['t'][t][1] for r in s) / D
        pr[t] = share * 1.5 / float(P1[t])
    return pr


PR_N = eff_prizes(lambda r: r['era'] == '2026' and not r['prem'])
PR_P = eff_prizes(lambda r: r['prem'])
T3 = top_ev(BETS_MON, PV['3%'])
for pr in (PR_N, PR_P):
    pr['6+1'] = T3['mean_6p1_prize_if_won_pv']; pr['6+0'] = T3['mean_6p0_prize_if_won']
OUT['ev_effective_prize_per_tier'] = {'normal_2026': PR_N, 'premium_2026': PR_P,
                                      'note': 'low tiers: realized pooled share*1.5/p_tier; 6+1 at 3% PV with sharing'}

pairs = []
for c in range(7):
    for same in (False, True):
        j = ev_pair(c, same)
        sN = summarize_pair(j, PR_N); sP = summarize_pair(j, PR_P)
        row = {'common': c, 'extra': 'same' if same else 'different', **{k: v for k, v in sN.items()}}
        row['premium_mean_pay_low'] = sP['mean_pay_low']; row['premium_sd_pay_low'] = sP['sd_pay_low']
        row['premium_p_pay_ge_4eur'] = sP['p_pay_ge_4eur']
        pairs.append(row)
OUT['ev_two_fields'] = pairs

# ============================================================================ 1b VAN pairs
OUT['van_single'] = {'p_any': sum(comb(11, h) * comb(11, 11 - h) for h in VP) / NV,
                     'p_top_one_in': NV / 2,
                     'ev_rule_per_1eur': sum(comb(11, h) * comb(11, 11 - h) * VP[h] for h in VP) / NV / 1.5}

# ============================================================================ 2b VAN realized
vrows = []
for d in van:
    t = d['tiers']; dep = d['deposits']
    low = sum(t[k][0] * t[k][1] for k in ('10', '9', '8', '3', '2', '1'))
    top = t['11'][0] * t['11'][1] + t['0'][0] * t['0'][1]
    prem = 0.0
    if d['premium']:
        prem = sum(float(p['Win'].split()[0].replace(',', '.')) for p in d['premium'])
    vrows.append(dict(date=d['date'], dow=d['day'][:3], dep=dep, bets=d['bets'], low=low, top=top, prem=prem,
                      topn=t['11'][1] + t['0'][1]))


def vgrp(s):
    D = sum(r['dep'] for r in s)
    per = [(r['low'] + r['top']) / r['dep'] for r in s]
    B = sum(r['bets'] for r in s)
    return {'draws': len(s), 'from': s[0]['date'], 'to': s[-1]['date'], 'mean_bets': round(B / len(s)),
            'low_share': sum(r['low'] for r in s) / D, 'top_share': sum(r['top'] for r in s) / D,
            'total_share': sum(r['low'] + r['top'] for r in s) / D,
            'total_share_incl_premium_codes': sum(r['low'] + r['top'] + r['prem'] for r in s) / D,
            'total_share_boot_se': boot_se(per), 'low_share_sd_draw': st.stdev([r['low'] / r['dep'] for r in s]),
            'top_winners': sum(r['topn'] for r in s), 'top_winners_exp': round(B * 2 / NV, 1),
            'top_poisson_p_le_obs': pois_lower(sum(r['topn'] for r in s), B * 2 / NV)}


vmon = [r for r in vrows if r['dow'] == 'Pon'][-8:]
VBETS_MON = st.mean(r['bets'] for r in vmon)
lamv = VBETS_MON * 2 / NV
vshare = (1 - math.exp(-lamv)) / lamv
v_low_rule = sum(comb(11, h) * comb(11, 11 - h) * VP[h] for h in VP if h not in (0, 11)) / NV / 1.5
v_top_rule = 2 * 100000 / NV / 1.5
OUT['van_returns'] = {
    'all_410': vgrp(vrows), 'last_3_months': vgrp([r for r in vrows if r['date'] >= '2026-08-23']),
    'rule': {'low_per_1eur': v_low_rule, 'top_per_1eur_no_sharing': v_top_rule, 'total_no_sharing': v_low_rule + v_top_rule,
             'bets_target_monday_mean_last8': round(VBETS_MON), 'lambda_other_top_winners': lamv,
             'top_share_factor': vshare, 'total_with_sharing': v_low_rule + v_top_rule * vshare},
    'premium_13_11_2026': {'codes_eur': [r['prem'] for r in vrows if r['prem']][0] if any(r['prem'] for r in vrows) else 0,
                           'per_1eur_that_day': [r['prem'] / r['dep'] for r in vrows if r['prem']]},
}
VAN_RET = v_low_rule + v_top_rule * vshare
vp = [van_pair(s, top_value=100000 * vshare) for s in range(12)]
OUT['van_two_tickets'] = vp

# ============================================================================ 3 purchase scenarios
evN_low = groups['2026']['low_share_mean']; evP_low = groups['2026_premium_May_Oct']['low_share_mean']
evN_se = groups['2026']['low_share_boot_se']; evP_se = groups['2026_premium_May_Oct']['low_share_boot_se']
top = {k: v['per_1eur_top'] for k, v in OUT['ev_top_tiers']['by_pv_rate'].items()}
d0 = [p for p in pairs if p['common'] == 0 and p['extra'] == 'different'][0]
v5 = vp[5]
p_ev1 = float(p_any_1); p_van1 = OUT['van_single']['p_any']
sc = {}
for name, low, se, sdl in (('2xEV_disjoint_normal', evN_low, evN_se, d0['sd_pay_low']),
                           ('2xEV_disjoint_premium', evP_low, evP_se, d0['premium_sd_pay_low'])):
    sc[name] = {'stake': 3.0, 'p_any': d0['p_any'], 'p_6p1_one_in': d0['one_in_6p1_either'],
                'return_low_per_1eur': low, 'return_low_boot_se': se,
                **{f'return_per_1eur_pv{k}': low + v for k, v in top.items()},
                'expected_back_eur_pv3%': 3.0 * (low + top['3%']),
                'player_sd_eur_low_tiers_only': sdl,
                'p_payout_ge_4eur_profit': d0['p_pay_ge_4eur'] if 'normal' in name else d0['premium_p_pay_ge_4eur']}
sc['2xVAN_s5'] = {'stake': 3.0, 'p_any': v5['p_any'], 'p_top_one_in': v5['one_in_top'],
                  'return_per_1eur_rule_with_sharing': VAN_RET,
                  'return_per_1eur_realized_410': OUT['van_returns']['all_410']['total_share'],
                  'return_realized_boot_se': OUT['van_returns']['all_410']['total_share_boot_se'],
                  'expected_back_eur': 3.0 * VAN_RET, 'player_sd_eur_low_tiers_only': v5['sd_pay_low'],
                  'p_payout_ge_4eur_profit': v5['p_pay_ge4']}
for lab, low in (('normal', evN_low), ('premium', evP_low)):
    r = (low + top['3%'] + VAN_RET) / 2
    sc[f'1EV_1VAN_{lab}'] = {'stake': 3.0, 'p_any': 1 - (1 - p_ev1) * (1 - p_van1),
                             'return_per_1eur_pv3%': r, 'return_per_1eur_pv0%': (low + top['0%'] + VAN_RET) / 2,
                             'expected_back_eur_pv3%': 3.0 * r}
OUT['scenarios'] = sc
json.dump(OUT, open(os.path.join(RUN, 'returns.json'), 'w'), indent=1, ensure_ascii=False, default=float)

# ============================================================================ markdown
def pc(x, d=2):
    return f'{100*x:.{d}f} %'


g = groups; T = OUT['ev_top_tiers']['by_pv_rate']; tc = OUT['ev_tier_count_check']
L = []
L.append('# Returns and exact odds — target Monday 23.11.2026 (subagent 3)\n')
L.append('Script: `lab/run_2311/scripts/returns.py` (python3 -I). All numbers: `returns.json`. '
         'No prediction: only prize arithmetic. Stake 2 × 1,50 € = 3 €.\n')
L.append('## Sanity table (per draw, 3 € stake)\n')
L.append('| Purchase | P(any prize) | Return per 1 € (6+1 PV 3 %) | 0 % / 5 % PV | low tiers only | € back on average |')
L.append('|---|---|---|---|---|---|')
for k, lab in (('2xEV_disjoint_normal', '2× EV, disjoint, normal month'), ('2xEV_disjoint_premium', '2× EV, disjoint, premium month')):
    s = sc[k]
    L.append(f"| {lab} | {pc(s['p_any'])} | **{s['return_per_1eur_pv3%']:.3f}** | {s['return_per_1eur_pv0%']:.3f} / {s['return_per_1eur_pv5%']:.3f} "
             f"| {s['return_low_per_1eur']:.3f} ± {s['return_low_boot_se']:.4f} | {s['expected_back_eur_pv3%']:.2f} € |")
s = sc['2xVAN_s5']
L.append(f"| 2× VAN, 5 common | {pc(s['p_any'])} | **{s['return_per_1eur_rule_with_sharing']:.3f}** (rule, sharing) | realized {s['return_per_1eur_realized_410']:.3f} ± {s['return_realized_boot_se']:.3f} "
         f"| {v_low_rule:.3f} | {s['expected_back_eur']:.2f} € |")
for lab in ('normal', 'premium'):
    s = sc[f'1EV_1VAN_{lab}']
    L.append(f"| 1 EV + 1 VAN ({lab} EV month) | {pc(s['p_any'])} | **{s['return_per_1eur_pv3%']:.3f}** | {s['return_per_1eur_pv0%']:.3f} (0 %) | — | {s['expected_back_eur_pv3%']:.2f} € |")
L.append('')
L.append(f"Player outcome spread (low tiers only, one draw): 2× EV SD ≈ {sc['2xEV_disjoint_normal']['player_sd_eur_low_tiers_only']:.1f} € (premium {sc['2xEV_disjoint_premium']['player_sd_eur_low_tiers_only']:.1f} €), "
         f"2× VAN SD ≈ {sc['2xVAN_s5']['player_sd_eur_low_tiers_only']:.1f} €. The mean is a long-run figure; a single draw is almost always 0 € or one small prize.\n")
n30 = [r['t']['3+0'][0] for r in rows if r['era'] == '2026' and not r['prem']]
OUT['ev_3p0_prize_2026_normal'] = {'mean': st.mean(n30), 'min': min(n30), 'max': max(n30), 'share_ge_3': sum(x >= 3 for x in n30) / len(n30)}
json.dump(OUT, open(os.path.join(RUN, 'returns.json'), 'w'), indent=1, ensure_ascii=False, default=float)
L.append(f"P(payout ≥ 4 €, i.e. more than the 3 € stake): 2× EV normal {pc(sc['2xEV_disjoint_normal']['p_payout_ge_4eur_profit'])}, "
         f"premium {pc(sc['2xEV_disjoint_premium']['p_payout_ge_4eur_profit'])}; 2× VAN {pc(sc['2xVAN_s5']['p_payout_ge_4eur_profit'])}. "
         f"EV 3+0 alone pays about the stake back in normal months (2026: mean {st.mean(n30):.2f} €, range {min(n30):.1f}–{max(n30):.1f} €); "
         f"VAN 8/3 hits pay exactly 3 €.\n")
L.append('## 1. Exact odds\n')
L.append(f"EV one field: P(any) = {pc(float(p_any_1),3)}; 6 main 1 : {NEV:,}; 6+1 1 : {TOT:,}; 5 main 1 : {1/float(pmain(5)):,.0f}.\n")
L.append('EV two fields, c common main numbers (extra numbers different / same):\n')
L.append('| c | P(any) | P(≥5+0 either) | P(6 main either) | 6+1 either 1 : (extras diff / same) | P(a "+1" tier) diff / same | SD low € diff / same |')
L.append('|---|---|---|---|---|---|---|')
for c in range(7):
    a = [p for p in pairs if p['common'] == c and p['extra'] == 'different'][0]
    b = [p for p in pairs if p['common'] == c and p['extra'] == 'same'][0]
    L.append(f"| {c} | {pc(a['p_any'],3)} | {pc(a['p_ge_5p0_either'],4)} | 1 : {1/a['p_6main_either']:,.0f} | {a['one_in_6p1_either']:,} / {b['one_in_6p1_either']:,} "
             f"| {pc(a['p_any_plus1_tier'],3)} / {pc(b['p_any_plus1_tier'],3)} | {a['sd_pay_low']:.2f} / {b['sd_pay_low']:.2f} |")
L.append('')
L.append(f"- P(any) does not depend on the extra numbers (3+0 already pays); disjoint fields maximise it: {d0['p_any_frac']} = {pc(d0['p_any'],3)}. "
         "Different extra numbers only change the mix (more often a '+1' tier, lower SD); same main numbers with different extras keep the same 6+1 odds but halve the 6-main odds.\n")
L.append('VAN two tickets, s common numbers:\n')
L.append('| s | P(any) | P(≥20 €) | P(≥200 €) | top (11 or 0) 1 : |')
L.append('|---|---|---|---|---|')
for v in vp:
    L.append(f"| {v['s']} | {pc(v['p_any'],3)} | {pc(v['p_ge20'],3)} | {pc(v['p_ge200'],4)} | {v['one_in_top']:,} |")
L.append(f"\nConfirmed: s = 5 and 6 give the maximum {pc(vp[5]['p_any'],3)} ({vp[5]['p_any_frac']}). Mixed 1 EV + 1 VAN: P(any) = {pc(sc['1EV_1VAN_normal']['p_any'],3)} (independent games).\n")
L.append('## 2. EV realized return of tiers 3+0…5+1 (share of stakes)\n')
L.append('| Group | draws | bets/draw | mean | SD draw-to-draw | bootstrap SE | realized 6+1/6+0 (nominal) |')
L.append('|---|---|---|---|---|---|---|')
for k, lab in (('old_2024_to_Sep', '2024 to Sep (old rules: extra 1–4, no 3+1)'), ('2024_Oct_Dec', '2024 Oct–Dec'), ('2025', '2025'),
               ('2026', '2026 normal months'), ('2026_normal_Mon', '2026 normal, Mon'), ('2026_normal_Thu', '2026 normal, Thu'),
               ('2026_premium_May_Oct', '2026 premium (May, Oct)'), ('2026_premium_Mon', 'premium, Mon'), ('2026_premium_Thu', 'premium, Thu')):
    x = g[k]
    L.append(f"| {lab} | {x['draws']} | {x['mean_bets']:,} | {x['low_share_mean']:.4f} | {x['low_share_sd_draw']:.4f} | {x['low_share_boot_se']:.4f} | {x['top_share_realized_nominal']:.3f} |")
L.append(f"\nBy rule: 0,579 × 0,542 = {0.579*0.542:.4f} (normal), ×2 = {2*0.579*0.542:.4f} (premium). Low-tier share is almost deterministic (SD ≈ 0,002): "
         "the pool is parimutuel, so only top tiers and personal luck vary. Only May and Oct 2026 show doubled tiers (auto-detected, matches the decisions).\n")
L.append('Top tiers (current plan, Monday bets ≈ {:,} = mean of last 8 Mondays):\n'.format(round(BETS_MON)))
L.append('| 6+1 PV rate | PV factor (120 monthly) | 6+1 per 1 € | 6+0 per 1 € | top per 1 € |')
L.append('|---|---|---|---|---|')
for k in ('0%', '3%', '5%'):
    L.append(f"| {k} | {PV_TABLE[k]['monthly_immediate']:.4f} | {T[k]['per_1eur_6p1']:.4f} | {T[k]['per_1eur_6p0']:.4f} | {T[k]['per_1eur_top']:.4f} |")
L.append(f"\nSharing factors at {round(BETS_MON):,} bets: 6+1 ×{T['0%']['share_factor_6p1']:.3f} (λ = {T['0%']['lambda_6p1']:.3f}), 6+0 ×{T['0%']['share_factor_6p0']:.3f} (λ = {T['0%']['lambda_6p0']:.3f}). "
         f"Yearly instead of monthly instalments: PV 3 % {PV_TABLE['3%']['yearly_immediate']:.3f}, 5 % {PV_TABLE['5%']['yearly_immediate']:.3f}. "
         f"Top-tier return vs bets (3 %): " + ', '.join(f"{int(b)//1000}k → {v:.3f}" for b, v in OUT['ev_top_tiers']['sensitivity_bets_3pct'].items()) + '.\n')
vr = OUT['van_returns']; ru = vr['rule']
L.append('## 2b. VAN return per 1 €\n')
L.append(f"- By rule: low tiers {ru['low_per_1eur']:.4f} + top {ru['top_per_1eur_no_sharing']:.4f} = {ru['total_no_sharing']:.4f}; with sharing "
         f"(Monday ≈ {ru['bets_target_monday_mean_last8']:,} bets, λ = {ru['lambda_other_top_winners']:.3f}, factor {ru['top_share_factor']:.3f}) = **{ru['total_with_sharing']:.4f}**.")
for k, lab in (('all_410', 'All 410 draws'), ('last_3_months', 'Last 3 months')):
    x = vr[k]
    L.append(f"- {lab} ({x['from']}…{x['to']}, {x['mean_bets']:,} bets/draw): realized {x['total_share']:.4f} ± {x['total_share_boot_se']:.3f} "
             f"(low {x['low_share']:.4f}, top {x['top_share']:.4f}; top winners {x['top_winners']} vs {x['top_winners_exp']} expected, p = {x['top_poisson_p_le_obs']:.2f}); "
             f"with the 13.11 premium codes {x['total_share_incl_premium_codes']:.4f}.")
L.append('')
L.append('## 3. Checks on the tier counts\n')
pc7 = tc['post_Oct2024_extra_1_7']
L.append(f"- Since 07.10.2024 deposits/1,5 is the right column count: low-tier winners / expected = "
         + ', '.join(f"{t} {pc7[t]['ratio']:.3f}" for t in LOW) + f"; bets from tier counts / (deposits/1,5) = {pc7['bets_from_low_tier_counts_over_deposits_div_1_5']}.")
oc = tc['old_2024_extra_1_4']; ow = tc['old_2024_if_wrongly_1_7']
L.append(f"- Before Oct 2024 the extra drum had 1–4 (drawn extra numbers only 1–4; with 1/7 the '+1' tiers look ×{ow['4+1']['ratio']:.2f}, with 1/4 they fit: 4+1 {oc['4+1']['ratio']:.3f}, 4+0 {oc['4+0']['ratio']:.3f}). "
         "So the naive 1/7 expectation for 2024 is wrong.")
hn = tc['history_naive_1_7_all_eras']; hc = tc['history_correct_rules']
L.append(f"- 6+1: {hc['6+1']['obs']} winners vs {hn['6+1']['exp']} (naive 1/7, p = {hn['6+1']['poisson_p_ge_obs']:.3f}) but {hc['6+1']['exp']} with correct 2024 rules (p = {hc['6+1']['poisson_p_ge_obs']:.2f}); "
         f"since Oct 2024: {pc7['6+1']['obs']} vs {pc7['6+1']['exp']} (normal).")
L.append(f"- 6+0: {hc['6+0']['obs']} vs {hc['6+0']['exp']} (correct rules, Poisson p = {hc['6+0']['poisson_p_ge_obs']:.3f}); since Oct 2024 {pc7['6+0']['obs']} vs {pc7['6+0']['exp']} (p = {pc7['6+0']['poisson_p_ge_obs']:.3f}). "
         f"But winners come in clusters (2–3 per draw; low tiers have dispersion index {pc7['5+0']['dispersion_index']}–{pc7['4+0']['dispersion_index']} ≫ 1), so plain Poisson overstates significance. "
         f"Draws with ≥1 6+0 winner since Oct 2024: {pc7['6+0']['draws_with_winner']} vs {pc7['6+0']['draws_with_winner_exp']} expected (p = {pc7['6+0']['p_draws_ge_obs']:.2f}) → chance, nothing to exploit.")
L.append("- Old 2024 payouts: 6+1 480 000 € for 1–2 winners, 320 000 € ×3 (cap 960 000 €); 6+0 24 000 € (48 000 € cap in spring, 12 000 € each in Sep 2024). "
         "Current plan (from 18.03.2026): 2 winners get 240 000 € each, ≥3 share 720 000 €; 6+0 shares 30 000 €.\n")
L.append('## Assumptions\n')
L.append('- 6+1 is paid in 120 monthly instalments (480 000 € → 4 000 €/month); no lump-sum option unless ≥7 winners. PV uses annuity-immediate; 3 % is the headline rate.')
L.append('- Co-winners ~ Poisson with uniform number choice (bets = mean of last 8 Mondays). Unpopular numbers would only raise the top-tier value a bit; not modelled here.')
L.append('- Low tiers use the realized 2026 share (normal or premium months); the same number holds for Monday and Thursday.')
L.append('- VAN: fixed prizes, 100 000 € shared by all 11-or-0 winners; premium codes (13.11.2026, 10 × 1 000 €) are a one-off and excluded from the headline.')
L.append('- Tax: lottery winnings from games operated under the Slovak gambling act are fully tax-exempt (§ 9 ods. 2 písm. l) zákona 595/2003; Finančná správa FAQ).')
L.append('- November/December 2026: no assumption on premium here — both columns are given.')
open(os.path.join(RUN, 'returns.md'), 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
