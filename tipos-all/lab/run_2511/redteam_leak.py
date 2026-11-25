"""Red team, part 2: LEAKAGE + reproduction test of all 30 rules (python3 -I -B, numpy, fixed seeds).
Clean pass: re-run every rule through harness.evaluate, record the ticket for every t, compare the stats with
agents/A*.json and the 25.11 ticket with ticket_25_11.
Poison pass (dynamic leakage test): for each t, overwrite IN PLACE every module-level data source with random
numbers from draw t on (harness.DRAWS[t:] main/order -> random draws, dates kept because the draw date is public;
A6: EV / Loto 5z35 draws dated >= date(t) -> random numbers; A10: tier-data rows >= t -> random), call the rule on
DRAWS[:t] again (fresh model for A4) and compare. Any change = the rule reads data it must not see.
Positive controls: a rule that reads DRAWS[t] and a rule that uses same-day EV must be flagged.
Writes redteam_leak.json and redteam_tickets.json (clean per-draw tickets of all 30 rules)."""
import sys, os, json, re, time, importlib.util
sys.dont_write_bytecode = True
RUN = '/home/user/Mobil/tipos-all/lab/run_2511'
sys.path.insert(0, RUN)
import numpy as np
import harness
from harness import evaluate, DRAWS

AG = os.path.join(RUN, 'agents')
SNAP = json.dumps(DRAWS, sort_keys=True)
ORIG = list(DRAWS)
N0, ND = 30, len(DRAWS)


