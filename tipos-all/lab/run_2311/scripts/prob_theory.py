"""Probability-theory derivation for 2 bets on 23.11.2026 (exact, fractions).
EV = Extra výplata (6 of 27 + extra 1..7), VAN = Všetko alebo nič (11 of 22).
Usage: python3 -I prob_theory.py data/ev.json
"""
import json, sys, math, statistics as st
from math import comb
from fractions import Fraction as F

# ---------- 1. Hypergeometric law for one EV field ----------
N = comb(27, 6)
def hyp(k): return F(comb(6, k) * comb(21, 6 - k), N)       # P(k of my 6 among 6 drawn)
print('1) EV one field, hypergeometric P(k hits):')
for k in range(7): print(f'   k={k}: {float(hyp(k)):.6%}  (1 in {float(1/hyp(k)):,.1f})')
p1 = sum(hyp(k) for k in (3, 4, 5, 6))
print(f'   P(any prize, k>=3) = {float(p1):.4%}   [extra number does not matter for "any prize": every tier needs >=3 main]')

# ---------- 2. Two fields: inclusion-exclusion P(A∪B)=P(A)+P(B)-P(A∩B) ----------
def two_fields(c):
    """c common numbers. Returns P(A), P(A∩B), P(A∪B) exactly by enumeration of the multivariate hypergeometric."""
    ao, bo, rest = 6 - c, 6 - c, 27 - 12 + c
    pA = pAB = F(0)
    for x in range(c + 1):
        for y in range(ao + 1):
            for z in range(bo + 1):
                w = 6 - x - y - z
                if w < 0 or w > rest: continue
                p = F(comb(c, x) * comb(ao, y) * comb(bo, z) * comb(rest, w), N)
                if x + y >= 3: pA += p
                if x + y >= 3 and x + z >= 3: pAB += p
    return pA, pAB, 2 * pA - pAB
print('\n2) EV two fields with c common numbers (inclusion-exclusion):')
for c in range(7):
    pA, pAB, pU = two_fields(c)
    print(f'   c={c}: P(A)=P(B)={float(pA):.4%}  P(A∩B)={float(pAB):.4%}  P(A∪B)={float(pU):.4%}')
print('   => P(A∪B) is maximal when P(A∩B) is minimal, i.e. c=0 (disjoint fields).')

# ---------- 3. VAN two tickets with s common numbers ----------
M = comb(22, 11); WIN = {0, 1, 2, 3, 8, 9, 10, 11}
def van_pair(s):
    r = 11 - s; pA = pAB = F(0)
    for x in range(s + 1):
        for y in range(r + 1):
            for z in range(r + 1):
                w = 11 - x - y - z
                if w < 0 or w > s: continue
                p = F(comb(s, x) * comb(r, y) * comb(r, z) * comb(s, w), M)
                if x + y in WIN: pA += p
                if x + y in WIN and x + z in WIN: pAB += p
    return pA, pAB, 2 * pA - pAB
print('\n3) VAN two tickets with s common numbers:')
for s in range(12):
    pA, pAB, pU = van_pair(s)
    print(f'   s={s:2d}: P(A∩B)={float(pAB):.4%}  P(A∪B)={float(pU):.4%}')
print('   => minimum of P(A∩B) at s=5,6 -> max P(any) 16.71%. EV disjoint (20.05%) > VAN best (16.71%).')
pev, _, pevU = two_fields(0); pvan, _, pvanU = van_pair(5)
print(f'   mixed 1 EV + 1 VAN (independent draws): 1-(1-{float(pev):.4f})(1-{float(pvan):.4f}) = {float(1-(1-pev)*(1-pvan)):.4%}')

# ---------- 4. Expected value with pari-mutuel sharing (Poisson co-winners) ----------
print('\n4) Sharing: if co-winners K ~ Poisson(mu), my share of a pool S is S*E[1/(1+K)] = S*(1-e^-mu)/mu.')
for mu in (0.05, 0.1, 0.5, 1, 2, 10, 100):
    print(f'   mu={mu:>6}: E[1/(1+K)] = {(1-math.exp(-mu))/mu:.4f}')
