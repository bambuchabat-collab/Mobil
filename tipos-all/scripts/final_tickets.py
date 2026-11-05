"""Final tickets: coverage-optimal shapes filled with the least popular numbers.
Usage: python3 -I final_tickets.py research.json out.json
"""
import json, sys, itertools, math
import numpy as np
R = json.load(open(sys.argv[1])); OUT = sys.argv[2]
bl = np.array(R['pop_loto535']['beta']); be = np.array(R['pop_extra']['beta'])

def runs(t):
    t = sorted(t); best = cur = 1
    for a, b in zip(t, t[1:]):
        cur = cur + 1 if b == a + 1 else 1; best = max(best, cur)
    return best

def deal(nums, n_t, k):
    nums = sorted(nums); return [sorted(nums[i::n_t]) for i in range(n_t)]

def cover(tickets, n, k, thr):
    combos = np.array(list(itertools.combinations(range(1, n + 1), k)), dtype=np.int64)
    cm = np.zeros(len(combos), dtype=np.uint64)
    for j in range(k): cm |= (np.uint64(1) << combos[:, j].astype(np.uint64))
    best = np.zeros(len(cm), np.int8)
    for t in tickets:
        m = 0
        for v in t: m |= 1 << v
        best = np.maximum(best, np.bitwise_count(cm & np.uint64(m)).astype(np.int8))
    return float((best >= thr).mean()), combos

# ---------- Extra výplata: 3 disjoint tickets (coverage-optimal), 18 least popular numbers ----------
blend = 0.6 * (bl[:27] - bl[:27].mean()) + 0.4 * be      # Loto 5 z 35 preferences carry over; EV data alone is too short
order = np.argsort(blend)
keep = sorted((order[:18] + 1).tolist()); drop = sorted((order[18:] + 1).tolist())
ev = deal(keep, 3, 6)
assert all(runs(t) <= 3 for t in ev)
cov_ev, combos27 = cover(ev, 27, 6, 3)
pbs = [7, 6, 5]
pbr = {int(k): v['ratio'] for k, v in R['pb_pop_extra'].items()}
# relative popularity of each ticket vs an average ticket (model units: exp of summed coefficients)
def relpop(t, beta, combos):
    allv = np.exp(beta[combos - 1].sum(1)); return float(np.exp(beta[np.array(t) - 1].sum()) / allv.mean())
ev_rel = [relpop(t, blend, combos27) for t in ev]

# ---------- Loto 5 z 35: 5 fields, 25 least popular numbers ----------
order_l = np.argsort(bl)
keep_l = sorted((order_l[:25] + 1).tolist()); drop_l = sorted((order_l[25:] + 1).tolist())
l5 = deal(keep_l, 5, 5)
assert all(runs(t) <= 3 for t in l5)
cov_l, combos35 = cover(l5, 35, 5, 3)
l_rel = [relpop(t, bl, combos35) for t in l5]
out = {'extra': {'tickets': [{'main': t, 'pb': p} for t, p in zip(ev, pbs)], 'dropped_popular': drop, 'cover_any_prize': cov_ev,
                 'rel_popularity': ev_rel, 'pb_ratio': {p: pbr[p] for p in pbs}, 'pb_ratio_all': pbr},
       'loto535': {'fields': l5, 'dropped_popular': drop_l, 'cover_any_prize': cov_l, 'rel_popularity': l_rel,
                   'most_popular': (np.argsort(-bl)[:8] + 1).tolist(), 'least_popular': (order_l[:8] + 1).tolist()}}
json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
