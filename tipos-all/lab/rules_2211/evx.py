import json,sys
from math import comb
raw=json.load(open(sys.argv[1]))
def eur(s): return float(s.replace('€','').replace('\xa0','').replace(' ','').replace(',','.')) if s else 0.0
N=comb(27,6)
def pm(k): return comb(6,k)*comb(21,6-k)/N
P={(k,e):pm(k)*(1/7 if e else 6/7) for k in (3,4,5,6) for e in (1,0)}
print('P any 1 field %.4f%%'%(100*sum(P.values())))
# two disjoint fields
any2=sum(comb(6,a)*comb(6,b)*comb(15,6-a-b) for a in range(7) for b in range(7) if a+b<=6 and (a>=3 or b>=3))/N
print('P any 2 disjoint fields %.4f%%'%(100*any2))
# realized tiers 3-8 share per bet, by draw
rows=[]
for r in raw:
    d=r['raw']; dep=eur(d.get('SumOfDeposits')); bets=dep/1.5
    if not bets: continue
    t={x['PocetUhadnutych'].replace(' ',''):(eur(x['VyskaVyhry']),int(x['PocetVyhier'] or 0)) for x in d['TabulkaVyhier']['Loteria']}
    low=sum(t[k][0]*t[k][1] for k in t if k not in ('6+1','6+0'))
    rows.append((r['date'],bets,low/dep,t))
import statistics as st
print('draws',len(rows),'bets/draw mean',round(st.mean(r[1] for r in rows)),'last10',[round(r[1]) for r in rows[-10:]])
print('tiers3-8 payout share of stake: mean %.4f, last 20 %.4f'%(st.mean(r[2] for r in rows),st.mean(r[2] for r in rows[-20:])))
bets=st.mean(r[1] for r in rows[-20:])
import math
def share(lam): return (1-math.exp(-lam))/lam
l1=bets*P[(6,1)]; l2=bets*P[(6,0)]
for pv in (1.0,0.86):
    top=480000*pv*P[(6,1)]*share(l1)+30000*P[(6,0)]*share(l2)
    print('pv',pv,'top tiers EV per 1.50: %.4f -> total ratio %.4f'%(top, st.mean(r[2] for r in rows[-20:])+top/1.5))
# months with an Extra výplata premium decision (tiers 3-8 doubled): May and October 2026
PREM=('2026-05','2026-10')
norm=[r for r in rows if r[0][:7] not in PREM]; prem=[r for r in rows if r[0][:7] in PREM]
for name,sub in (('normal',norm),('premium',prem)):
    low=st.mean(r[2] for r in sub)
    for pv in (1.0,0.86):
        top=480000*pv*P[(6,1)]*share(l1)+30000*P[(6,0)]*share(l2)
        print(f'{name}: draws {len(sub)}, tiers3-8 {low:.4f}, pv {pv}: total return {low+top/1.5:.4f}')
