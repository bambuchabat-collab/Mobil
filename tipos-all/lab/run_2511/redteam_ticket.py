"""Red team, part 5: check of the single ticket for 25.11.2026 (python3 -I -B, numpy, exact integer odds).
Pattern checks on the ticket T and its complement C, with the share of ALL 705 432 possible tickets that would
fail the same check (so 'pattern' means something rarer than a typical random ticket), comparison with the last
draws, A10 popularity score (prize-sharing proxy) and exact odds. Writes redteam_ticket.json."""
import sys, os, json, itertools
from fractions import Fraction
from math import comb
sys.dont_write_bytecode = True
RUN = '/home/user/Mobil/tipos-all/lab/run_2511'
sys.path.insert(0, RUN)
import numpy as np
from harness import DRAWS

T = [1, 4, 7, 8, 10, 11, 14, 16, 18, 20, 21]
U = set(range(1, 23))
C = sorted(U - set(T))
LEAD_C = [2, 3, 5, 6, 9, 12, 13, 15, 17, 19, 22]
LAST = {'2026-11-23': [1, 5, 6, 8, 9, 10, 13, 14, 15, 18, 21], '2026-11-24': [1, 2, 4, 6, 7, 14, 15, 17, 20, 21, 22]}

# ---- enumerate all tickets as bitmasks ----
ALLM = np.array([sum(1 << (x - 1) for x in c) for c in itertools.combinations(range(1, 23), 11)], np.int64)
mask = lambda S: sum(1 << (x - 1) for x in S)
bits = ((ALLM[:, None] >> np.arange(22)) & 1).astype(np.int8)          # (705432, 22)


def longest_run_all():
    best = np.zeros(len(ALLM), np.int8); cur = np.zeros(len(ALLM), np.int8)
    for i in range(22):
        cur = np.where(bits[:, i] == 1, cur + 1, 0).astype(np.int8); best = np.maximum(best, cur)
    return best


def aps():
    out = []                                         # (length, d, start, mask)
    for d in range(1, 22):
        for a in range(1, 23):
            L = 0; S = []
            while a + L * d <= 22:
                S.append(a + L * d); L += 1
                if L >= 3: out.append((L, d, a, mask(S)))
    return out
AP = aps()


def longest_ap_all():
    best = np.full(len(ALLM), 2, np.int8)
    for L, d, a, mk in AP:
        hit = (ALLM & mk) == mk
        best = np.where(hit & (best < L), L, best).astype(np.int8)
    return best


def longest_ap(S):
    mS = mask(S); best = (2, None)
    for L, d, a, mk in AP:
        if (mS & mk) == mk and L > best[0]: best = (L, [a + i * d for i in range(L)])
    return best


def longest_run(S):
    best = cur = 0
    for x in range(1, 23):
        cur = cur + 1 if x in S else 0; best = max(best, cur)
    return best


def layouts():
    """row-major slips of width w: rows = consecutive blocks, columns = residues; only lines of length >= 4."""
    lines = {}
    for w in range(4, 12):
        rows = [list(range(s, min(s + w, 23))) for s in range(1, 23, w)]
        cols = [list(range(c, 23, w)) for c in range(1, w + 1)]
        lines[w] = [('row', r) for r in rows if len(r) >= 4] + [('col', c) for c in cols if len(c) >= 4]
    return lines
LINES = layouts()


def full_lines(S):
    S = set(S); return {str(w): [f'{k}:{l}' for k, l in L if set(l) <= S] for w, L in LINES.items() if any(set(l) <= S for k, l in L)}


def any_full_line_all():
    hit = np.zeros(len(ALLM), bool)
    for w, L in LINES.items():
        for k, l in L:
            mk = mask(l); hit |= (ALLM & mk) == mk
    return hit


run_all = longest_run_all(); ap_all = longest_ap_all(); line_all = any_full_line_all()
odd_all = bits[:, 0::2].sum(1); low_all = bits[:, :11].sum(1)


