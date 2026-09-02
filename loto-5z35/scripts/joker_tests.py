"""JOKER: is the 6-digit number really random, and is it worth buying?"""
import json, math, collections
import numpy as np

rows = [r for r in json.load(open('data/draws_2021_2026.json'))
        if r['joker'] and len(r['joker']) == 6]
print(f"=== JOKER RNG UNIFORMITY  ({len(rows)} draws) ===")
for pos in range(6):
    c = collections.Counter(r['joker'][pos] for r in rows)
    exp = len(rows) / 10
    chi = sum((c.get(str(d), 0) - exp) ** 2 / exp for d in range(10))
    print(f"  digit position {pos+1}: chi2={chi:6.2f}  (df=9, crit@5% = 16.92)")

last2 = [r['joker'][-2:] for r in rows]
c2 = collections.Counter(last2)
exp2 = len(last2) / 100
chi2v = sum((c2.get(f'{i:02d}', 0) - exp2) ** 2 / exp2 for i in range(100))
print(f"  last-2 block: chi2={chi2v:.1f} (df=99, expected 99)")

print("\n=== ARE PLAYERS' JOKER NUMBERS RNG-ASSIGNED? ===")
recs = [(r['joker'], r['dep_joker'] / 0.50, r['jw2'])
        for r in rows if r.get('dep_joker') and r.get('jw2')]
y = np.array([math.log(w / (tk * 0.009)) for _, tk, w in recs])
n = len(y)
feats = {
    'repdigit (00,11,...)': lambda e: 1.0 if e[0] == e[1] else 0.0,
    'ends in 0':            lambda e: 1.0 if e[1] == '0' else 0.0,
    'ends in 7':            lambda e: 1.0 if e[1] == '7' else 0.0,
    'contains 7':           lambda e: 1.0 if '7' in e else 0.0,
    'ascending (12,23,...)': lambda e: 1.0 if int(e[1]) - int(e[0]) == 1 else 0.0,
}
for nm, fn in feats.items():
    x = np.array([fn(jk[-2:]) for jk, _, _ in recs])
    if x.std() == 0:
        continue
    c = np.corrcoef(x, y)[0, 1]
    t = c * math.sqrt((n - 2) / (1 - c * c))
    print(f"  {nm:22s} r={c:+.3f}  t={t:+6.2f}  "
          f"{'<- worth noting' if abs(t) > 2.5 else 'no effect (RNG)'}")

print("\n=== JOKER EXPECTED VALUE ===")
JP = rows[-1]['jackpot_joker'] or 325664.40
tickets = (rows[-1]['dep_joker'] or 55194) / 0.50
lam = tickets * 1e-6
share = (1 - math.exp(-lam)) / lam
fixed = 0.009 * 3.30 + 0.0009 * 33 + 0.00009 * 330 + 0.000009 * 3300
ev = fixed + 1e-6 * JP * share
print(f"  jackpot {JP:,.2f} EUR | ~{tickets:,.0f} joker tickets | share if hit {share:.3f}")
print(f"  fixed tiers {fixed:.4f} EUR + jackpot {1e-6*JP*share:.4f} EUR = {ev:.4f} EUR")
print(f"  return at 0.50 EUR: {ev/0.50*100:.1f}%")
