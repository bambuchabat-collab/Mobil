"""A6 CROSS-GAME SIGNALS: VAN ticket from recency in Extra vyplata (EV) and Loto 5 z 35 (L535).
Pre-registered in A6_prereg.md. Run: python3 -I A6.py"""
import json, os, sys
import numpy as np
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2511')
from harness import evaluate, DRAWS

HERE = os.path.dirname(os.path.abspath(__file__))
EV = sorted(json.load(open(os.path.join(HERE, 'A6_ev.json'))), key=lambda x: x['date'])
L535 = sorted(json.load(open(os.path.join(HERE, 'A6_l535.json'))), key=lambda x: x['date'])
WINDOW, CNT_N, NEVER = 60, 10, 10 ** 6

def target_date(past):
    """Date of the VAN draw being predicted. Rules only receive `past`; the date of the next draw is
    known in advance (daily game), so it is taken from the schedule, never its numbers."""
    t = len(past)
    return DRAWS[t]['date'] if t < len(DRAWS) else '2026-11-25'

def ranked(seq_newest_first, t):
    sets = [set(x for x in d['main'] if x <= 22) for d in seq_newest_first[:WINDOW]]
    age = {x: next((j for j, s in enumerate(sets) if x in s), NEVER) for x in range(1, 23)}
    cnt = {x: sum(x in s for s in sets[:CNT_N]) for x in range(1, 23)}
    perm = np.random.default_rng([2511, 6, t]).permutation(np.arange(1, 23))
    u = {int(x): i for i, x in enumerate(perm)}
    return sorted(range(1, 23), key=lambda x: (age[x], -cnt[x], u[x]))

def ev_before(D):
    return [d for d in EV if d['date'] < D][::-1]

def merged_before(D):
    seq = [(d['date'], 0, d) for d in EV if d['date'] < D] + [(d['date'], 1, d) for d in L535 if d['date'] < D]
    seq.sort(key=lambda z: (z[0], -z[1]))          # same date: EV placed after L535 in ascending -> first when reversed
    return [z[2] for z in seq][::-1]

def R1(past):
    return ranked(ev_before(target_date(past)), len(past))[:11]

def R2(past):
    return ranked(ev_before(target_date(past)), len(past))[11:]

def R3(past):
    return ranked(merged_before(target_date(past)), len(past))[:11]

DEFS = {
    'R1': 'EV-hot-avoid (PRIMARY): 11 numbers of 1..22 most recently drawn in EV (date < VAN date); ties by count in last 10 EV draws, then seeded permutation',
    'R2': 'EV-hot-repeat: complement of R1 (11 numbers least recently drawn in EV)',
    'R3': 'EV+L535-hot-avoid: 11 numbers of 1..22 most recently drawn in EV or Loto 5 z 35 (merged by date, date < VAN date); same tie-breaks',
}

def plain(v):
    if isinstance(v, (np.integer,)): return int(v)
    if isinstance(v, (np.floating,)): return float(v)
    return v

if __name__ == '__main__':
    # sanity: no other-game draw on/after the VAN date is used; coverage of evaluated window
    for t in (30, 411):
        D = DRAWS[t]['date']
        assert all(d['date'] < D for d in ev_before(D)) and all(d['date'] < D for d in merged_before(D))
    gaps = [(DRAWS[t]['date'], ev_before(DRAWS[t]['date'])[0]['date']) for t in range(30, len(DRAWS))]
    print('EV lag (VAN date, latest EV used) first/last:', gaps[0], gaps[-1])
    rules = []
    for name, f in (('R1', R1), ('R2', R2), ('R3', R3)):
        r = {k: plain(v) for k, v in evaluate(f, name).items()}
        r['definition'] = DEFS[name]
        rules.append(r)
        print(r)
    ticket = sorted(int(x) for x in R1(DRAWS))
    tR3 = sorted(int(x) for x in R3(DRAWS))
    print('ticket_25_11 (R1):', ticket, ' R3 would give:', tR3)
    json.dump({'id': 'A6', 'family': 'CROSS-GAME SIGNALS', 'rules': rules, 'ticket_25_11': ticket,
               'ticket_25_11_R2': sorted(int(x) for x in R2(DRAWS)), 'ticket_25_11_R3': tR3,
               'data': {'ev_draws': len(EV), 'ev_last': EV[-1]['date'], 'l535_draws': len(L535), 'l535_last': L535[-1]['date']}},
              open(os.path.join(HERE, 'A6.json'), 'w'), indent=1)
