"""Red team, attack (e): exact odds by brute-force enumeration of all 296010 x 7 outcomes for the final tickets,
and an independent recomputation of the 0.491 / 0.511 return.  python3 -I redteam_e_odds.py -> ../redteam_e.json"""
import json, os, sys
from fractions import Fraction as F
from math import exp, factorial
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from redteam_common import *

fa, xa, fb, xb = FINAL
Sa = np.zeros(27, bool); Sa[np.array(fa) - 1] = True
Sb = np.zeros(27, bool); Sb[np.array(fb) - 1] = True
ha = DB[:, Sa].sum(1); hb = DB[:, Sb].sum(1)
NC7 = NC * 7
cnt = {}
# outcomes: (D, pb); field A wins tier (k, pb==xa) etc.
anyc = int(np.sum((ha >= 3) | (hb >= 3))) * 7
six_main = int(np.sum((ha == 6) | (hb == 6))) * 7
six1 = int(np.sum(ha == 6)) + int(np.sum(hb == 6))           # pb must equal that field's extra: 1 of 7
both = int(np.sum((ha >= 3) & (hb >= 3))) * 7
tiers = {}
for k in (3, 4, 5, 6):
    for e in (1, 0):
        na = int(np.sum(ha == k)) * (1 if e else 6); nb = int(np.sum(hb == k)) * (1 if e else 6)
        tiers[f'{k}+{e}'] = (na + nb) / 2 / NC7            # per field
out = {'P_any_prize_2_fields': str(F(anyc, NC7)), 'P_any_float': anyc / NC7,
       'P_6main_either': str(F(six_main, NC7)), 'P_6plus1_either': str(F(six1, NC7)),
       'P_both_fields_win': both / NC7, 'tier_prob_per_field': tiers,
       'one_field_P_any': float(np.mean(ha >= 3))}
print(out)
# returns per 1 EUR (normal month), independent of returns.py
fp = pool_shares((DATES >= '2026-01-01') & ~PREM)
low = sum(fp.values())
mon = [t for t in range(N) if not THU[t]][-8:]
bets = float(np.mean(B[mon]))
lam1 = bets * PM[6] / 7; lam0 = bets * PM[6] * 6 / 7
def pois(k, l): return exp(-l) * l ** k / factorial(k)
def pv(i, n=120):
    v = (1 + i) ** (-1 / 12); return sum(v ** k for k in range(1, n + 1)) / n
res = {}
for lab, i in (('0%', 0.0), ('3%', 0.03), ('5%', 0.05)):
    f = pv(i)
    e1 = sum(pois(k, lam1) * (480000 if k == 0 else 240000 if k == 1 else 720000 / (k + 1)) * (1 if k + 1 >= 7 else f)
             for k in range(40))
    e0 = 30000 * (1 - exp(-lam0)) / lam0
    top = (PM[6] / 7 * e1 + PM[6] * 6 / 7 * e0) / 1.5
    res[lab] = {'pv_factor': f, 'top_per_EUR': top, 'total_per_EUR': low + top}
out['low_tiers_share_2026_normal'] = low
out['low_tiers_by_rules'] = 0.579 * (0.015 + 0.043 + 0.044 + 0.108 + 0.062 + 0.27)
out['monday_bets_last8'] = bets
out['returns'] = res
# the 3% rate: what discount rate makes total = 0.491?
print(json.dumps({k: out[k] for k in ('low_tiers_share_2026_normal', 'low_tiers_by_rules', 'monday_bets_last8', 'returns')}, indent=1))
json.dump(out, open(os.path.join(BASE, 'redteam_e.json'), 'w'), indent=1)
