"""Check two Extra výplata fields: constraints + exact odds. Usage: python3 -I check_ev_tickets.py "a b c d e f/x" "g h i j k l/y" """
import sys
from math import comb
from fractions import Fraction as F
def parse(s):
    m, e = s.split('/'); return sorted(int(v) for v in m.split()), int(e)
(A, ea), (B, eb) = parse(sys.argv[1]), parse(sys.argv[2])
for f, e in ((A, ea), (B, eb)):
    assert len(set(f)) == 6 and all(1 <= v <= 27 for v in f) and 1 <= e <= 7
    run3 = any(f[i] + 1 == f[i + 1] and f[i + 1] + 1 == f[i + 2] for i in range(4))
    ap = [(a, b, c) for i, a in enumerate(f) for j, b in enumerate(f[i+1:], i+1) for c in f[j+1:] if b - a == c - b]
    pairs = sum(1 for i in range(5) if f[i] + 1 == f[i + 1])
    print(f, '+', e, '| 3-run:', run3, '| equal-step triples:', ap, '| consecutive pairs:', pairs)
common = set(A) & set(B); print('common numbers:', sorted(common), '| extras differ:', ea != eb)
N = comb(27, 6); c = len(common)
# exact P(any prize on either) via enumeration over hits in A-only, B-only, common, rest
a_only, b_only, rest = 6 - c, 6 - c, 27 - 12 + c
anyp = F(0); top6 = F(0)
for x in range(c + 1):
  for y in range(a_only + 1):
    for z in range(b_only + 1):
      w = 6 - x - y - z
      if w < 0 or w > rest: continue
      k = comb(c, x) * comb(a_only, y) * comb(b_only, z) * comb(rest, w)
      ha, hb = x + y, x + z
      if ha >= 3 or hb >= 3: anyp += F(k, N)
      if ha == 6 or hb == 6: top6 += F(k, N)
# 6+1 on either: P(6 main on A)*P(extra=ea) + same for B (disjoint events if A!=B)
p61 = (F(1, N) * F(1, 7)) * (2 if A != B else 1)
print(f'P(any prize) = {float(anyp):.4%}  (1 in {float(1/anyp):.2f})')
print(f'P(6 main on either) = 1 in {float(1/top6):,.0f};  P(6+1 on either) = 1 in {float(1/p61):,.0f}')
