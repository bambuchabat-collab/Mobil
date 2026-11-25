"""A9 — Bayesian ball-propensity models (pre-registered in A9_prereg.md).
R1 Dirichlet-multinomial with exponential forgetting (half-life 30), R2 BOCPD (hazard 1/50, Beta(1,1)) per number,
R3 Plackett-Luce MAP on draw order (Gaussian prior s = 0.1). Ticket = 11 lowest posterior predictive propensities.
Run: python3 -I A9.py
"""
import sys, json
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2511')
import numpy as np
from harness import evaluate, DRAWS

np.random.seed(0)                      # no randomness used; fixed for completeness
N = 22
HALF_LIFE = 30.0
ALPHA0 = 1.0
HAZARD = 1.0 / 50.0
BETA_A, BETA_B = 1.0, 1.0
PL_S = 0.1


def lowest11(score):
    """11 numbers with lowest score; ties -> smaller number first (stable sort on index order)."""
    idx = np.argsort(np.asarray(score, float), kind='stable')[:11]
    return sorted(int(i) + 1 for i in idx)


def indicator(past):
    X = np.zeros((len(past), N))
    for d, dr in enumerate(past):
        X[d, np.array(dr['main']) - 1] = 1.0
    return X


# ---------------- R1: Dirichlet-multinomial with exponential forgetting ----------------
def r1_propensity(past):
    X = indicator(past)
    t = len(past)
    w = 0.5 ** ((t - 1 - np.arange(t)) / HALF_LIFE)
    c = w @ X
    return (ALPHA0 + c) / (N * ALPHA0 + c.sum())


def rule_r1(past):
    return lowest11(r1_propensity(past))


# ---------------- R2: BOCPD per number (vectorised over the 22 numbers) ----------------
def r2_predictive(past):
    X = indicator(past)                      # (t, 22)
    R = np.ones((N, 1))                      # run-length posterior, r = 0 only
    s = np.zeros((N, 1))                     # ones in run
    n = np.zeros((N, 1))                     # length of run
    for x in X:
        x = x[:, None]
        p1 = (BETA_A + s) / (BETA_A + BETA_B + n)
        pred = np.where(x == 1.0, p1, 1.0 - p1)
        joint = R * pred
        growth = joint * (1.0 - HAZARD)
        cp = (joint * HAZARD).sum(axis=1, keepdims=True)
        R = np.hstack([cp, growth])
        R /= R.sum(axis=1, keepdims=True)
        s = np.hstack([np.zeros((N, 1)), s + x])
        n = np.hstack([np.zeros((N, 1)), n + 1.0])
    p1 = (BETA_A + s) / (BETA_A + BETA_B + n)
    return (R * p1).sum(axis=1)


def rule_r2(past):
    return lowest11(r2_predictive(past))


# ---------------- R3: Plackett-Luce MAP on draw order ----------------
def pl_stages(past):
    """Stage masks (11*t, 22): balls still in the drum; chosen counts per ball."""
    masks = np.zeros((11 * len(past), N))
    chosen = np.zeros(N)
    row = 0
    for dr in past:
        rem = np.ones(N)
        for b in dr['order']:
            masks[row] = rem
            rem[b - 1] = 0.0
            chosen[b - 1] += 1.0
            row += 1
    return masks, chosen


def r3_theta(past):
    M, chosen = pl_stages(past)
    th = np.zeros(N)
    prec = 1.0 / PL_S ** 2
    for _ in range(100):
        E = M * np.exp(th - th.max())
        P = E / E.sum(axis=1, keepdims=True)
        grad = chosen - P.sum(axis=0) - prec * th
        if np.abs(grad).max() < 1e-10:
            break
        H = -(np.diag(P.sum(axis=0)) - P.T @ P) - prec * np.eye(N)
        th = th - np.linalg.solve(H, grad)
    return th


def rule_r3(past):
    return lowest11(r3_theta(past))


DEFS = {
    'A9_R1_dirmult_halflife30': 'Dirichlet(alpha0=1) propensity with exponential forgetting w=0.5**(age/30), age 0 = newest past draw; ticket = 11 lowest (alpha0+c_i)/(22*alpha0+sum c); ties -> smaller number.',
    'A9_R2_bocpd_h50_beta11': 'Per-number Bernoulli BOCPD (Adams-MacKay), constant hazard 1/50, Beta(1,1) segment prior, exact (untruncated) run-length recursion; ticket = 11 lowest posterior predictive P(drawn next).',
    'A9_R3_plackett_luce_map_s0.1': 'Plackett-Luce on full draw order (11 sequential picks from 22), MAP with theta_i~N(0,0.1^2), Newton to |grad|<1e-10, all past draws equal weight; ticket = 11 lowest theta_i (= lowest plug-in inclusion prob).',
}
RULES = [('A9_R1_dirmult_halflife30', rule_r1), ('A9_R2_bocpd_h50_beta11', rule_r2),
         ('A9_R3_plackett_luce_map_s0.1', rule_r3)]


def plain(o):
    if isinstance(o, dict):
        return {k: plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [plain(v) for v in o]
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    return o


if __name__ == '__main__':
    out = {'id': 'A9', 'family': 'BAYESIAN BALL-PROPENSITY MODELS', 'rules': []}
    for name, fn in RULES:
        res = evaluate(fn, name)
        res['definition'] = DEFS[name]
        out['rules'].append(plain(res))
        print(json.dumps(plain(res)))
    out['ticket_25_11'] = rule_r1(DRAWS)
    out['tickets_25_11_secondary'] = {'R2': rule_r2(DRAWS), 'R3': rule_r3(DRAWS)}
    print('ticket R1 25.11:', out['ticket_25_11'], 'R2:', out['tickets_25_11_secondary']['R2'],
          'R3:', out['tickets_25_11_secondary']['R3'])
    with open('/home/user/Mobil/tipos-all/lab/run_2511/agents/A9.json', 'w') as f:
        json.dump(plain(out), f, indent=1)
