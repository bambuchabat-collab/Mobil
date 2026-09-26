from fractions import Fraction
from math import comb
P,K,E=33,7,6
T=comb(P,K)*E
TIERS={(7,1):25_632_288,(7,0):5_126_458,(6,1):140_837,(6,0):28_167,
       (5,1):3_756,(5,0):751,(4,1):282,(4,0):56,(3,1):49,(2,1):19}
PAY=set(TIERS)
def cnt(k,j): return comb(K,k)*comb(P-K,K-k)*(1 if j else E-1)
print(f"C(33,7)*6 = {T:,}\n")
ok=True
for (k,j),off in TIERS.items():
    c=cnt(k,j); o=T/c; m=round(o)==off or int(o)==off; ok&=m
    print(f"  {k}+{j}  {c:>9,}  exact 1:{o:>12,.1f}  TIPOS 1:{off:>10,}  {'OK' if m else 'MISMATCH'}")
assert ok, "model invalid"
print("\nAll 10 tiers match the official table -> model validated.\n")
p1=Fraction(sum(cnt(k,j) for k,j in PAY),T)
print(f"P(any prize), ONE ticket = {p1} = {float(p1)*100:.5f}%  (1 in {1/float(p1):.2f})")

def mh(sizes,draw):
    out=[]
    def rec(i,rem,cur,w):
        if i==len(sizes)-1:
            if rem<=sizes[i]: out.append((tuple(cur)+(rem,),w*comb(sizes[i],rem)))
            return
        for n in range(min(sizes[i],rem)+1): rec(i+1,rem-n,cur+[n],w*comb(sizes[i],n))
    rec(0,draw,[],1); return out

def two(a,same_extra):
    """a = shared main numbers; same_extra = both tickets use the same extra."""
    reg=[a,K-a,K-a,P-(2*K-a)]
    law={}
    for (n11,n10,n01,_),w in mh(reg,K):
        law[(n11+n10,n11+n01)]=law.get((n11+n10,n11+n01),0)+w
    tot=win=both=0
    for (mA,mB),w in law.items():
        for eA,eB,we in ([(1,1,1),(0,0,E-1)] if same_extra else
                         [(1,0,1),(0,1,1),(0,0,E-2)]):
            ww=w*we; tot+=ww
            pa,pb=(mA,eA) in PAY,(mB,eB) in PAY
            if pa or pb: win+=ww
            if pa and pb: both+=ww
    assert tot==T
    return Fraction(win,tot),Fraction(both,tot)

print("\nTWO TICKETS - configuration comparison (exact):\n")
print(f"{'shared mains':>13} {'extra':>10} {'P(any prize)':>14} {'P(both win)':>13}")
best=None
for a in (0,1,2):
    for se in (True,False):
        p,b=two(a,se)
        tag='same' if se else 'diff'
        if best is None or p>best[0]: best=(p,a,tag,b)
        print(f"{a:>13} {tag:>10} {float(p)*100:>13.5f}% {float(b)*100:>12.5f}%")
p,a,tag,b=best
print(f"\nBEST: {a} shared main numbers, {tag} extra number")
print(f"  P(any prize, 2 tickets) = {p} = {float(p)*100:.5f}%  (1 in {1/float(p):.2f})")
print(f"  P(both win)             = {float(b)*100:.5f}%   (so NOT simply additive)")
print(f"  naive 2x one ticket     = {float(2*p1)*100:.5f}%")
