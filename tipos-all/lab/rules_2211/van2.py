from math import comb
from fractions import Fraction as F
P={11:100000,10:200,9:20,8:3,3:3,2:20,1:200,0:100000}
N=comb(22,11)
def one():
    pa=sum(comb(11,h)*comb(11,11-h) for h in P)/N
    ev=sum(comb(11,h)*comb(11,11-h)*P[h] for h in P)/N
    top=2/N
    return pa,ev,top
pa,ev,top=one()
print(f"1 ticket: any {pa:.6%}  top 1 in {1/top:,.0f}  EV {ev:.4f} per 1.50 -> {ev/1.5:.4f} per 1 EUR")
for s in range(12):
    r=11-s
    any_=0; topw=0; dist={}
    for x in range(s+1):
     for y in range(r+1):
      for z in range(r+1):
        w=11-x-y-z
        if w<0 or w>s: continue
        c=comb(s,x)*comb(r,y)*comb(r,z)*comb(s,w)
        a=x+y; b=x+z
        if a in P or b in P: any_+=c
        if a in (0,11) or b in (0,11): topw+=c
        k=P.get(a,0)+P.get(b,0); dist[k]=dist.get(k,0)+c
    print(f"s={s:2d} any={any_/N:.4%} top=1 in {N/topw:,.0f}")
