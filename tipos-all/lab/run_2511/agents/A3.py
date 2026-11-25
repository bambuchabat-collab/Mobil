"""A3: per-number Markov chains and pooled run-length (gap) hazard. See A3_prereg.md."""
import sys, json
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2511')
import numpy as np
from harness import evaluate, DRAWS

CAP = 6
SEED = 20251125


def matrix(past):
    X = np.zeros((len(past), 22), dtype=np.int8)
    for u, d in enumerate(past):
        for x in d['main']:
            X[u, x - 1] = 1
    return X


def pick_lowest(q, T):
    jitter = np.random.default_rng(SEED + T).random(22) * 1e-9
    idx = np.argsort(q + jitter, kind='stable')[:11]
    return sorted(int(i) + 1 for i in idx)


def r1(past):
    X = matrix(past); T = len(X)
    prev, nxt = X[:-1], X[1:]
    q = np.empty(22)
    for i in range(22):
        s = X[-1, i]
        m = prev[:, i] == s
        q[i] = (nxt[m, i].sum() + 1) / (m.sum() + 2)
    return pick_lowest(q, T)


def r2(past):
    X = matrix(past); T = len(X)
    a, b, nxt = X[:-2], X[1:-1], X[2:]
    q = np.empty(22)
    for i in range(22):
        ca, cb = X[-2, i], X[-1, i]
        m = (a[:, i] == ca) & (b[:, i] == cb)
        q[i] = (nxt[m, i].sum() + 1) / (m.sum() + 2)
    return pick_lowest(q, T)


def run_states(X):
    """signed run length (capped) at each time u, per number, from draws <= u."""
    T = len(X); R = np.zeros((T, 22), dtype=np.int16)
    for i in range(22):
        run = 0
        for u in range(T):
            if u > 0 and X[u, i] == X[u - 1, i]:
                run += 1
            else:
                run = 1
            L = min(run, CAP)
            R[u, i] = L if X[u, i] == 1 else -L
    return R


def r3(past):
    X = matrix(past); T = len(X)
    R = run_states(X)
    states = R[:-1].ravel(); outc = X[1:].ravel()
    h = {}
    for r in list(range(-CAP, 0)) + list(range(1, CAP + 1)):
        m = states == r
        h[r] = (outc[m].sum() + 1) / (m.sum() + 2)
    q = np.array([h[int(R[-1, i])] for i in range(22)])
    return pick_lowest(q, T)


DEFS = {
    'R1': 'per-number 1st-order Markov: q_i=(k_i(s)+1)/(n_i(s)+2), s=x_i(last draw), all past draws; 11 lowest q; ties by fixed-seed jitter',
    'R2': 'per-number 2nd-order Markov: q_i=(k_i(ab)+1)/(n_i(ab)+2), (a,b)=last two states, all past draws; 11 lowest q; ties by jitter',
    'R3': 'pooled signed run-length hazard (gap if absent, streak if present, capped 6), Laplace, all numbers & past draws; 11 lowest; ties by jitter',
}

if __name__ == '__main__':
    rules = []
    for name, f in (('R1', r1), ('R2', r2), ('R3', r3)):
        res = evaluate(f, 'A3_' + name)
        res = {k: (float(v) if isinstance(v, (float, np.floating)) else int(v) if isinstance(v, (int, np.integer)) else v)
               for k, v in res.items()}
        res['definition'] = DEFS[name]
        res['ticket_25_11'] = f(DRAWS)
        rules.append(res)
        print(json.dumps(res))
    out = {'id': 'A3', 'family': 'PER-NUMBER MARKOV CHAINS AND GAP/HAZARD MODELS',
           'rules': rules, 'ticket_25_11': r1(DRAWS)}
    json.dump(out, open('/home/user/Mobil/tipos-all/lab/run_2511/agents/A3.json', 'w'), indent=1, ensure_ascii=False)