def describe(S):
    S = sorted(S); st = set(S)
    L, apseq = longest_ap(S)
    r = longest_run(st)
    n_odd = sum(x % 2 for x in S); n_low = sum(x <= 11 for x in S)
    return {'numbers': S, 'n': len(S), 'distinct_in_range': len(st) == 11 and all(1 <= x <= 22 for x in S),
            'n_odd': n_odd, 'all_odd_or_even': n_odd in (0, 11), 'n_in_1_11': n_low, 'is_1_11_or_12_22': n_low in (0, 11),
            'longest_run': r, 'run_gt_3': r > 3, 'share_tickets_with_longer_or_equal_run': float((run_all >= r).mean()),
            'longest_AP': L, 'longest_AP_seq': apseq, 'share_tickets_with_AP_ge_this': float((ap_all >= L).mean()),
            'whole_set_is_AP': L == 11, 'full_lines_len_ge4_layouts_w4_11': full_lines(S),
            'share_tickets_with_any_full_line': float(line_all.mean()),
            'sum': sum(S), 'sum_mean_sd': [126.5, (11 * 40.25 * 11 / 21) ** 0.5],
            'mirror_23_minus_x_overlap': len(st & {23 - x for x in S})}


# last draws and the transform family of A7 (rotations, reflections, parity) applied to the last draw
def fam():
    G = [lambda x, k=k: ((x - 1 + k) % 22) + 1 for k in range(0, 22)]
    G += [lambda x, c=c: ((c - x) % 22) + 1 for c in range(22)]
    G += [lambda x: x + 1 if x % 2 else x - 1]
    return G
last2 = {}
for d in DRAWS[-2:]:
    last2[d['date']] = d['main']
assert last2 == LAST, (last2, LAST)
vs_last = {}
for D, S in LAST.items():
    imgs = [set(g(x) for x in S) for g in fam()]
    vs_last[D] = {'hits_if_T_had_played': len(set(T) & set(S)), 'equal': sorted(T) == S, 'equal_complement': C == S,
                  'T_equals_any_rotation_reflection_parity_image_or_its_complement':
                      any(set(T) == I or set(T) == U - I for I in imgs),
                  'max_overlap_with_those_images': max(max(len(set(T) & I), len(set(T) & (U - I))) for I in imgs)}
hist_ov = [len(set(T) & set(d['main'])) for d in DRAWS]
hist = {'equal_any_past_draw': any(sorted(T) == d['main'] for d in DRAWS),
        'equal_complement_any_past_draw': any(C == d['main'] for d in DRAWS),
        'overlap_range_over_412_draws': [min(hist_ov), max(hist_ov)], 'mean_overlap': float(np.mean(hist_ov))}
agent_tickets = {}
for i in range(1, 11):
    j = json.load(open(os.path.join(RUN, 'agents', f'A{i}.json')))
    agent_tickets[j['id']] = len(set(T) & set(j['ticket_25_11']))

# popularity proxy (A10 ridge betas from tier data 0..409): where does T / C sit among all tickets?
b = json.load(open(os.path.join(RUN, 'agents', 'A10.json')))['popularity_beta_0_409']
beta = np.array([b[str(x)] for x in range(1, 23)])
pop_all = bits @ beta
pop = {'T_score': float(beta[np.array(T) - 1].sum()), 'C_score': float(beta[np.array(C) - 1].sum())}
pop['T_percentile'] = float((pop_all < pop['T_score']).mean()); pop['C_percentile'] = float((pop_all < pop['C_score']).mean())
# sampling SE of the T-vs-C popularity contrast under A10's own ridge model (sandwich with residual variance)
VAN = json.load(open('/home/user/Mobil/tipos-all/lab/run_2311/data/van.json'))
yv = np.array([np.log((sum(v['tiers'][k][1] for k in ('8', '9', '10')) + 0.5) /
                      (sum(v['tiers'][k][1] for k in ('3', '2', '1')) + 0.5)) for v in VAN])
