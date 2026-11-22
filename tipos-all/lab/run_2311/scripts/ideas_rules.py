"""Subagent 5: descriptive rules checks D1, D2, D4, D5 (+ post-hoc D7) for EV/VAN. Not part of the Holm family.
python3 -I ideas_rules.py -> ../ideas_rules_results.json
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from math import comb
from ideas_common import load_ev, EV_SHARE, EV_FUND, BASE

d = load_ev(); ev = d['ev']
out = {}
# D1 realised share per tier vs rules, smallest prize, by era
D1 = {}
for k in ['5+1', '5+0', '4+1', '4+0', '3+1', '3+0']:
    rows = [(e['tiers'][k][0] * e['tiers'][k][1] / e['deposits'], e['tiers'][k][0], e['tiers'][k][1], o, pr)
            for e, o, pr in zip(ev, d['old'], d['prem']) if k in e['tiers']]
    def summ(sel):
        s = [r[0] for r in sel if r[2] > 0]
        return dict(n=len(sel), draws_with_0_winners=sum(1 for r in sel if r[2] == 0),
                    share_mean=float(np.mean(s)) if s else None, share_sd=float(np.std(s)) if s else None,
                    min_prize=min((r[1] for r in sel if r[2] > 0), default=None),
                    max_prize=max((r[1] for r in sel if r[2] > 0), default=None))
    D1[k] = dict(rule_share_of_stakes=EV_SHARE[k] * EV_FUND,
                 new_normal=summ([r for r in rows if r[3] == 0 and r[4] == 0]),
                 new_premium=summ([r for r in rows if r[3] == 0 and r[4] == 1]),
                 old_era=summ([r for r in rows if r[3] == 1]))
out['D1_tier_shares'] = D1
out['D1_premium_draws'] = [dt for dt, pr in zip(d['dates'], d['prem']) if pr]
# D2 fixed-pool tiers with several winners
out['D2_top_tiers_multi'] = [dict(date=e['date'], tier=k, prize=e['tiers'][k][0], winners=e['tiers'][k][1])
                             for e in ev for k in ('6+1', '6+0') if e['tiers'][k][1] >= 1]
# D2 summary: observed vs uniform-play expected winners in the fixed-pool tiers (descriptive)
D2s = {}
for era in ('old', 'new'):
    sel = [e for e in ev if ('3+1' in e['tiers']) == (era == 'new')]
    q = 3 / 4 if era == 'old' else 6 / 7; NN = comb(27, 6)
    l0 = np.array([e['bets'] * q / NN for e in sel]); w0 = np.array([e['tiers']['6+0'][1] for e in sel])
    l1 = np.array([e['bets'] * (1 - q) / NN for e in sel]); w1 = np.array([e['tiers']['6+1'][1] for e in sel])
    D2s[era] = {'draws': len(sel), '6+0_obs': int(w0.sum()), '6+0_exp': float(l0.sum()),
                '6+0_draws_ge2_obs': int((w0 >= 2).sum()),
                '6+0_draws_ge2_exp_poisson': float((1 - np.exp(-l0) - l0 * np.exp(-l0)).sum()),
                '6+1_obs': int(w1.sum()), '6+1_exp': float(l1.sum())}
out['D2_summary'] = D2s
# D4 exact P(any prize) for 3 EUR on a Monday
N = comb(27, 6)
p1 = sum(comb(6, a) * comb(21, 6 - a) for a in range(3, 7)) / N
p2 = sum(comb(6, a) * comb(6, b) * comb(15, 6 - a - b) for a in range(7) for b in range(7)
         if a + b <= 6 and (a >= 3 or b >= 3)) / N
TOT = comb(22, 11)
pv1 = sum(comb(11, h) * comb(11, 11 - h) for h in (0, 1, 2, 3, 8, 9, 10, 11)) / TOT
out['D4_P_any_3EUR'] = {'EV 2 disjoint fields': p2, 'VAN 2 tickets 5-6 common': 0.167115,
                        'EV 1 field + VAN 1 ticket': 1 - (1 - p1) * (1 - pv1), 'EV 1 field': p1, 'VAN 1 ticket': pv1}
# D5 extra number: P(any) unaffected (3+0 pays); value of +1 tiers
out['D5_extra'] = dict(P_any_independent_of_extra=True,
                       plus1_tiers_share_of_stakes=(EV_SHARE['5+1'] + EV_SHARE['4+1'] + EV_SHARE['3+1']) * EV_FUND,
                       note='with C2 relative popularity 0.86 for extras 5,6,7 vs mean 1.0 -> about +16% on these tiers '
                            '= +1.1 pp of stake (already known, agent_extra C2)')
# D7 (post hoc, descriptive): Monday vs Thursday bets and sharing of the fixed 6+0 / 6+1 pools
mon = d['bets'][(d['thu'] == 0) & (d['old'] == 0)][-30:]; thu = d['bets'][d['thu'] == 1]
P60 = (1 / N) * 6 / 7; P61 = (1 / N) / 7
def fixed_ev(b):
    l0, l1 = b * P60, b * P61
    return (30000 * P60 * (1 - np.exp(-l0)) / l0 + 480000 * P61 * (1 - np.exp(-l1)) / l1) / 1.5
out['D7_posthoc_day_volume'] = dict(mean_bets_monday_last30=float(mon.mean()), mean_bets_thursday=float(thu.mean()),
                                    fixed_tiers_return_monday=float(fixed_ev(mon.mean())),
                                    fixed_tiers_return_thursday=float(fixed_ev(thu.mean())))
json.dump(out, open(os.path.join(BASE, 'ideas_rules_results.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
