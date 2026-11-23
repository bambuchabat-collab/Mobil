"""Red team, attack (f): verify every user constraint on the final / runner-up tickets and look for recognisable
patterns (generic bet-slip grids of width 3..10: rows, columns, diagonals), overlap with earlier project tickets.
python3 -I redteam_f_tickets.py -> ../redteam_f.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from redteam_common import *

EARLIER = ([1, 2, 14, 20, 22, 23], 6, [8, 10, 15, 16, 18, 19], 5)


def lines(f, w):
    """max numbers of the field on one row / column / diagonal / anti-diagonal of a row-major grid of width w"""
    rc = [((v - 1) // w, (v - 1) % w) for v in f]
    best = {}
    for name, key in (('row', lambda r, c: r), ('col', lambda r, c: c), ('diag', lambda r, c: c - r), ('anti', lambda r, c: c + r)):
        ks = [key(r, c) for r, c in rc]
        best[name] = max(ks.count(k) for k in set(ks))
    return best


def check(tk):
    fa, xa, fb, xb = tk
    res = {}
    for lab, f, x in (('field1', fa, xa), ('field2', fb, xb)):
        gaps = list(np.diff(sorted(f)))
        res[lab] = {'numbers': f, 'extra': x, 'six_distinct_in_1_27': len(set(f)) == 6 and all(1 <= v <= 27 for v in f),
                    'run_of_3': has_run3(f), 'ap3_triples': ap3(f), 'consecutive_pairs': npairs(f), 'gaps': [int(g) for g in gaps],
                    'all_gaps_distinct(stricter reading of no equal steps)': len(set(gaps)) == len(gaps),
                    'extra_in_5_6_7': x in (5, 6, 7), 'extra_in_own_field': x in f, 'sum': int(sum(f)),
                    'claimed_popularity_ranks(1=least)': [CLAIM_ORDER.index(v) + 1 for v in f],
                    'max_on_one_line_grid_w3..10': {w: max(lines(f, w).values()) for w in range(3, 11)}}
    res['disjoint'] = not (set(fa) & set(fb)); res['extras_differ'] = xa != xb
    res['all_numbers_within_claimed_k_least_popular'] = max(CLAIM_ORDER.index(v) + 1 for v in fa + fb)
    res['numbers_outside_12_least_popular'] = sorted(v for v in fa + fb if CLAIM_ORDER.index(v) >= 12)
    res['common_with_earlier_project_tickets'] = [sorted(set(fa) & set(EARLIER[0])), sorted(set(fb) & set(EARLIER[2]))]
    res['ALL_USER_CONSTRAINTS_OK'] = bool(res['disjoint'] and res['extras_differ'] and all(
        res[l]['six_distinct_in_1_27'] and not res[l]['run_of_3'] and not res[l]['ap3_triples'] and res[l]['extra_in_5_6_7']
        for l in ('field1', 'field2')))
    return res


# how unusual is "max on one grid line" for random valid fields (reference distribution)
rng = np.random.default_rng(11)
ref = {w: [] for w in range(3, 11)}
for _ in range(4000):
    f = sorted(rng.choice(np.arange(1, 28), 6, replace=False).tolist())
    for w in range(3, 11):
        ref[w].append(max(lines(f, w).values()))
out = {'FINAL': check(FINAL), 'RUNNER_UP': check(RUNNER),
       'reference_P(max_on_line >= value)_random_field': {w: {k: float(np.mean(np.array(ref[w]) >= k)) for k in (3, 4, 5)} for w in ref}}
print(json.dumps(out, indent=1, default=str)[:5000])
json.dump(out, open(os.path.join(BASE, 'redteam_f.json'), 'w'), indent=1, default=str)
