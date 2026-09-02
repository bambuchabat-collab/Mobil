import json,math,itertools,random
import numpy as np
from math import comb
rows=json.load(open('data/draws_2014_2026.json'))
pop=np.load('data/pop_recent.npy')
C=comb(35,5); P={k:comb(5,k)*comb(30,5-k)/C for k in (3,4,5)}
PB=0.60
last=[r for r in rows if r['date']=='2026-08-30'][0]
DEP=last['deposits']; BOARDS=DEP/PB; JACK=20000.0; POOL2=0.207*DEP
def ev(t):
    m=math.exp(sum(pop[n-1] for n in t))
    l5=BOARDS*P[5]*m; l4=BOARDS*P[4]*m
    return P[5]*JACK*(1-math.exp(-l5))/l5 + P[4]*POOL2*(1-math.exp(-l4))/l4 + P[3]*3.30
T1=(28,29,30,34,35)
print(f"Ticket 1 (locked in): {list(T1)}  EV={ev(T1):.4f}")

allt=[(ev(t),t) for t in itertools.combinations(range(1,36),5)]
allt.sort(reverse=True)
print("\n=== CANDIDATES FOR TICKET 2 ===")
print(f"{'option':34s} {'overlap':>8s} {'EV2':>8s} {'total EV':>9s} {'P(>=1 prize)':>13s}")

def p_any(tickets):
    """exact P(at least one ticket wins something) by enumerating draws is huge;
       use complement over hypergeometric on the union structure via Monte Carlo"""
    rng=random.Random(99); hit=0; N=400000
    pool=list(range(1,36))
    for _ in range(N):
        d=set(rng.sample(pool,5))
        if any(len(d&set(t))>=3 for t in tickets): hit+=1
    return hit/N

# best overall (ignoring overlap)
best2=allt[1][1]
# best fully disjoint
disj=next(t for _,t in allt if not set(t)&set(T1))
# best sharing at most 1
share1=next(t for _,t in allt if len(set(t)&set(T1))<=1)
opts={
 f"max-EV runner-up {list(best2)}": best2,
 f"share <=1 number {list(share1)}": share1,
 f"fully disjoint   {list(disj)}": disj,
}
for name,t in opts.items():
    ov=len(set(t)&set(T1))
    print(f"{name:34s} {ov:8d} {ev(t):8.4f} {ev(T1)+ev(t):9.4f} {p_any([T1,t]):12.4f}")
single=p_any([T1])
print(f"\n  one ticket alone: P(>=1 prize) = {single:.4f}  (1 in {1/single:.1f})")