print('   For tiers with many winners (mu>>1) the prize is ~ S/mu: 10% fewer co-winners (unpopular numbers) -> ~11% bigger prize;')
print('   the chance to win does not change (every 6-set has the same hypergeometric law).')

# ---------- 5. Distribution of the total payout of the 2-field EV purchase ----------
ev = json.load(open(sys.argv[1]))
PREM = ('2026-05', '2026-10')
norm = [r for r in ev if r['date'][:4] == '2026' and r['date'][:7] not in PREM]
med = {t: st.median(r['tiers'][t][0] for r in norm if r['tiers'].get(t, [0, 0])[1] > 0) for t in ('5+1', '5+0', '4+1', '4+0', '3+1', '3+0')}
bets = st.mean(r['bets'] for r in ev[-10:])
p61 = F(1, N * 7); p60 = F(6, N * 7)
mu61, mu60 = bets * float(p61), bets * float(p60)
med['6+1'] = 480000 * (1 - math.exp(-mu61)) / mu61   # nominal, before annuity discount
med['6+0'] = 30000 * (1 - math.exp(-mu60)) / mu60
print(f'\n5) Typical prizes, normal months 2026 (median, € ): ' + ', '.join(f'{k} {v:,.1f}' for k, v in med.items()))
def prize(k, ext): return med.get(f'{k}+{1 if ext else 0}', 0.0) if k >= 3 else 0.0
dist = {}
ao = bo = 6; rest = 15
for y in range(7):
    for z in range(7):
        w = 6 - y - z
        if w < 0 or w > rest: continue
        p = F(comb(6, y) * comb(6, z) * comb(rest, w), N)
        for e, pe in (('A', F(1, 7)), ('B', F(1, 7)), ('o', F(5, 7))):
            v = round(prize(y, e == 'A') + prize(z, e == 'B'), 2)
            dist[v] = dist.get(v, F(0)) + p * pe
E = sum(float(p) * v for v, p in dist.items())
Elow = sum(float(p) * v for v, p in dist.items() if v < 20000)
print(f'   E[payout] for 3 € = {E:.3f} €  -> {E/3:.3f} per 1 € (nominal top prize); low tiers only {Elow/3:.3f} per 1 €')
for thr in (3, 3.01, 10, 20, 100, 1000):
    print(f'   P(payout >= {thr} €) = {float(sum(p for v, p in dist.items() if v >= thr)):.4%}')
print(f'   P(payout = 0) = {float(dist.get(0.0, 0)):.4%}')
sd = math.sqrt(sum(float(p) * (v - E) ** 2 for v, p in dist.items()))
print(f'   SD of payout = {sd:,.0f} € (dominated by the top prize): expected loss per draw {3-E:.2f} €; LLN: over n draws loss ~ n*{3-E:.2f} €')

# ---------- 6. Same payout distribution for 2 VAN tickets (s=5) ----------
PZ = {11: 100000, 10: 200, 9: 20, 8: 3, 3: 3, 2: 20, 1: 200, 0: 100000}
def van_dist(s):
    r = 11 - s; d = {}
    for x in range(s + 1):
        for y in range(r + 1):
            for z in range(r + 1):
                w = 11 - x - y - z
                if w < 0 or w > s: continue
                p = F(comb(s, x) * comb(r, y) * comb(r, z) * comb(s, w), M)
                v = PZ.get(x + y, 0) + PZ.get(x + z, 0)
                d[v] = d.get(v, F(0)) + p
    return d
vd = van_dist(5)
print('\n6) VAN 2 tickets, s=5, payout distribution for 3 €:')
for thr in (3, 3.01, 10, 20, 100, 1000):
    print(f'   P(payout >= {thr} €) = {float(sum(p for v, p in vd.items() if v >= thr)):.4%}')
Ev = sum(float(p) * v for v, p in vd.items())
print(f'   E[payout] by rules = {Ev:.3f} € -> {Ev/3:.4f} per 1 € (before top-prize sharing)')
