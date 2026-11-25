"""A5: calendar and date numerology anti-hit rules (pre-registered in agents/A5_prereg.md).
Run: python3 -I /home/user/Mobil/tipos-all/lab/run_2511/agents/A5.py
"""
import sys, json, datetime as dt
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2511')
import numpy as np
from harness import evaluate, DRAWS

SEED = 20261125
FINAL_DATE = '2026-11-25'
SYN = 29.530588853
JD_NEW = 2451550.2597


def target_date(past):
    """Calendar date of the draw being predicted (date field only)."""
    t = len(past)
    return dt.date.fromisoformat(DRAWS[t]['date'] if t < len(DRAWS) else FINAL_DATE)


def priority(r, t):
    perm = np.random.default_rng([SEED, r, t]).permutation(22) + 1
    return {int(n): i for i, n in enumerate(perm)}


def pick(key, r, t, largest=False):
    pr = priority(r, t)
    sgn = -1 if largest else 1
    return sorted(range(1, 23), key=lambda n: (sgn * key[n], pr[n]))[:11]


def counts(draws):
    f = {n: 0 for n in range(1, 23)}
    for d in draws:
        for n in d['main']:
            f[int(n)] += 1
    return f


def wrap(x):
    return ((x - 1) % 22) + 1


def anchors(D):
    ds = sum(int(c) for c in D.strftime('%d%m%Y'))
    return sorted({wrap(D.day), D.month, wrap(ds), sum(int(c) for c in str(D.day)), D.isoweekday()})


def lunar_bucket(D):
    jd = D.toordinal() + 1721424.5 + 17 / 24
    age = (jd - JD_NEW) % SYN
    return int(np.floor(age / SYN * 4 + 0.5)) % 4


def R1(past):
    D = target_date(past)
    w = D.weekday()
    f = counts([d for d in past if dt.date.fromisoformat(d['date']).weekday() == w])
    return pick(f, 1, len(past))


def R2(past):
    D = target_date(past)
    A = anchors(D)
    key = {n: min(min(abs(n - a), 22 - abs(n - a)) for a in A) for n in range(1, 23)}
    return pick(key, 2, len(past), largest=True)


def R3(past):
    D = target_date(past)
    b = lunar_bucket(D)
    f = counts([d for d in past if lunar_bucket(dt.date.fromisoformat(d['date'])) == b])
    return pick(f, 3, len(past))


DEFS = {
    'R1': 'Same-weekday cold: 11 numbers least often drawn in past draws on the target weekday; ties by rng([SEED,1,t]).',
    'R2': 'Date anchors A={day wrap22, month, digit sum DDMMYYYY wrap22, digit sum of day, ISO weekday}; '
          '11 numbers farthest (circular distance on 1..22) from nearest anchor; ties by rng([SEED,2,t]).',
    'R3': 'Lunar 4-bucket cold: 11 numbers least often drawn in past draws in the same mean-lunar-phase quarter '
          '(new/first/full/last, centred) at 17:00 UTC; ties by rng([SEED,3,t]).',
}


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
    out = {'id': 'A5', 'family': 'CALENDAR AND DATE NUMEROLOGY', 'seed': SEED, 'rules': []}
    for name, rule in (('R1', R1), ('R2', R2), ('R3', R3)):
        res = evaluate(rule, name)
        res['definition'] = DEFS[name]
        res['ticket_25_11'] = sorted(int(x) for x in rule(DRAWS))
        out['rules'].append(plain(res))
        print(res)
    D = dt.date.fromisoformat(FINAL_DATE)
    out['final_date_info'] = {'date': FINAL_DATE, 'weekday': D.strftime('%A'), 'anchors': anchors(D),
                              'lunar_bucket': lunar_bucket(D)}
    out['ticket_25_11'] = sorted(int(x) for x in R1(DRAWS))
    print('final', out['final_date_info'], 'ticket R1', out['ticket_25_11'])
    json.dump(plain(out), open('/home/user/Mobil/tipos-all/lab/run_2511/agents/A5.json', 'w'), indent=1,
              ensure_ascii=False)