Xv = np.zeros((len(VAN), 22))
for i_, v in enumerate(VAN): Xv[i_, np.array(v['main']) - 1] = 1
Xc = Xv - Xv.mean(0); yc = yv - yv.mean()
A = np.linalg.inv(Xc.T @ Xc + np.eye(22))
bh_ = A @ Xc.T @ yc
s2 = float(((yc - Xc @ bh_) ** 2).sum() / (len(yc) - 22))
cvec = np.zeros(22); cvec[np.array(T) - 1] = 1
V = s2 * A @ (Xc.T @ Xc) @ A
pop['beta_reproduced'] = bool(np.allclose(bh_, beta, atol=1e-9))
pop['T_score_se'] = float(np.sqrt(cvec @ V @ cvec)); pop['T_score_z'] = pop['T_score'] / pop['T_score_se']
pop['note'] = ('A10 betas are noisy (A10 found no draw effect); a mid percentile = neither a popular nor an unpopular '
               'combination by this proxy. Score(T) = -Score(C) + const, so T and C sit at mirrored percentiles.')

# exact odds
TOT = comb(22, 11)
P = {k: Fraction(comb(11, k) * comb(11, 11 - k), TOT) for k in range(12)}
prize = {11: 100000, 10: 200, 9: 20, 8: 3, 3: 3, 2: 20, 1: 200, 0: 100000}
fr = lambda f: {'fraction': f'{f.numerator}/{f.denominator}', 'one_in': float(1 / f) if f else None, 'percent': float(f * 100)}
odds = {'P_hits': {str(k): fr(P[k]) for k in range(12)},
        'P_0': fr(P[0]), 'P_0_or_11': fr(P[0] + P[11]),
        'P_any_prize': fr(sum(P[k] for k in prize)), 'P_5_or_6': fr(P[5] + P[6]), 'P_4_to_7_no_prize': fr(sum(P[k] for k in range(4, 8))),
        'P_5': fr(P[5]), 'P_6': fr(P[6]),
        'expected_payout_eur_unshared_top': float(sum(P[k] * v for k, v in prize.items())),
        'expected_payout_eur_without_top': float(sum(P[k] * v for k, v in prize.items() if k not in (0, 11)))}
odds['claims'] = {'P0=1/705432': P[0] == Fraction(1, 705432), 'P0or11=1/352716': P[0] + P[11] == Fraction(1, 352716),
                  'P_any_prize_8.61%': round(float(sum(P[k] for k in prize)) * 100, 2) == 8.61}

dT, dC = describe(T), describe(C)
problems = []
for nm, d in (('T', dT), ('C', dC)):
    if not d['distinct_in_range']: problems.append(nm + ' invalid')
    if d['all_odd_or_even']: problems.append(nm + ' all odd/even')
    if d['run_gt_3']: problems.append(nm + ' run > 3')
    if d['is_1_11_or_12_22']: problems.append(nm + ' 1-11/12-22')
    if d['whole_set_is_AP'] or d['longest_AP'] >= 6: problems.append(nm + f" AP length {d['longest_AP']}")
    if d['full_lines_len_ge4_layouts_w4_11']: problems.append(nm + ' contains a full slip line (len>=4) in some layout')
for D, v in vs_last.items():
    if v['equal'] or v['equal_complement'] or v['T_equals_any_rotation_reflection_parity_image_or_its_complement']:
        problems.append('related to draw ' + D)
OUT = {'ticket': T, 'complement': C, 'complement_matches_lead': C == LEAD_C, 'T': dT, 'C': dC, 'vs_last_draws': vs_last,
       'vs_history': hist, 'overlap_with_agents_25_11_tickets': agent_tickets, 'popularity_proxy': pop, 'odds': odds,
       'problems': problems, 'verdict': 'TICKET OK' if not problems else 'TICKET CHANGE'}
json.dump(OUT, open(os.path.join(RUN, 'redteam_ticket.json'), 'w'), indent=1)
print(json.dumps(OUT, indent=1))
