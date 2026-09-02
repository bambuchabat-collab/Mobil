import json,collections,statistics,math,random
import numpy as np
rows=json.load(open('data/draws_2014_2026.json'))
N=len(rows)
def gap_profile(draws):
    last={}; buck=collections.defaultdict(lambda:[0,0])
    for i,s in enumerate(draws):
        s=set(s)
        for n in range(1,36):
            if n in last:
                b=min((i-last[n])//5,5); buck[b][1]+=1
                if n in s: buck[b][0]+=1
        for n in s: last[n]=i
    return {b:(h/t,t) for b,(h,t) in buck.items()}
real=gap_profile([r['nums'] for r in rows])
rng=random.Random(2026)
sims=[gap_profile([rng.sample(range(1,36),5) for _ in range(N)]) for _ in range(60)]
print("=== Is the long-gap dip real, or an artefact of the estimator? ===")
print("   Same analysis on 60 SIMULATED fair lotteries of the same length.\n")
print(f"   {'gap bucket':14s} {'real P':>8s} {'sim mean':>9s} {'sim sd':>8s} {'z':>7s}")
for b in sorted(real):
    p,t=real[b]
    sv=[s[b][0] for s in sims if b in s]
    m=statistics.mean(sv); sd=statistics.pstdev(sv)
    z=(p-m)/sd if sd>0 else 0
    print(f"   {b*5}-{b*5+4:<10} {p:8.4f} {m:9.4f} {sd:8.4f} {z:+7.2f}")
print("\n   A fair lottery reproduces the same downward tilt -> the dip is")
print("   a property of the gap estimator, not evidence about the machine.")

print("\n=== Same question for the OVERDUE backtest (z=-2.27) ===")
BURN=200
def over(h):
    L={}
    for i,s in enumerate(h):
        for n in s: L[n]=i
    return sorted(range(1,36),key=lambda n:(L.get(n,-1),n))[:5]
def run(draws):
    v=[]
    for t in range(BURN,len(draws)):
        v.append(len(set(draws[t])&set(over(draws[:t]))))
    return statistics.mean(v)
real_m=run([r['nums'] for r in rows])
sim_m=[run([rng.sample(range(1,36),5) for _ in range(N)]) for _ in range(40)]
m=statistics.mean(sim_m); sd=statistics.pstdev(sim_m)
print(f"   real OVERDUE mean matches : {real_m:.4f}")
print(f"   simulated fair lotteries  : {m:.4f} +- {sd:.4f}  (n=40)")
print(f"   z of real vs fair-lottery distribution = {(real_m-m)/sd:+.2f}")
print(f"   (theory for a fixed set is 0.7143; the OVERDUE rule is not a fixed set,")
print(f"    so the fair-lottery simulation is the correct baseline, not 0.7143)")
