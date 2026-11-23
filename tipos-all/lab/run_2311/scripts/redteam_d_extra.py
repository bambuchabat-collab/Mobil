"""Red team, attack (d): P4 'players take the extra number from their own 6 numbers'.
Identification: under independence of a ticket's extra and its main numbers, the share of m-hit winners holding the
drawn extra pb does NOT depend on whether pb is among the drawn main numbers D. If a fraction phi of tickets takes its
extra uniformly from its own 6 numbers, the +1 share of m-hit winners is higher when pb in D (ticket then contains pb
with prob m/6) than when pb not in D (prob (6-m)/21). So the effect is identifiable from public tier counts.
Test (independent of ideas_ev.py): post-era draws; u_m = log(n(m+1)/n(m+0)); remove drawn-extra fixed effects;
statistic = inverse-variance-weighted mean difference (pb in D) - (pb not in D) over m=3,4,(5);
null: re-assign the main sets D across draws (keeps pb, keeps u), 20000 permutations.
python3 -I redteam_d_extra.py -> ../redteam_d.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from redteam_common import *

rng = np.random.default_rng(1123)
post = np.where(POST)[0]
U = {m: np.log((W1[m][post] + 0.5) / (W0[m][post] + 0.5)) for m in (3, 4, 5)}
pbp = PB[post]
inD = np.array([PB[t] in set(MAIN[t]) for t in post])
MAINp = MAIN[post]
VAR = {m: float(np.mean(1 / (W1[m][post] + 0.5) + 1 / (W0[m][post] + 0.5))) for m in (3, 4, 5)}


def resid(u):
    r = u.copy()
    for x in range(1, 8):
        s = pbp == x; r[s] -= r[s].mean()
    return r


Rm = {m: resid(U[m]) for m in (3, 4, 5)}


def stat(ind, ms=(3, 4)):
    num = den = 0.0; per = {}
    for m in ms:
        d = Rm[m][ind].mean() - Rm[m][~ind].mean()
        sd2 = np.var(Rm[m]) * (1 / ind.sum() + 1 / (~ind).sum())
        per[m] = d; num += d / sd2; den += 1 / sd2
    return num / den, per


obs, per = stat(inD)
obs5, per5 = stat(inD, (3, 4, 5))
cnt = cnt5 = 0; R = 20000
for _ in range(R):
    perm = rng.permutation(len(post))
    ind = np.array([pbp[i] in set(MAINp[perm[i]]) for i in range(len(post))])
    s, _ = stat(ind); s5, _ = stat(ind, (3, 4, 5))
    cnt += s >= obs; cnt5 += s5 >= obs5
out = {'n_post_draws': int(len(post)), 'n_pb_in_D': int(inD.sum()), 'expected_share_pb_in_D': 6 / 27,
       'diff_log_plus1_share_pb_in_D_minus_not': {str(m): float(v) for m, v in per5.items()},
       'pct_effect': {str(m): float(100 * (np.exp(v) - 1)) for m, v in per5.items()},
       'p_perm_m34': (1 + cnt) / (1 + R), 'p_perm_m345': (1 + cnt5) / (1 + R)}
# implied fraction phi of tickets with extra drawn from own numbers (s ~ 1/7), from the 4-match effect
s0 = 1 / 7
for m in (3, 4):
    e = np.exp(per5[m])
    a_in, a_out = m / 6 / 6, (6 - m) / 21 / 6
    # (phi*a_in + (1-phi)s0) / (phi*a_out + (1-phi)s0) = e  -> solve for phi
    phi = (e - 1) * s0 / ((a_in - s0) - e * (a_out - s0))
    out[f'implied_phi_from_{m}match'] = float(phi)
# money for the final tickets: extra outside own field (as chosen) vs inside (hypothetical)
q = 6 / 27
fp = pool_shares((DATES >= '2026-01-01') & ~PREM)
def plus1(inside, delta, k):
    pin = k / 6 if inside else (6 - k) / 21
    norm = (1 - q) + q * np.exp(delta)
    return pin * np.exp(-delta) * norm + (1 - pin) * norm
d3, d4 = per5[3], per5[4]
ins = sum(fp[f'{k}+1'] * plus1(True, d3 if k == 3 else d4, k) for k in (3, 4, 5))
outs = sum(fp[f'{k}+1'] * plus1(False, d3 if k == 3 else d4, k) for k in (3, 4, 5))
out['money_pp_per_EUR_outside_minus_inside'] = float(100 * (outs - ins))
out['final_tickets'] = {'field1_extra_in_own_field': FINAL[1] in FINAL[0], 'field2_extra_in_own_field': FINAL[3] in FINAL[2],
                        'extras_in_other_field': [FINAL[1] in FINAL[2], FINAL[3] in FINAL[0]]}
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(BASE, 'redteam_d.json'), 'w'), indent=1)
