# exploratory (NOT preregistered): stability of F3 hits across halves / thirds
import sys, json; sys.path.insert(0,'/home/user/Mobil/tipos-all/lab/run_2811/agents'); sys.path.insert(0,'/home/user/Mobil/tipos-all/lab/run_2811')
import numpy as np, S3
from math import comb
from harness2 import load
em=load('EM'); N,K,T=33,7,7
pmf=np.array([comb(T,k)*comb(N-T,K-k) for k in range(T+1)],float)/comb(N,K); mu=(np.arange(T+1)*pmf).sum(); var=((np.arange(T+1)-mu)**2*pmf).sum()
hits=[]
for t in range(30,len(em)):
    P=set(S3.F3(em[:t],em[t]['date'])); hits.append(len(P&set(em[t]['main'])))
h=np.array(hits); n=len(h)
def pu(seg):
    s=np.array([1.0])
    for _ in range(len(seg)): s=np.convolve(s,pmf)
    return float(s[int(seg.sum()):].sum())
res={'all':(n,h.mean(),pu(h))}
for nm,seg in (('half1',h[:n//2]),('half2',h[n//2:]),('third1',h[:n//3]),('third2',h[n//3:2*n//3]),('third3',h[2*n//3:])):
    res[nm]=(len(seg),float(seg.mean()),pu(seg),float((seg.mean()-mu)/np.sqrt(var/len(seg))))
print(json.dumps(res,indent=1)); print('hist',np.bincount(h,minlength=8).tolist(),'expected',(pmf*n).round(1).tolist())
json.dump({'note':'exploratory, not preregistered','F3_splits':res},open('/home/user/Mobil/tipos-all/lab/run_2811/agents/S3_explore.json','w'))
