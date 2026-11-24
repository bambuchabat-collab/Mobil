"""Pick 2 random-looking VAN tickets (11 of 22) with exactly 5 common numbers. Uses OS randomness."""
import secrets, json
from math import comb
R = secrets.SystemRandom()
U = set(range(1, 23))
PREV = [{1,5,6,7,10,12,13,16,17,18,21}, {2,9,12,13,15,16,17,18,19,20,22}]
def runs(t):
    s = sorted(t); best = cur = 1
    for a, b in zip(s, s[1:]):
        cur = cur + 1 if b == a + 1 else 1; best = max(best, cur)
    return best
def rows(t, w):  # max numbers in one row of a w-wide slip grid
    return max(sum(1 for x in t if (x - 1) // w == r) for r in range(22 // w + 1))
def ok(t):
    for x in (t, U - t):
        odd = sum(v % 2 for v in x); low = sum(v <= 11 for v in x)
        if not (4 <= odd <= 7 and 4 <= low <= 7): return False
        if runs(x) > 3: return False
        # no complete row of a 5..8-wide slip grid
        if any(set(range(r, min(r + w, 23))) <= x for w in (5, 6, 7, 8) for r in range(1, 23, w) if r + w - 1 <= 22): return False
        if any({v for v in range(r, 23, m)} <= x for m in (3, 4, 5) for r in range(1, m + 1)): return False
    return all(len(t & p) not in (0, 11) for p in PREV)
while True:
    a = set(R.sample(sorted(U), 11))
    if ok(a): break
while True:
    keep = set(R.sample(sorted(a), 5)); b = keep | set(R.sample(sorted(U - a), 6))
    if ok(b) and len(a & b) == 5: break
print(sorted(a), 'complement', sorted(U - a))
print(sorted(b), 'complement', sorted(U - b))
print('common', sorted(a & b))
json.dump({'draw': '2026-11-24 18:00 CET', 'game': 'Všetko alebo nič', 'tickets': [sorted(a), sorted(b)], 'common': sorted(a & b)},
          open('/home/user/Mobil/tipos-all/lab/run_2411/tickets_2411.json', 'w'))