def load(name):
    spec = importlib.util.spec_from_file_location('rt_' + name, os.path.join(AG, name + '.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def load_a8():
    src = open(os.path.join(AG, 'A8.py')).read()
    cut = src.index('\nrules = []\n')           # everything after this evaluates and writes A8.json -> not executed
    ns = {'__name__': 'rt_A8', '__file__': os.path.join(AG, 'A8.py')}
    exec(compile(src[:cut], 'A8.py', 'exec'), ns)
    return type('M', (), ns)


t0 = time.time()
M = {a: load(a) for a in ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A9', 'A10']}
M['A8'] = load_a8()
print('modules loaded', round(time.time() - t0, 1), flush=True)

# (agent, rule name as in json, factory returning a fresh callable)
RULES = []
for a, names in [('A1', [('R1', 'r1_late_ball'), ('R2', 'r2_early_recent'), ('R3', 'r3_transition')]),
                 ('A2', [('R1', 'rule_r1'), ('R2', 'rule_r2'), ('R3', 'rule_r3')]),
                 ('A3', [('A3_R1', 'r1'), ('A3_R2', 'r2'), ('A3_R3', 'r3')]),
                 ('A5', [('R1', 'R1'), ('R2', 'R2'), ('R3', 'R3')]),
                 ('A6', [('R1', 'R1'), ('R2', 'R2'), ('R3', 'R3')]),
                 ('A7', [('R1', 'R1'), ('R2', 'R2'), ('R3', 'R3')]),
                 ('A8', [('R1', 'R1'), ('R2', 'R2'), ('R3', 'R3')]),
                 ('A9', [('A9_R1_dirmult_halflife30', 'rule_r1'), ('A9_R2_bocpd_h50_beta11', 'rule_r2'),
                         ('A9_R3_plackett_luce_map_s0.1', 'rule_r3')]),
                 ('A10', [('R1', 'R1'), ('R2', 'R2'), ('R3', 'R3')])]:
    for rn, fn in names:
        f = getattr(M[a], fn)
        RULES.append((a, rn, (lambda f=f: f)))
for k in ('R1', 'R2', 'R3'):
    RULES.append(('A4', k, (lambda k=k: M['A4'].make_rule(k))))
RULES.sort(key=lambda r: (int(r[0][1:]), r[1]))

# positive controls
def ctrl_peek(past):
    return sorted(set(range(1, 23)) - set(harness.DRAWS[len(past)]['main']))
def ctrl_sameday_ev(past):
    D = M['A6'].target_date(past)
    seq = [d for d in M['A6'].EV if d['date'] <= D][::-1]   # WRONG on purpose: includes same-day EV
    return M['A6'].ranked(seq, len(past))[:11]
CONTROLS = [('CTRL', 'peek_DRAWS[t]', lambda: ctrl_peek), ('CTRL', 'same_day_EV', lambda: ctrl_sameday_ev)]

REPORTED = {}
for f in sorted(os.listdir(AG)):
    if re.fullmatch(r'A\d+\.json', f):
        j = json.load(open(os.path.join(AG, f)))
        for r in j['rules']:
            REPORTED[(j['id'], r['rule'])] = r
        REPORTED[(j['id'], 'ticket')] = j['ticket_25_11']

# ---------------- poisoning helpers ----------------
EV0, L0 = list(M['A6'].EV), list(M['A6'].L535)
X10, Y10 = M['A10'].X.copy(), M['A10'].Y.copy()


def rand_draw(rng, d):
    o = (rng.permutation(22) + 1)[:11].tolist()
    return {'date': d['date'], 'day': d['day'], 'main': sorted(o), 'order': o}


def poison(t, rng):
    DRAWS[t:] = [rand_draw(rng, d) for d in ORIG[t:]]
    D = ORIG[t]['date']
    M['A6'].EV = [d if d['date'] < D else {**d, 'main': sorted((rng.permutation(27) + 1)[:6].tolist())} for d in EV0]
    M['A6'].L535 = [d if d['date'] < D else {**d, 'main': sorted((rng.permutation(35) + 1)[:5].tolist())} for d in L0]
    if t < len(Y10):
        Xp, Yp = X10.copy(), Y10.copy()
        Xp[t:] = 0
        for s in range(t, len(Yp)):
            Xp[s, rng.permutation(22)[:11]] = 1
        Yp[t:] = rng.normal(0, 3, len(Yp) - t)
        M['A10'].X[:] = Xp; M['A10'].Y[:] = Yp
    M['A10']._cache.clear()


def restore():
    DRAWS[:] = ORIG
    M['A6'].EV, M['A6'].L535 = EV0, L0
    M['A10'].X[:] = X10; M['A10'].Y[:] = Y10; M['A10']._cache.clear()


rng_t = np.random.default_rng(99)
T_ALL = list(range(N0, ND))
T_A4 = sorted(set([30, 31, 39, 40, 41, 99, 100, 209, 210, 211, 399, 400, 409, 410, 411] +
                  rng_t.choice(T_ALL, 15, replace=False).tolist()))
OUT = {'rules': [], 'controls': []}
TICKETS = {}
for a, rn, fac in RULES + CONTROLS:
    t1 = time.time()
    rec = {}
    f = fac()
    def wrap(past, f=f):
        T = f(past); rec[len(past)] = sorted(int(x) for x in T); return T
    res = evaluate(wrap, rn)
    row = {'agent': a, 'rule': rn, 'mean_hits': float(res['mean_hits']), 'p_mean_lower': float(res['p_mean_lower']),
           'p_le3': float(res['p_le3']), 'n_zero': int(res['n_zero']), 'won_eur': int(res['won_eur'])}
    if a != 'CTRL':
        rep = REPORTED[(a, rn)]
        row['reproduced'] = (abs(rep['mean_hits'] - row['mean_hits']) < 1e-12 and
                             abs(rep['p_mean_lower'] - row['p_mean_lower']) < 1e-12 and
                             abs(rep['p_le3'] - row['p_le3']) < 1e-12 and rep['n_zero'] == row['n_zero'] and
                             rep['won_eur'] == row['won_eur'])
    assert json.dumps(DRAWS, sort_keys=True) == SNAP, 'DRAWS mutated by ' + a + rn
    ts = T_A4 if a == 'A4' else T_ALL
    rng = np.random.default_rng([2511, int(a[1:]) if a != 'CTRL' else 0, len(OUT['rules']) + len(OUT['controls'])])
    diff = []
    for t in ts:
        poison(t, rng)
        try:
            g = fac() if a == 'A4' else f
            T = sorted(int(x) for x in g(DRAWS[:t]))
        finally:
            restore()
        if T != rec[t]:
            diff.append(t)
    assert json.dumps(DRAWS, sort_keys=True) == SNAP
    row.update({'poison_t_tested': len(ts), 'poison_changed_ticket': len(diff), 'changed_at_t': diff[:10],
                'leak': bool(diff), 'seconds': round(time.time() - t1, 1)})
    (OUT['controls'] if a == 'CTRL' else OUT['rules']).append(row)
    if a != 'CTRL':
        TICKETS[f'{a}:{rn}'] = [rec[t] for t in T_ALL]
    print(row, flush=True)

# 25.11 tickets reproduce?
tk = {}
for a in ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10']:
    prim = [r for r in RULES if r[0] == a][0]
    T = sorted(int(x) for x in prim[2]()(DRAWS))
    tk[a] = {'recomputed': T, 'reported': sorted(REPORTED[(a, 'ticket')]), 'match': T == sorted(REPORTED[(a, 'ticket')])}
OUT['tickets_25_11'] = tk

# static scan: every place an agent touches module-level DRAWS or opens a file
static = {}
for a in ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10']:
    lines = open(os.path.join(AG, a + '.py')).read().splitlines()
    static[a] = [f'{i + 1}: {l.strip()}' for i, l in enumerate(lines)
                 if re.search(r'DRAWS\[|open\(|json\.load', l) and 'import' not in l]
OUT['static_scan'] = static
OUT['controls_flagged'] = all(c['leak'] for c in OUT['controls'])
OUT['any_leak'] = any(r['leak'] for r in OUT['rules'])
OUT['all_reproduced'] = all(r['reproduced'] for r in OUT['rules'])
json.dump(OUT, open(os.path.join(RUN, 'redteam_leak.json'), 'w'), indent=1)
json.dump({'t': T_ALL, 'tickets': TICKETS}, open(os.path.join(RUN, 'redteam_tickets.json'), 'w'))
print('controls flagged:', OUT['controls_flagged'], 'any leak:', OUT['any_leak'], 'all reproduced:', OUT['all_reproduced'])
print('tickets:', {a: v['match'] for a, v in tk.items()})
