"""A1: DRAW ORDER / BALL POSITION family. Pre-registration: A1_prereg.md (written before running this)."""
import sys, json, os
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2511')
from harness import evaluate, DRAWS
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NUMS = list(range(1, 23))


def r1_late_ball(past):
    """11 numbers with the largest mean draw position (1..11) over all past draws; never drawn -> 12."""
    s = {x: 0 for x in NUMS}; c = {x: 0 for x in NUMS}
    for d in past:
        for pos, x in enumerate(d['order'], 1):
            s[x] += pos; c[x] += 1
    m = {x: (s[x] / c[x] if c[x] else 12.0) for x in NUMS}
    ranked = sorted(NUMS, key=lambda x: (-m[x], c[x], x))
    return ranked[:11]


def r2_early_recent(past):
    """First-drawn balls of the last 3 draws: positions 1..11, lags 1..3 within each position, until 11 numbers."""
    T = []
    for p in range(11):
        for L in (1, 2, 3):
            x = past[-L]['order'][p]
            if x not in T:
                T.append(x)
                if len(T) == 11:
                    return T
    raise RuntimeError('unreachable')


def r3_transition(past, n_sim=10000):
    """Markov order model: first ball ~ F+1, next ball ~ C[prev]+1 among remaining; 11 lowest inclusion probs."""
    F = np.ones(23); F[0] = 0
    C = np.ones((23, 23)); C[:, 0] = 0
    for d in past:
        o = d['order']
        F[o[0]] += 1
        for a, b in zip(o[:-1], o[1:]):
            C[a, b] += 1
    rng = np.random.default_rng(20261125 + len(past))
    used = np.zeros((n_sim, 23), bool); used[:, 0] = True
    inc = np.zeros(23)
    w = np.broadcast_to(F, (n_sim, 23)).copy()
    for step in range(11):
        w[used] = 0
        cw = np.cumsum(w, axis=1)
        u = rng.random(n_sim) * cw[:, -1]
        pick = (cw < u[:, None]).sum(axis=1)
        used[np.arange(n_sim), pick] = True
        w = C[pick].copy()
    inc = used[:, 1:].mean(axis=0)               # inclusion prob for numbers 1..22
    ranked = sorted(NUMS, key=lambda x: (inc[x - 1], x))
    return ranked[:11]


RULES = [
    ('R1', r1_late_ball, 'PRIMARY. 11 numbers with largest mean draw position (1..11) over all past draws in which drawn '
                         '(never drawn -> 12); tie-break fewer appearances, then smaller number.'),
    ('R2', r2_early_recent, 'Early balls of last 3 draws: scan positions 1..11, within each lags 1,2,3 (most recent first), '
                            'add order[p] if new, stop at 11.'),
    ('R3', r3_transition, 'Order-transition Markov model from all past draws: first ball ~ F+1, next ~ C[prev][b]+1 among '
                          'remaining; 10000 sims, seed 20261125+len(past); 11 lowest inclusion probabilities.'),
]


def plain(o):
    if isinstance(o, dict): return {k: plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [plain(v) for v in o]
    if isinstance(o, np.integer): return int(o)
    if isinstance(o, np.floating): return float(o)
    return o


if __name__ == '__main__':
    out = {'id': 'A1', 'family': 'DRAW ORDER / BALL POSITION', 'rules': []}
    for name, f, definition in RULES:
        r = evaluate(f, name)
        r['definition'] = definition
        r['ticket_25_11'] = sorted(int(x) for x in f(DRAWS))
        out['rules'].append(plain(r))
        print(json.dumps(plain(r)))
    out['ticket_25_11'] = sorted(int(x) for x in r1_late_ball(DRAWS))
    json.dump(out, open(os.path.join(HERE, 'A1.json'), 'w'), indent=1)
    print('ticket_25_11 (R1):', out['ticket_25_11'])
