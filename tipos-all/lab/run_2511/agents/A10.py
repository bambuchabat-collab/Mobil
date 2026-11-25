"""A10 — PLAYER POPULARITY family. See A10_prereg.md for the pre-registered definitions."""
import sys, json
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2511')
from harness import evaluate, DRAWS
import numpy as np

np.random.seed(0)
VAN = json.load(open('/home/user/Mobil/tipos-all/lab/run_2311/data/van.json'))
NT = len(VAN)                      # 410 draws with tier data (indices 0..409)
for i in range(NT):
    assert VAN[i]['date'] == DRAWS[i]['date'] and sorted(VAN[i]['main']) == DRAWS[i]['main']
LAMBDA = 1.0

def y_of(s):
    t = VAN[s]['tiers']
    H = sum(t[k][1] for k in ('8', '9', '10'))
    L = sum(t[k][1] for k in ('3', '2', '1'))
    return float(np.log((H + 0.5) / (L + 0.5)))

Y = np.array([y_of(s) for s in range(NT)])
X = np.zeros((NT, 22))
for s in range(NT):
    for n in VAN[s]['main']:
        X[s, n - 1] = 1.0

_cache = {}
def popularity(m):
    """Ridge beta from tier draws 0..m-1."""
    if m not in _cache:
        Xm, ym = X[:m], Y[:m]
        Xc = Xm - Xm.mean(0); yc = ym - ym.mean()
        _cache[m] = np.linalg.solve(Xc.T @ Xc + LAMBDA * np.eye(22), Xc.T @ yc)
    return _cache[m]

def ranked(past):
    m = min(len(past), NT)
    b = popularity(m)
    return sorted(range(1, 23), key=lambda n: (-b[n - 1], n))   # most popular first

def R1(past): return ranked(past)[:11]
def R2(past): return ranked(past)[11:]
def R3(past):
    prev = min(len(past), NT) - 1          # previous draw with tier data
    return R1(past) if Y[prev] > 0 else R2(past)

DEFS = {
 'R1': 'ticket = 11 most popular numbers; popularity = ridge (lambda=1, intercept, centred) of y=log((W8+W9+W10+.5)/(W3+W2+W1+.5)) on drawn indicators, past tier draws only',
 'R2': 'ticket = 11 least popular numbers (same popularity estimate); reverse hypothesis',
 'R3': 'if previous draw y>0 (more 8-10 than 1-3 winners) ticket = R1 (11 most popular) else R2 (11 least popular)',
}

if __name__ == '__main__':
    rules = []
    for name, f in (('R1', R1), ('R2', R2), ('R3', R3)):
        r = evaluate(f, name)
        r = {k: (float(v) if isinstance(v, (float, np.floating)) else int(v) if isinstance(v, (int, np.integer)) else v)
             for k, v in r.items()}
        r['definition'] = DEFS[name]
        rules.append(r)
        print(r)
    ticket = sorted(int(x) for x in R1(DRAWS))
    b = popularity(NT)
    # descriptive diagnostics (not part of the test)
    yc = Y - Y.mean()
    fit = (X - X.mean(0)) @ b
    r2 = 1 - ((yc - fit) ** 2).sum() / (yc ** 2).sum()
    print('ticket_25_11', ticket)
    print('beta (draws 0..409):', {n: round(float(b[n - 1]), 4) for n in range(1, 23)})
    print('y sd', float(Y.std()), 'in-sample R2', float(r2), 'last y', float(Y[-1]))
    json.dump({'id': 'A10', 'family': 'PLAYER POPULARITY', 'rules': rules, 'ticket_25_11': ticket,
               'popularity_beta_0_409': {str(n): float(b[n - 1]) for n in range(1, 23)}},
              open('/home/user/Mobil/tipos-all/lab/run_2511/agents/A10.json', 'w'), indent=1, ensure_ascii=False)
