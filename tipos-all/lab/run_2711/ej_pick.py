"""Experimental Eurojackpot ticket for 27.11.2026 (5 of 50 + 2 of 12), OS randomness, popularity-aware filters.
Filters: >=3 numbers above 31 (players over-pick birthdays 1-31), no 3 consecutive, no 3-term arithmetic progression,
not all in one decade. Odds computed exactly."""
import secrets, json, datetime
from math import comb
R = secrets.SystemRandom()
def ok(m):
    s = sorted(m)
    if sum(x > 31 for x in s) < 3: return False
    if any(s[i] + 2 == s[i + 1] + 1 == s[i + 2] for i in range(3)): return False
    if any(b - a == c - b for i, a in enumerate(s) for j, b in enumerate(s[i+1:], i+1) for c in s[j+1:]): return False
    return len({(x - 1) // 10 for x in s}) >= 3
while True:
    m = sorted(R.sample(range(1, 51), 5))
    if ok(m): break
e = sorted(R.sample(range(1, 13), 2))
N5, N2 = comb(50, 5), comb(12, 2)
def p(k, j): return comb(5, k) * comb(45, 5 - k) / N5 * comb(2, j) * comb(10, 2 - j) / N2
T = [(5,2),(5,1),(5,0),(4,2),(4,1),(4,0),(3,2),(2,2),(3,1),(3,0),(1,2),(2,1)]
pany = sum(p(*t) for t in T)
out = {'made_utc': datetime.datetime.utcnow().isoformat(timespec='seconds') + 'Z', 'draw': '2026-11-27 20:00 CET',
       'main': m, 'euro': e, 'p_any': pany, 'p_any_one_in': 1 / pany, 'p_jackpot_one_in': 1 / p(5, 2),
       'note': 'experiment only: acceptance closed at 17:45 CET'}
json.dump(out, open('ej_ticket_2711.json', 'w'), indent=1); print(out)
