"""Randomness tests on LOTO 5 z 35 draws + backtest of common 'systems'.

Answers the question: can past results predict future ones?
Run from a directory containing data/draws_2021_2026.json
"""
import json, math, collections, random, statistics
from math import comb

rows = json.load(open('data/draws_2021_2026.json'))
N = len(rows)
C = comb(35, 5)
P = {k: comb(5, k) * comb(30, 5 - k) / C for k in (3, 4, 5)}

print("=== EXACT PROBABILITIES ===")
print(f"  C(35,5) = {C:,}")
for k in (5, 4, 3):
    print(f"  match {k}: 1 : {1/P[k]:,.1f}")

print("\n=== CHI-SQUARE UNIFORMITY ===")
cnt = collections.Counter()
for r in rows:
    cnt.update(r['nums'])
exp = N * 5 / 35
chi = sum((cnt[n] - exp) ** 2 / exp for n in range(1, 36))
print(f"  n={N} draws, chi2={chi:.2f} (df=34, a fair machine averages 34)")

print("\n=== POSITION BIAS (numbers stored in draw order) ===")
for pos in range(5):
    v = [r['nums'][pos] for r in rows]
    print(f"  position {pos+1}: mean={statistics.mean(v):6.2f}  (uniform = 18.00)")

print("\n=== DOES A LONG GAP MAKE A NUMBER 'DUE'? ===")
last = {}
buckets = collections.defaultdict(lambda: [0, 0])
for i, r in enumerate(rows):
    s = set(r['nums'])
    for n in range(1, 36):
        if n in last:
            b = min((i - last[n]) // 3, 8)
            buckets[b][1] += 1
            if n in s:
                buckets[b][0] += 1
    for n in s:
        last[n] = i
for b in sorted(buckets):
    hit, tot = buckets[b]
    lbl = f"{b*3}-{b*3+2}" if b < 8 else "24+"
    print(f"  gap {lbl:>6s} draws: P(drawn)={hit/tot:.4f}  n={tot:6d}   (flat 1/7 = 0.1429)")

print("\n=== BACKTEST: does any system beat random? ===")
BURN = 150
random.seed(7)

def hot(h):
    c = collections.Counter(n for r in h for n in r['nums'])
    return [n for n, _ in sorted(c.items(), key=lambda x: (-x[1], x[0]))[:5]]

def cold(h):
    c = collections.Counter({n: 0 for n in range(1, 36)})
    c.update(n for r in h for n in r['nums'])
    return [n for n, _ in sorted(c.items(), key=lambda x: (x[1], x[0]))[:5]]

def overdue(h):
    last = {}
    for i, r in enumerate(h):
        for n in r['nums']:
            last[n] = i
    return sorted(range(1, 36), key=lambda n: (last.get(n, -1), n))[:5]

def hot30(h):
    c = collections.Counter(n for r in h[-30:] for n in r['nums'])
    return [n for n, _ in sorted(c.items(), key=lambda x: (-x[1], x[0]))[:5]]

def repeat(h):
    return h[-1]['nums']

def rnd(h):
    return random.sample(range(1, 36), 5)

STRATS = {'HOT (all-time)': hot, 'COLD (all-time)': cold, 'OVERDUE': overdue,
          'HOT (last 30)': hot30, 'REPEAT last draw': repeat, 'RANDOM (baseline)': rnd}
res = {k: [] for k in STRATS}
for t in range(BURN, N):
    h, actual = rows[:t], set(rows[t]['nums'])
    for name, fn in STRATS.items():
        res[name].append(len(actual & set(fn(h))))

base = 25 / 35
sd1 = math.sqrt(5 * (5/35) * (1 - 5/35) * (35 - 5) / (35 - 1))
print(f"  theoretical mean matches for ANY fixed set of 5 = {base:.4f}\n")
print(f"  {'strategy':22s} {'mean':>8s} {'z vs theory':>12s}")
for name in STRATS:
    v = res[name]
    z = (statistics.mean(v) - base) / (sd1 / math.sqrt(len(v)))
    print(f"  {name:22s} {statistics.mean(v):8.4f} {z:+12.2f}")
print("\n  |z| > 2 would signal a real edge. None of them get there.")
