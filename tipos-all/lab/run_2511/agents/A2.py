"""A2 — CO-OCCURRENCE / PAIRS family. See A2_prereg.md for the pre-registered definitions."""
import sys, json, itertools
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2511')
import numpy as np
from harness import evaluate, DRAWS

np.random.seed(2511)  # not used (all rules deterministic); fixed for the record
NUM = np.arange(1, 23)


def ind(past):
    X = np.zeros((len(past), 22))
    for k, d in enumerate(past):
        X[k, np.array(d['main']) - 1] = 1.0
    return X


def r1_scores(X):
    P, Q = X[:-1], X[1:]
    M = len(P)
    A = P.T @ Q
    a, b = P.sum(0), Q.sum(0)
    R = A - np.outer(a, b) / M
    return X[-1] @ R  # s_j = sum_{i in D_last} R[i, j]


def lowest11(score):
    return [int(x) for x in NUM[np.argsort(score, kind='stable')[:11]]]


def rule_r1(past):
    return lowest11(r1_scores(ind(past)))


def phi_matrix(X):
    N = len(X)
    c = X.sum(0)
    n = X.T @ X
    den = np.sqrt(np.outer(c * (N - c), c * (N - c)))
    with np.errstate(divide='ignore', invalid='ignore'):
        phi = np.where(den > 0, (N * n - np.outer(c, c)) / den, 0.0)
    np.fill_diagonal(phi, 0.0)
    return phi


def rule_r2(past):
    X = ind(past)
    s = r1_scores(X)
    Pidx = np.argsort(s, kind='stable')[11:]  # 11 highest s_j = predicted draw
    phi = phi_matrix(X)
    u = np.empty(22)
    for k in range(22):
        others = [p for p in Pidx if p != k]
        u[k] = phi[k, others].mean()
    return lowest11(u)


# all partitions with number 1 in side A, in itertools.combinations order
COMBS = [(0,) + c for c in itertools.combinations(range(1, 22), 10)]
XA = np.zeros((len(COMBS), 22), np.float64)
for r, c in enumerate(COMBS):
    XA[r, list(c)] = 1.0


def rule_r3(past):
    X = ind(past)
    phi = phi_matrix(X)
    # 2*W = 2 x'Phi x - 2 x'Phi1 + 1'Phi1  (Phi symmetric, zero diag) -> maximise x'Phi x - x'rowsum
    obj = ((XA @ phi) * XA).sum(1) - XA @ phi.sum(1)
    best = int(np.argmax(obj))  # first max in combinations order
    A = np.zeros(22, bool); A[list(COMBS[best])] = True
    x = X[:, A].sum(1)
    if len(x) > 2 and x[:-1].std() > 0 and x[1:].std() > 0:
        r = float(np.corrcoef(x[:-1], x[1:])[0, 1])
    else:
        r = 0.0
    last_A = x[-1] > 5.5
    pred_A = last_A if r >= 0 else (not last_A)
    ticket_mask = ~A if pred_A else A
    return [int(v) for v in NUM[ticket_mask]]


DEFS = {
    'R1': 'lag-1 pair residual R[i,j]=A[i,j]-a_i b_j/M over all past transitions; s_j=sum_{i in last draw} R[i,j]; '
          'ticket = 11 lowest s_j (primary)',
    'R2': 'predicted draw P = 11 highest R1 scores; contemporaneous phi over all past draws; u_k = mean_{p in P\\k} phi[k,p]; '
          'ticket = 11 lowest u_k',
    'R3': 'max within-group phi 11/11 partition (exhaustive, all past draws); side predicted by sign of lag-1 autocorr '
          'of overlap with side A applied to last draw; ticket = other side',
}

if __name__ == '__main__':
    rules = []
    for name, fn in [('R1', rule_r1), ('R2', rule_r2), ('R3', rule_r3)]:
        res = evaluate(fn, name)
        res = {k: (float(v) if isinstance(v, (np.floating, float)) else int(v) if isinstance(v, (np.integer,)) else v)
               for k, v in res.items()}
        res['definition'] = DEFS[name]
        res['ticket_25_11'] = sorted(fn(DRAWS))
        rules.append(res)
        print(json.dumps(res, ensure_ascii=False))
    out = {'id': 'A2', 'family': 'CO-OCCURRENCE / PAIRS', 'rules': rules,
           'ticket_25_11': sorted(rule_r1(DRAWS))}
    json.dump(out, open('/home/user/Mobil/tipos-all/lab/run_2511/agents/A2.json', 'w'), ensure_ascii=False, indent=1)
    print('ticket_25_11 (R1):', out['ticket_25_11'])
