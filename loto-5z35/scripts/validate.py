import json,math
import numpy as np
from math import comb
rows=[r for r in json.load(open('data/draws_2021_2026.json')) if r['deposits'] and r['w3']]
C=comb(35,5); P3=comb(5,3)*comb(30,2)/C; PRICE=0.50
def fit(sub,lam=3.0):
    n=len(sub)
    y=np.array([math.log(r['w3']/((r['deposits']/PRICE)*P3)) for r in sub])
    X=np.zeros((n,35))
    for i,r in enumerate(sub):
        for num in r['nums']: X[i,num-1]=1.0
    Xc=np.column_stack([np.ones(n),X])
    A=Xc.T@Xc+lam*np.eye(36); A[0,0]-=lam
    b=np.linalg.solve(A,Xc.T@y)
    p=b[1:]-b[1:].mean()
    return b[0],p
train=[r for r in rows if r['date']<'2025-01-01']
test =[r for r in rows if r['date']>='2025-01-01']
print(f"=== OUT-OF-SAMPLE VALIDATION ===")
print(f"train: {len(train)} draws (2021-2024)   test: {len(test)} draws (2025-2026)\n")
_,pop_tr=fit(train)
yt=np.array([math.log(r['w3']/((r['deposits']/PRICE)*P3)) for r in test])
pred=np.array([sum(pop_tr[n-1] for n in r['nums']) for r in test])
c=np.corrcoef(pred,yt)[0,1]
t=c*math.sqrt((len(yt)-2)/(1-c*c))
print(f"correlation between TRAIN-fitted popularity and TEST winner counts:")
print(f"  r = {c:+.3f}   t = {t:+.2f}   {'HOLDS UP' if t>4 else 'weak'}")
slope=np.polyfit(pred,yt,1)[0]
print(f"  regression slope = {slope:.2f}  (1.0 = model transfers perfectly)")
_,pop_full=fit(rows)
print(f"\n  train-vs-full per-number correlation: {np.corrcoef(pop_tr,pop_full)[0,1]:+.3f}")
print(f"  5 least played (train only): {sorted(int(i+1) for i in np.argsort(pop_tr)[:5])}")
print(f"  5 least played (full data) : {sorted(int(i+1) for i in np.argsort(pop_full)[:5])}")
print(f"  5 most  played (full data) : {sorted(int(i+1) for i in np.argsort(pop_full)[-5:])}")

