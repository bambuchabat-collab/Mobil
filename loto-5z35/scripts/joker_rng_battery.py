import json,math,collections
import numpy as np
from scipy.stats import chi2 as X2
rows=[r for r in json.load(open('data/draws_2014_2026.json')) if len(r['joker'])==6]
J=[r['joker'] for r in rows]; n=len(J)
digits=''.join(J)
print(f"=== JOKER RNG TEST BATTERY  ({n} draws, {len(digits)} digits, 2014-2026) ===\n")
def verdict(p): return "PASS" if p>0.01 else ("*** FAIL ***" if p<0.001 else "borderline")

# 1 overall digit frequency
c=collections.Counter(digits); e=len(digits)/10
chi=sum((c[str(d)]-e)**2/e for d in range(10)); p=1-X2.cdf(chi,9)
print(f"1. overall digit frequency      chi2={chi:7.2f} df=9    p={p:.4f}  {verdict(p)}")
print(f"   counts: {[c[str(d)] for d in range(10)]}  (expected {e:.0f} each)")

# 2 per position
print("2. per-position frequency")
for pos in range(6):
    c=collections.Counter(x[pos] for x in J); e=n/10
    chi=sum((c.get(str(d),0)-e)**2/e for d in range(10)); p=1-X2.cdf(chi,9)
    print(f"   position {pos+1}                  chi2={chi:7.2f} df=9    p={p:.4f}  {verdict(p)}")

# 3 last-2 block (the tier that matters most)
c=collections.Counter(x[-2:] for x in J); e=n/100
chi=sum((c.get(f'{i:02d}',0)-e)**2/e for i in range(100)); p=1-X2.cdf(chi,99)
print(f"3. last-2 block (100 cells)     chi2={chi:7.2f} df=99   p={p:.4f}  {verdict(p)}")

# 4 serial correlation of numeric value
v=np.array([int(x) for x in J],dtype=float)
r1=np.corrcoef(v[:-1],v[1:])[0,1]
t=r1*math.sqrt((n-3)/(1-r1**2)); p=2*(1-X2.cdf(t*t,1))
print(f"4. lag-1 autocorr of value      r={r1:+.4f}          p={p:.4f}  {verdict(p)}")

# 5 digit transition matrix (does digit d follow digit e more often?)
seq=[int(x) for x in digits]
M=np.zeros((10,10))
for i in range(len(seq)-1): M[seq[i],seq[i+1]]+=1
e=M.sum()/100
chi=((M-e)**2/e).sum(); p=1-X2.cdf(chi,81)
print(f"5. digit transition matrix      chi2={chi:7.2f} df=81   p={p:.4f}  {verdict(p)}")

# 6 poker test on the 6 digits of each number
def pat(s):
    return tuple(sorted(collections.Counter(s).values(),reverse=True))
cp=collections.Counter(pat(x) for x in J)
# exact probabilities for 6 digits from 10 symbols
from math import comb,factorial
def prob(pattern):
    k=len(pattern); tot=10**6
    ways=factorial(10)//factorial(10-k)
    mult=collections.Counter(pattern)
    for cnt in mult.values(): ways//=factorial(cnt)
    arrange=factorial(6)
    for x in pattern: arrange//=factorial(x)
    return ways*arrange/tot
print("6. digit-pattern (poker) test")
chi=0; df=0
for pt,obs in sorted(cp.items(), key=lambda x:-x[1]):
    ex=prob(pt)*n
    if ex>=5: chi+=(obs-ex)**2/ex; df+=1
    print(f"   {str(pt):22s} obs={obs:5d}  exp={ex:8.1f}")
p=1-X2.cdf(chi,df-1)
print(f"   pattern chi2={chi:7.2f} df={df-1}    p={p:.4f}  {verdict(p)}")

# 7 repeats of full number and of last-2
full_rep=sum(1 for i in range(1,n) if J[i]==J[i-1])
l2=[x[-2:] for x in J]; l2_rep=sum(1 for i in range(1,n) if l2[i]==l2[i-1])
print(f"7. consecutive repeats          full: {full_rep} (exp {(n-1)/1e6:.4f})   last-2: {l2_rep} (exp {(n-1)/100:.1f})")

# 8 gap test: distance between successive appearances of each last-2 value
gaps=collections.defaultdict(list); last={}
for i,x in enumerate(l2):
    if x in last: gaps[x].append(i-last[x])
    last[x]=i
allg=[g for v in gaps.values() for g in v]
print(f"8. gap test on last-2           mean gap={np.mean(allg):.1f} (expected 100)  n={len(allg)}")

# 9 has any single 6-digit number ever repeated?
cc=collections.Counter(J); dup=[k for k,v in cc.items() if v>1]
print(f"9. duplicate 6-digit numbers    {len(dup)} (expected ~{n*(n-1)/2/1e6:.2f} by birthday)")
