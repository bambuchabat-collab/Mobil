import json,math,itertools
import numpy as np
from math import comb
pop=np.load('data/pop_full.npy')
C=comb(35,5); P={k:comb(5,k)*comb(30,5-k)/C for k in (3,4,5)}
PRICE=0.50
DEP=88998.6           # stakes proxy (last comparable draw)
BOARDS=DEP/PRICE
JACKPOT=20000.0       # reset to minimum: won on 30.08
POOL2=0.207*DEP       # empirical tier-2 pool share
FIX3=3.30

def m_of(t): return math.exp(sum(pop[n-1] for n in t))
def ev(t):
    m=m_of(t)
    l5=BOARDS*P[5]*m; l4=BOARDS*P[4]*m
    sh5=(1-math.exp(-l5))/l5; sh4=(1-math.exp(-l4))/l4
    return P[5]*JACKPOT*sh5 + P[4]*POOL2*sh4 + P[3]*FIX3, m

print("=== FINAL OPTIMISATION - draw of 02.09.2026 ===")
print(f"  boards in play ~{BOARDS:,.0f} | jackpot {JACKPOT:,.0f}e (reset) | tier-2 pool {POOL2:,.0f}e\n")
best=[]; 
for t in itertools.combinations(range(1,36),5):
    e,m=ev(t); best.append((e,m,t))
best.sort(reverse=True)
print(f"{'rank':>4s}  {'ticket':<22s} {'popularity':>10s} {'EV':>8s} {'return':>8s}")
for i,(e,m,t) in enumerate(best[:8],1):
    print(f"{i:4d}  {str(list(t)):<22s} {m:10.3f} {e:8.4f} {e/PRICE*100:7.1f}%")
print("  ...")
for i,(e,m,t) in enumerate(best[-3:],len(best)-2):
    print(f"{i:4d}  {str(list(t)):<22s} {m:10.3f} {e:8.4f} {e/PRICE*100:7.1f}%")

import random; random.seed(5)
rs=[ev(random.sample(range(1,36),5))[0] for _ in range(30000)]
avg=sum(rs)/len(rs)
b=best[0]
print(f"\n  average random ticket : EV {avg:.4f}  ({avg/PRICE*100:.1f}% return)")
print(f"  recommended ticket    : EV {b[0]:.4f}  ({b[0]/PRICE*100:.1f}% return)")
print(f"  improvement over average: {(b[0]/avg-1)*100:+.1f}%")
print(f"  improvement over worst  : {(b[0]/best[-1][0]-1)*100:+.1f}%")

print("\n=== PROBABILITIES FOR YOUR ONE TICKET (unchanged by number choice) ===")
for k in (5,4,3):
    print(f"  match {k}: 1 in {1/P[k]:,.0f}   ({P[k]*100:.5f}%)")
pa=P[3]+P[4]+P[5]
print(f"  any prize: 1 in {1/pa:.1f}  ({pa*100:.2f}%)")

print("\n=== JOKER (0.50 EUR, number is RNG-assigned) ===")
JP=325664.40
tickets_j=55194/0.50
lam=tickets_j*1e-6
share=(1-math.exp(-lam))/lam
evj=0.009*3.30+0.0009*33+0.00009*330+0.000009*3300+1e-6*JP*share
print(f"  jackpot {JP:,.2f}e (not hit for 14 draws) | ~{tickets_j:,.0f} joker tickets")
print(f"  expected share if you hit all 6: {share:.3f}")
print(f"  EV = {evj:.4f}e  ->  return {evj/0.50*100:.1f}%")
print(f"  fixed tiers alone: {0.009*3.30+0.0009*33+0.00009*330+0.000009*3300:.4f}e ({(0.009*3.30+0.0009*33+0.00009*330+0.000009*3300)/0.5*100:.1f}%)")
print(f"  the rolled-over jackpot supplies {1e-6*JP*share/evj*100:.0f}% of the joker's value")
print(f"\n  COMBINED (1 board + 1 joker = 1.00e): EV = {b[0]+evj:.4f}e -> {(b[0]+evj)/1.00*100:.1f}% return")
