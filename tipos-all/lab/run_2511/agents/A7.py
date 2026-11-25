"""A7: geometric / transform rules on the previous draw (see A7_prereg.md). Run: python3 -I A7.py"""
import sys, json
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2511')
import numpy as np
from harness import evaluate, DRAWS

N = 22
ALL = set(range(1, N + 1))

# ---- transform family G (1-based maps as 0-based arrays: G[i][x-1] = g(x)-1) ----
def rot(k): return lambda x: ((x - 1 + k) % N) + 1
def refl(c): return lambda x: ((c - x) % N) + 1
def parity(x): return x + 1 if x % 2 == 1 else x - 1

FAMILY = [('rot%d' % k, rot(k)) for k in range(1, 22)] + \
         [('refl%d' % c, refl(c)) for c in range(0, 22)] + [('parity', parity)]
G = np.array([[g(x) - 1 for x in range(1, N + 1)] for _, g in FAMILY])
for row in G: assert sorted(row) == list(range(N))
assert len({tuple(r) for r in G}) == 44 and list(G[21]) == [22 - x for x in range(1, 23)]  # refl0 = 23-x

def ind(draws):
    X = np.zeros((len(draws), N), int)
    for i, d in enumerate(draws): X[i, np.array(d['main']) - 1] = 1
    return X

def image(g_row, S):
    return {int(g_row[x - 1]) + 1 for x in S}

# ---- R1: adaptive selection over 88 candidates (44 transforms x {image, complement}) ----
def r1_choice(past):
    X = ind(past)
    prev, nxt = X[:-1], X[1:]
    best = None
    for i, row in enumerate(G):
        s_img = int((prev * nxt[:, row]).sum())          # sum_s |g(D_{s-1}) ∩ D_s|
        s_cmp = 11 * len(nxt) - s_img                     # complement of image
        for j, sc in ((0, s_img), (1, s_cmp)):
            if best is None or sc < best[0]: best = (sc, i, j)
    return best

def R1(past):
    sc, i, j = r1_choice(past)
    T = image(G[i], past[-1]['main'])
    return T if j == 0 else ALL - T

# ---- R2: mirror 23-x, direction fixed on draws 0..29 ----
def mirror(S): return {23 - x for x in S}
m0 = np.mean([len(mirror(DRAWS[s - 1]['main']) & set(DRAWS[s]['main'])) for s in range(1, 30)])
R2_IMAGE = m0 <= 5.5
def R2(past):
    T = mirror(past[-1]['main'])
    return T if R2_IMAGE else ALL - T

# ---- R3: 5-column slip, Moore-neighbour density of previous draw ----
POS = {x: ((x - 1) // 5, (x - 1) % 5) for x in ALL}
CELL = {v: k for k, v in POS.items()}
NB = {x: [CELL[(POS[x][0] + dr, POS[x][1] + dc)] for dr in (-1, 0, 1) for dc in (-1, 0, 1)
          if (dr or dc) and (POS[x][0] + dr, POS[x][1] + dc) in CELL] for x in ALL}
TIE = {int(x): i for i, x in enumerate(np.random.default_rng(2511).permutation(22) + 1)}
def r3_low(P):
    P = set(P)
    order = sorted(ALL, key=lambda x: (sum(y in P for y in NB[x]) / len(NB[x]), TIE[x]))
    return set(order[:11])
a0 = np.mean([len(r3_low(DRAWS[s - 1]['main']) & set(DRAWS[s]['main'])) for s in range(1, 30)])
R3_LOW = a0 <= 5.5
def R3(past):
    A = r3_low(past[-1]['main'])
    return A if R3_LOW else ALL - A

if __name__ == '__main__':
    defs = {
        'R1': 'Adaptive: among 88 candidates (21 rotations, 22 reflections incl. 23-x, parity flip; each as image '
              'g(P) or complement C(g(P))) pick the one with least cumulative overlap with the next draw over all '
              'past transitions; ticket = that candidate applied to the previous draw. Ties -> first in order.',
        'R2': 'Mirror x->23-x of previous draw; orientation (image vs complement) fixed on draws 0..29: m0=%.4f -> %s'
              % (m0, 'image' if R2_IMAGE else 'complement'),
        'R3': '5-column slip (rows 1-5,...,21-22), Moore-neighbour density of previous draw, 11 lowest (seeded '
              'tiebreak 2511) or highest; orientation fixed on draws 0..29: a0=%.4f -> %s'
              % (a0, 'lowest' if R3_LOW else 'highest'),
    }
    rules = []
    for name, f in (('R1', R1), ('R2', R2), ('R3', R3)):
        r = evaluate(f, name)
        r = {k: (float(v) if isinstance(v, (float, np.floating)) else int(v) if isinstance(v, (int, np.integer)) else v)
             for k, v in r.items()}
        r['definition'] = defs[name]
        rules.append(r); print(r)
    # which candidate R1 picked over the walk-forward (diagnostic)
    picks = {}
    for t in range(30, len(DRAWS)):
        _, i, j = r1_choice(DRAWS[:t]); key = FAMILY[i][0] + ('' if j == 0 else '_C')
        picks[key] = picks.get(key, 0) + 1
    sc, i, j = r1_choice(DRAWS)
    ticket = sorted(int(x) for x in R1(DRAWS))
    out = {'id': 'A7', 'family': 'GEOMETRIC / TRANSFORM RULES on the previous draw(s)', 'rules': rules,
           'r1_pick_counts': picks,
           'r1_choice_for_25_11': {'transform': FAMILY[i][0], 'orientation': 'image' if j == 0 else 'complement',
                                   'mean_overlap_past': sc / (len(DRAWS) - 1)},
           'ticket_25_11': ticket}
    print(picks, out['r1_choice_for_25_11'], ticket)
    json.dump(out, open('/home/user/Mobil/tipos-all/lab/run_2511/agents/A7.json', 'w'), indent=1, ensure_ascii=False)
