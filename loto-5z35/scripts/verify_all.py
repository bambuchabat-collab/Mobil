import json,math,collections,statistics,random
import numpy as np
from math import comb
from scipy.stats import chi2 as X2
rows=json.load(open('data/draws_2014_2026.json'))
N=len(rows); C=comb(35,5)
P={k:comb(5,k)*comb(30,5-k)/C for k in (3,4,5)}

print("V4 PROBABILITIES")
print(f"   C(35,5) = {C:,}   [claimed 324,632]")
for k in (5,4,3): print(f"   match {k}: 1 : {1/P[k]:,.1f}")
print(f"   any prize: 1 : {1/(P[3]+P[4]+P[5]):,.1f}")

print("\nV5 CHI-SQUARE, MAIN GAME")
cnt=collections.Counter()
for r in rows: cnt.update(r['nums'])
exp=N*5/35; chi=sum((cnt[n]-exp)**2/exp for n in range(1,36))
print(f"   harvested n={N}: chi2={chi:.2f} df=34 p={1-X2.cdf(chi,34):.4f}")
off=json.load(open('data/tipos_official_stats.json'))
d2={r['Number']:r['Value'] for r in off['DetailsAll']}
tot=sum(d2.values()); e2=tot/35
chi2v=sum((d2[n]-e2)**2/e2 for n in range(1,36))
print(f"   official n={tot/5:.0f}: chi2={chi2v:.2f} df=34 p={1-X2.cdf(chi2v,34):.4f}")

print("\nV6 POSITION BIAS")
means=[statistics.mean(r['nums'][p] for r in rows) for p in range(5)]
print("   position means: "+"  ".join(f"{m:.2f}" for m in means)+"   [uniform=18.00]")
xs=[p for r in rows for p in range(5)]; ys=[v for r in rows for v in r['nums']]
print(f"   corr(position, value) = {np.corrcoef(xs,ys)[0,1]:+.4f}")

print("\nV7 OVERDUE / GAP")
last={}; buck=collections.defaultdict(lambda:[0,0])
for i,r in enumerate(rows):
    s=set(r['nums'])
    for n in range(1,36):
        if n in last:
            b=min((i-last[n])//5,5); buck[b][1]+=1
            if n in s: buck[b][0]+=1
    for n in s: last[n]=i
for b in sorted(buck):
    h,t=buck[b]; print(f"   gap {b*5}-{b*5+4:>2} draws: P={h/t:.4f} n={t}")
print(f"   [flat expectation 1/7 = {5/35:.4f}]")

print("\nV8 BACKTEST (full data, random baseline averaged over 200 seeds)")
BURN=200
def hot(h):
    c=collections.Counter(n for r in h for n in r['nums'])
    return [n for n,_ in sorted(c.items(),key=lambda x:(-x[1],x[0]))[:5]]
def cold(h):
    c=collections.Counter({n:0 for n in range(1,36)})
    c.update(n for r in h for n in r['nums'])
    return [n for n,_ in sorted(c.items(),key=lambda x:(x[1],x[0]))[:5]]
def over(h):
    L={}
    for i,r in enumerate(h):
        for n in r['nums']: L[n]=i
    return sorted(range(1,36),key=lambda n:(L.get(n,-1),n))[:5]
def hot30(h):
    c=collections.Counter(n for r in h[-30:] for n in r['nums'])
    return [n for n,_ in sorted(c.items(),key=lambda x:(-x[1],x[0]))[:5]]
def rep(h): return h[-1]['nums']
S={'HOT':hot,'COLD':cold,'OVERDUE':over,'HOT30':hot30,'REPEAT':rep}
res={k:[] for k in S}
for t in range(BURN,N):
    h=rows[:t]; a=set(rows[t]['nums'])
    for k,f in S.items(): res[k].append(len(a&set(f(h))))
base=25/35
sd1=math.sqrt(5*(5/35)*(1-5/35)*(35-5)/(35-1))
n_bt=N-BURN
for k in S:
    m=statistics.mean(res[k]); z=(m-base)/(sd1/math.sqrt(n_bt))
    print(f"   {k:8s} mean={m:.4f}  z={z:+.2f}")
rng=random.Random(0)
rm=[statistics.mean(len(set(rows[t]['nums'])&set(rng.sample(range(1,36),5)))
    for t in range(BURN,N)) for _ in range(200)]
print(f"   RANDOM   mean={statistics.mean(rm):.4f}  (theory {base:.4f}, "
      f"sd of the mean {statistics.pstdev(rm):.4f})")
