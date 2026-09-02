import json,math,collections
import numpy as np
from scipy.stats import chi2 as X2
rows=[r for r in json.load(open('data/draws_2014_2026.json')) if len(r['joker'])==6]
J=[r['joker'] for r in rows]; n=len(J)
print(f"=== SECOND-ROUND JOKER TESTS ({n} draws) ===\n")

# 1. day-of-week conditioning
print("1. Does the day of the week change the digit distribution?")
names={2:'Wed',4:'Fri',6:'Sun'}
for dw in (2,4,6):
    sub=[r['joker'] for r in rows if r['dow']==dw]
    if len(sub)<50: continue
    c=collections.Counter(''.join(sub)); e=len(sub)*6/10
    chi=sum((c[str(d)]-e)**2/e for d in range(10)); p=1-X2.cdf(chi,9)
    print(f"   {names[dw]:4s} n={len(sub):4d}  chi2={chi:6.2f}  p={p:.3f}  {'PASS' if p>0.01 else 'FAIL'}")

# 2. drift over time
print("\n2. Has the generator drifted over 12 years?")
for lo,hi in [('2014','2016'),('2017','2019'),('2020','2022'),('2023','2026')]:
    sub=[r['joker'] for r in rows if lo<=r['date'][:4]<=hi]
    c=collections.Counter(''.join(sub)); e=len(sub)*6/10
    chi=sum((c[str(d)]-e)**2/e for d in range(10)); p=1-X2.cdf(chi,9)
    print(f"   {lo}-{hi} n={len(sub):4d}  chi2={chi:6.2f}  p={p:.3f}  {'PASS' if p>0.01 else 'FAIL'}")

# 3. is the joker linked to the ball draw?
print("\n3. Is the joker correlated with the same draw's 5 balls?")
jv=np.array([int(x) for x in J],float)
bs=np.array([sum(r['nums']) for r in rows],float)
b1=np.array([r['nums'][0] for r in rows],float)
for nm,x in (('sum of 5 balls',bs),('first ball drawn',b1)):
    c=np.corrcoef(x,jv)[0,1]; t=c*math.sqrt((n-2)/(1-c*c))
    print(f"   vs {nm:18s} r={c:+.4f} t={t:+5.2f}  {'PASS' if abs(t)<2.9 else 'FAIL'}")
# last digit of joker vs last ball mod 10
ld=np.array([int(x[-1]) for x in J]); bl=np.array([r['nums'][-1]%10 for r in rows])
M=np.zeros((10,10))
for a,b in zip(bl,ld): M[a,b]+=1
e=M.sum()/100; chi=((M-e)**2/e).sum(); p=1-X2.cdf(chi,81)
print(f"   last ball mod10 x joker last digit: chi2={chi:.1f} df=81 p={p:.3f}  {'PASS' if p>0.01 else 'FAIL'}")

# 4. digit-sum distribution
print("\n4. Digit-sum distribution vs theory")
ds=[sum(int(c) for c in x) for x in J]
# exact distribution of sum of 6 uniform digits
dist=np.zeros(55); dist[0]=1
for _ in range(6):
    nd=np.zeros(55)
    for s in range(55):
        if dist[s]:
            for d in range(10):
                if s+d<55: nd[s+d]+=dist[s]/10
    dist=nd
obs=collections.Counter(ds)
chi=0; df=0
for s in range(55):
    e=dist[s]*n
    if e>=5: chi+=(obs.get(s,0)-e)**2/e; df+=1
p=1-X2.cdf(chi,df-1)
print(f"   mean={np.mean(ds):.2f} (theory 27.0)  chi2={chi:.1f} df={df-1} p={p:.3f}  {'PASS' if p>0.01 else 'FAIL'}")

# 5. digit-level lag-1 dependence per position
print("\n5. Does each position depend on the previous draw's same position?")
worst=1.0
for pos in range(6):
    a=[int(x[pos]) for x in J[:-1]]; b=[int(x[pos]) for x in J[1:]]
    M=np.zeros((10,10))
    for u,v in zip(a,b): M[u,v]+=1
    e=M.sum()/100; chi=((M-e)**2/e).sum(); p=1-X2.cdf(chi,81)
    worst=min(worst,p)
    print(f"   position {pos+1}: chi2={chi:6.1f} df=81 p={p:.3f}")
print(f"   worst p across 6 positions = {worst:.3f}  {'PASS' if worst>0.01/6 else 'FAIL'}")

# 6. attractive-number test (would manual pickers cluster?)
print("\n6. Do 'attractive' endings show extra winners (manual pickers)?")
recs=[(r['joker'],r['dep_joker']/0.60,r['jw2']) for r in rows if r.get('dep_joker') and r.get('jw2')]
y=np.array([math.log(w/(tk*0.009)) for _,tk,w in recs]); m=len(y)
def f_att(e):
    return 1.0 if (e[0]==e[1] or abs(int(e[0])-int(e[1]))==1 or e in ('00','69','13','07','77')) else 0.0
x=np.array([f_att(j[-2:]) for j,_,_ in recs])
c=np.corrcoef(x,y)[0,1]; t=c*math.sqrt((m-2)/(1-c*c))
print(f"   'attractive' last-2 endings: r={c:+.3f} t={t:+.2f} (n={m})  "
      f"{'clustering!' if abs(t)>2.9 else 'no clustering'}")
