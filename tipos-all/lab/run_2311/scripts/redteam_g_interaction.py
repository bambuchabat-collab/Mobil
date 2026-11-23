"""Red team, extra attack on P3 (not in the original list): are extra-number preferences weaker among the players who
share unpopular main numbers? (e.g. quick-pick tickets are uniform in BOTH main and extra numbers). If so, the
population-average extra popularity (5/6/7 ~0.9) overstates the extra-number bonus for a field of unpopular numbers.
Test: post-era draws, u_t = log(+1 share / (1 - +1 share)) of 3-5-match winners; deviation from the drawn-extra mean
regressed on z_t * c_pb, z_t = D-side popularity score of the drawn main numbers (red-team ridge, 3-match),
c_pb = centred log share of the drawn extra. delta > 0 means: in unpopular-number draws extras look more uniform.
Null: permute z across draws (20000).  python3 -I redteam_g_interaction.py -> ../redteam_g.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from redteam_common import *
from redteam_model import fit_tier, K_extra

rng = np.random.default_rng(99)
post = np.where(POST)[0]
f3 = fit_tier(np.arange(N), 3)
z = Z[post] @ f3['beta']; z = (z - z.mean()) / z.std()
n1 = sum(W1[m][post] for m in (3, 4, 5)); nt = sum(W[m][post] for m in (3, 4, 5))
s = n1 / nt; u = np.log(s / (1 - s))
pb = PB[post]
dev = u.copy(); cbar = np.zeros(8)
for x in range(1, 8):
    k = pb == x; cbar[x] = u[k].mean(); dev[k] -= u[k].mean()
c = cbar[pb] - cbar[1:].mean()


def delta(zz):
    X = zz * c
    return float((X @ dev) / (X @ X))


obs = delta(z)
null = np.array([delta(rng.permutation(z)) for _ in range(20000)])
p_two = float((1 + np.sum(np.abs(null) >= abs(obs))) / (1 + len(null)))
# descriptive: relative popularity of extras in unpopular-D vs popular-D draws (terciles of z)
q1, q2 = np.quantile(z, [1 / 3, 2 / 3])
def relpop(sel):
    sh = np.array([n1[sel & (pb == x)].sum() / nt[sel & (pb == x)].sum() for x in range(1, 8)])
    return [round(float(v), 3) for v in 7 * sh / sh.sum()]
out = {'delta': obs, 'null_sd': float(null.std()), 'p_two_sided': p_two,
       'interpretation': 'delta>0: extra preferences weaker in unpopular-number draws',
       'extra_rel_pop_unpopular_D_tercile': relpop(z <= q1), 'extra_rel_pop_popular_D_tercile': relpop(z >= q2),
       'extra_rel_pop_all_post': relpop(np.ones(len(post), bool))}
# what the extra bonus would be for a field of unpopular numbers if the unpopular-tercile extra shares applied
fp = pool_shares((DATES >= '2026-01-01') & ~PREM)
for lab, sel in (('all_post', np.ones(len(post), bool)), ('unpopular_D_tercile', z <= q1)):
    sh = np.array([n1[sel & (pb == x)].sum() / nt[sel & (pb == x)].sum() for x in range(1, 8)])
    K = K_extra(sh, fp); Kb = K.mean(1)
    out[f'extra_bonus_6_7_pct_{lab}'] = float(100 * ((K[:, 5] + K[:, 6]).sum() / 2 / Kb.sum() - 1))
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(BASE, 'redteam_g.json'), 'w'), indent=1)

# robustness: drop draws where the drawn extra is also a drawn main number (P4 coupling could mimic the interaction)
keep = np.array([PB[t] not in set(MAIN[t]) for t in post])
def delta_sub(zz, k):
    X = (zz * c)[k]; return float((X @ dev[k]) / (X @ X))
obs_k = delta_sub(z, keep)
null_k = np.array([delta_sub(rng.permutation(z), keep) for _ in range(20000)])
out['robust_drop_pb_in_D'] = {'n': int(keep.sum()), 'delta': obs_k,
                              'p_two_sided': float((1 + np.sum(np.abs(null_k) >= abs(obs_k))) / (1 + len(null_k)))}
# robustness: 2026 only
k26 = keep & (DATES[post] >= '2026-01-01')
obs26 = delta_sub(z, k26); null26 = np.array([delta_sub(rng.permutation(z), k26) for _ in range(20000)])
out['robust_2026_only_drop_pb_in_D'] = {'n': int(k26.sum()), 'delta': obs26,
                                        'p_two_sided': float((1 + np.sum(np.abs(null26) >= abs(obs26))) / (1 + len(null26)))}
print(out['robust_drop_pb_in_D'], out['robust_2026_only_drop_pb_in_D'])
json.dump(out, open(os.path.join(BASE, 'redteam_g.json'), 'w'), indent=1)

# money: extra-number bonus for the FINAL fields with the interaction applied at their winning draws
zall = DALL.astype(np.float64) @ f3['beta']
zs = (zall - (Z[post] @ f3['beta']).mean()) / (Z[post] @ f3['beta']).std()
cx = cbar[1:] - cbar[1:].mean()
sh26 = extra_shares(DATES >= '2026-01-01')
lg = np.log(sh26 / (1 - sh26))
money = {}
for lab, f, x in (('field1', FINAL[0], FINAL[1]), ('field2', FINAL[2], FINAL[3])):
    S = np.zeros(27, bool); S[np.array(f) - 1] = True; ov = DB[:, S].sum(1)
    zb = {m: float(zs[ov == m].mean()) for m in (3, 4, 5)}
    K0 = K_extra(sh26, fp); Kb = K0.mean(1)
    bonus0 = float(100 * (K0[:, x - 1].sum() / Kb.sum() - 1))
    Kadj = np.zeros(3)
    for ci, m in enumerate((3, 4, 5)):
        sa = 1 / (1 + np.exp(-(lg + out['delta'] * zb[m] * cx)))
        Kadj[ci] = K_extra(sa, fp)[ci, x - 1] / K_extra(sa, fp)[ci].mean() * Kb[ci]
    money[lab] = {'mean_z_of_winning_draws': zb, 'extra_bonus_pct_2026_shares': bonus0,
                  'extra_bonus_pct_with_interaction': float(100 * (Kadj.sum() / Kb.sum() - 1))}
out['final_fields_extra_bonus'] = money
print(json.dumps(money, indent=1))
json.dump(out, open(os.path.join(BASE, 'redteam_g.json'), 'w'), indent=1)
