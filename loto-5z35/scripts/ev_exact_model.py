"""AUDIT: my EV scaled the sharing by MY ticket's popularity.
That is wrong. The number of people who also win depends on the popularity
of the DRAWN numbers, conditional on my ticket matching. Done exactly here
with elementary symmetric polynomials."""
import json,math,itertools
import numpy as np
from math import comb
rows=json.load(open('data/draws_2014_2026.json'))
pop=np.load('data/pop_recent.npy')
u=np.exp(pop)                       # per-number relative play weight
PB=0.60
wed=[r['deposits'] for r in rows if r['dow']==2 and r['date']>='2026-01-01']
DEP=float(np.median(wed)); BOARDS=DEP/PB
POOL1=max(20000.0,0.25*DEP); POOL2=0.2047*DEP; FIX3=3.30
print(f"today: stakes~{DEP:,.0f}  boards~{BOARDS:,.0f}  pool1={POOL1:,.0f}  pool2={POOL2:,.0f}")

def esp(vals,k):
    """elementary symmetric polynomial e_k"""
    e=np.zeros(k+1); e[0]=1.0
    for v in vals:
        for j in range(min(k,len(e)-1),0,-1): e[j]+=e[j-1]*v
    return e[k]
E5_ALL=esp(u,5)                      # total weight over all tickets

def ev_exact(T):
    T=list(T); notT=[n for n in range(1,36) if n not in T]
    uT=u[[n-1 for n in T]]
    ev=0.0
    # ---- k=5: draw equals my ticket
    D=T; uD=uT
    p_draw=1.0/comb(35,5)
    w5=np.prod(uD)/E5_ALL                       # P(another board = this exact set)
    lam=(BOARDS-1)*w5
    share=(1-math.exp(-lam))/lam if lam>1e-12 else 1.0
    ev+=p_draw*POOL1*share
    # ---- k=4: draw shares 4 with my ticket
    for four in itertools.combinations(T,4):
        for extra in notT:
            D=list(four)+[extra]
            uD=u[[n-1 for n in D]]
            uNot=u[[n-1 for n in range(1,36) if n not in D]]
            w4=esp(uD,4)*esp(uNot,1)/E5_ALL      # P(another board matches exactly 4 of D)
            lam=(BOARDS-1)*w4
            share=(1-math.exp(-lam))/lam if lam>1e-12 else 1.0
            ev+=p_draw*POOL2*share
    # ---- k=3: fixed prize, sharing irrelevant
    ev+=(comb(5,3)*comb(30,2)/comb(35,5))*FIX3
    return ev

# old approximate model, for comparison
P={k:comb(5,k)*comb(30,5-k)/comb(35,5) for k in (3,4,5)}
def ev_approx(T):
    m=math.exp(sum(pop[n-1] for n in T))
    l5=BOARDS*P[5]*m; l4=BOARDS*P[4]*m
    return P[5]*POOL1*(1-math.exp(-l5))/l5 + P[4]*POOL2*(1-math.exp(-l4))/l4 + P[3]*FIX3

tests={'my ticket 1':(28,29,30,34,35),'my ticket 2':(16,18,26,31,32),
       'suggested t2':(16,26,31,32,35),'worst':(3,5,7,8,9),'mid':(4,11,17,23,29)}
print(f"\n{'ticket':16s} {'approx EV':>10s} {'EXACT EV':>10s} {'diff':>8s}")
for nm,t in tests.items():
    a=ev_approx(t); e=ev_exact(t)
    print(f"{nm:16s} {a:10.4f} {e:10.4f} {(e/a-1)*100:+7.2f}%")
np.save('/tmp/u.npy',u)
