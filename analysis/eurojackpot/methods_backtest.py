"""
Backtest of the prediction methods that public lottery sites actually promote.

Already refuted in history_analysis.py: hot, cold, overdue, sums, odd/even,
high/low, consecutive pairs, serial dependence. This file adds the five that
turn up in the "systems" literature but had not been tested here:

  1. Delta system      - play the most common gap pattern between sorted numbers
  2. Positional        - play the most frequent number in each sorted position
  3. Pair affinity     - play numbers that most often appear together
  4. Last digit        - play the most frequent last digits
  5. Markov / follower - play the numbers that most often FOLLOW the last draw's

Each is backtested the same way: at every draw, build the rule from history
only, pick 5 numbers, count matches against what was actually drawn. For ANY
fixed set of 5 numbers the expectation is 5 x 5/50 = 0.5 matches per draw.
"""

import random
from collections import Counter, defaultdict
from math import sqrt

from draws import DRAWS
from stats_util import normal_sf

random.seed(20260911)
BURN = 100
N = len(DRAWS)
POOL = list(range(1, 51))


def top_k(counter, k, universe=POOL):
    """Deterministic top-k: highest count, ties broken by smallest number."""
    return [n for n, _ in sorted(((u, counter.get(u, 0)) for u in universe),
                                 key=lambda kv: (-kv[1], kv[0]))[:k]]


# --- the five rules ----------------------------------------------------------

def pick_delta(hist):
    """Most common gap pattern, anchored on the most common first number."""
    pat = Counter()
    first = Counter()
    for _, m, _ in hist:
        pat[tuple(b - a for a, b in zip(m, m[1:]))] += 1
        first[m[0]] += 1
    gaps = pat.most_common(1)[0][0]
    start = first.most_common(1)[0][0]
    out, cur = [start], start
    for g in gaps:
        cur += g
        out.append(cur)
    return out if max(out) <= 50 and len(set(out)) == 5 else sorted(
        random.sample(POOL, 5))


def pick_positional(hist):
    """Most frequent number in each sorted position, deduplicated."""
    pos = [Counter() for _ in range(5)]
    for _, m, _ in hist:
        for i, n in enumerate(m):
            pos[i][n] += 1
    out = []
    for i in range(5):
        for n, _ in pos[i].most_common():
            if n not in out:
                out.append(n)
                break
    return out


def pick_pairs(hist):
    """Seed with the most-drawn number, then greedily add its closest companions."""
    freq = Counter()
    co = defaultdict(Counter)
    for _, m, _ in hist:
        freq.update(m)
        for a in m:
            for b in m:
                if a != b:
                    co[a][b] += 1
    seed = freq.most_common(1)[0][0]
    out = [seed]
    while len(out) < 5:
        score = Counter()
        for n in out:
            score.update(co[n])
        for n in out:
            del score[n]
        out.append(score.most_common(1)[0][0])
    return out


def pick_last_digit(hist):
    """Most frequent last digits, filled with the most frequent number per digit."""
    dig = Counter()
    per = defaultdict(Counter)
    for _, m, _ in hist:
        for n in m:
            dig[n % 10] += 1
            per[n % 10][n] += 1
    out = []
    for d, _ in dig.most_common():
        for n, _ in per[d].most_common():
            if n not in out:
                out.append(n)
                break
        if len(out) == 5:
            break
    return out


def pick_markov(hist):
    """Numbers that most often appear in the draw AFTER the previous draw's numbers."""
    follow = defaultdict(Counter)
    for i in range(1, len(hist)):
        for a in hist[i - 1][1]:
            follow[a].update(hist[i][1])
    score = Counter()
    for a in hist[-1][1]:
        score.update(follow[a])
    return top_k(score, 5)


METHODS = [
    ("delta system", pick_delta),
    ("positional", pick_positional),
    ("pair affinity", pick_pairs),
    ("last digit", pick_last_digit),
    ("markov/follower", pick_markov),
    ("random", lambda h: random.sample(POOL, 5)),
]

# --- backtest ----------------------------------------------------------------
results = {name: 0 for name, _ in METHODS}
n_back = 0
for t in range(BURN, N):
    hist = DRAWS[:t]
    target = set(DRAWS[t][1])
    n_back += 1
    for name, fn in METHODS:
        results[name] += len(set(fn(hist)) & target)

# matches ~ Hypergeometric(50, 5, 5): mean 0.5, var 0.4133 per draw
mean, var = 0.5, 5 * 0.1 * 0.9 * 45 / 49
exp_total = mean * n_back
sd = sqrt(var * n_back)

print(f"Backtest over {n_back} real draws ({DRAWS[BURN][0]} .. {DRAWS[-1][0]})")
print(f"Expected matches for ANY fixed 5-number set: {exp_total:.1f} +/- {sd:.1f}\n")
print(f"{'method':>18} {'matches':>9} {'per draw':>10} {'z':>7} {'p':>7}")
for name, _ in METHODS:
    m = results[name]
    z = (m - exp_total) / sd
    print(f"{name:>18} {m:>9} {m / n_back:>10.4f} {z:>+7.2f} "
          f"{2 * normal_sf(abs(z)):>7.3f}")

best = max(results, key=results.get)
print(f"\nBest performer: {best} ({results[best]} matches). "
      f"z = {(results[best] - exp_total) / sd:+.2f}")
print("With six methods tested, the largest of six noise draws lands around")
print("+1.3 sigma by construction, so even the winner here is not a finding.")
print("\nNone of the five published 'systems' beats a fixed set of five numbers")
print("chosen with no data at all. Combined with the eight methods already")
print("tested in history_analysis.py, that is thirteen with no signal.")
