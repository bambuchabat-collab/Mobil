import json,math,itertools
import numpy as np
from math import comb
rows=json.load(open('data/draws_2014_2026.json'))
pop=np.load('data/pop_recent.npy'); u=np.exp(pop)
PB=0.60
wed=[r['deposits'] for r in rows if r['dow']==2 and r['date']>='2026-01-01']
DEP=float(np.median(wed)); BOARDS=DEP/PB
POOL1=max(20000.0,0.25*DEP); POOL2=0.2047*DEP; FIX3=3.30
def esp(vals,k):
    e=np.zeros(k+1); e[0]=1.0
    for v in vals:
        for j in range(min(k,len(e)-1),0,-1): e[j]+=e[j-1]*v
    return e[k]
E5=esp(u,5); UTOT=u.sum(); uinv=1.0/u
P3=comb(5,3)*comb(30,2)/comb(35,5); pdraw=1.0/comb(35,5)

tickets=np.array(list(itertools.combinations(range(35),5)),dtype=np.int64)
NT=len(tickets); print(f"evaluating all {NT:,} tickets with the exact model...")
ev=np.full(NT,P3*FIX3)
CH=20000
for s in range(0,NT,CH):
    T=tickets[s:s+CH]                       # (c,5) zero-based
    uT=u[T]                                 # (c,5)
    prodT=uT.prod(1); sumT=uT.sum(1); sinvT=uinv[T].sum(1)
    # ---- k=5
    lam=(BOARDS-1)*prodT/E5
    ev[s:s+CH]+=pdraw*POOL1*np.where(lam>1e-12,(1-np.exp(-lam))/np.maximum(lam,1e-12),1.0)
    # ---- k=4: drop one of 5, add one of the 30 outside
    mask=np.ones((len(T),35),bool)
    np.put_along_axis(mask,T,False,axis=1)
    acc=np.zeros(len(T))
    for di in range(5):
        ui=uT[:,di]
        pT=prodT/ui; sT=sumT-ui; sI=sinvT-1.0/ui
        for e_idx in range(35):
            col=mask[:,e_idx]
            if not col.any(): continue
            ue=u[e_idx]
            prodD=pT*ue; sumD=sT+ue; sinvD=sI+1.0/ue
            e4=prodD*sinvD
            e1=UTOT-sumD
            lam4=(BOARDS-1)*e4*e1/E5
            sh=np.where(lam4>1e-12,(1-np.exp(-lam4))/np.maximum(lam4,1e-12),1.0)
            acc+=np.where(col,pdraw*POOL2*sh,0.0)
    ev[s:s+CH]+=acc
order=np.argsort(-ev)
print(f"\n{'rank':>5s}  {'ticket':<24s} {'EV':>8s} {'return':>8s}")
for r in range(10):
    i=order[r]; t=[int(x)+1 for x in tickets[i]]
    print(f"{r+1:5d}  {str(t):<24s} {ev[i]:8.4f} {ev[i]/PB*100:7.2f}%")
print("  ...")
for r in range(3):
    i=order[-3+r]; t=[int(x)+1 for x in tickets[i]]
    print(f"{NT-2+r:5d}  {str(t):<24s} {ev[i]:8.4f} {ev[i]/PB*100:7.2f}%")
def rank_of(tk):
    key=tuple(sorted(x-1 for x in tk))
    idx=np.where((tickets==np.array(key)).all(1))[0][0]
    return int(np.where(order==idx)[0][0])+1, ev[idx]
for nm,tk in (('MY TICKET 1',(28,29,30,34,35)),('MY TICKET 2',(16,18,26,31,32)),
              ('suggested t2',(16,26,31,32,35))):
    rk,e=rank_of(tk)
    print(f"\n{nm} {list(tk)}: rank {rk:,} of {NT:,}   EV {e:.4f} ({e/PB*100:.2f}%)")
print(f"\naverage ticket EV: {ev.mean():.4f} ({ev.mean()/PB*100:.2f}%)")
print(f"best vs average: {(ev[order[0]]/ev.mean()-1)*100:+.1f}%   "
      f"best vs worst: {(ev[order[0]]/ev[order[-1]]-1)*100:+.1f}%")
np.save('/tmp/ev_exact.npy',ev)
