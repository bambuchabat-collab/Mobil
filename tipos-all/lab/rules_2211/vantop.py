import json,sys
from math import comb
raw=json.load(open(sys.argv[1]))
def eur(s): return float(s.replace('€','').replace('\xa0','').replace(' ','').replace(',','.')) if s else 0.0
N=comb(22,11); p8=comb(11,8)*comb(11,3)/N; p3=p8; p9=comb(11,9)*comb(11,2)/N; p10=comb(11,10)*11/N
tot_top=0; exp_top=0; rows=[]
for r in raw:
    d=r['raw']; t={x['PocetUhadnutych'].strip():(eur(x['VyskaVyhry']),int(x['PocetVyhier'] or 0)) for x in d['TabulkaVyhier']['Loteria']}
    low=t['8'][1]+t['3'][1]+t['9'][1]+t['2'][1]
    bets=low/(2*p8+2*p9)   # estimate bets from mid tiers
    top=t['11'][1]+t['0'][1]
    tot_top+=top; exp_top+=bets*2/N
    dep=eur(d.get('SumOfDeposits'))
    rows.append((r['date'],bets,dep/1.5 if dep else None,top,t['11'],t['0'],sorted(int(x) for x in d['Zrebovanie'])))
print('draws',len(rows),'top winners',tot_top,'expected if random',round(exp_top,1))
print('avg bets/draw (from tiers)',round(sum(r[1] for r in rows)/len(rows)), 'deposits-based', round(sum(r[2] or 0 for r in rows)/len(rows)))
print('draws with >=1 top win', sum(1 for r in rows if r[3]>0), ' with >=2:', sum(1 for r in rows if r[3]>=2))
for r in rows:
    if r[3]>=2 or (r[3]==1 and (r[4][0] not in (0,100000) and r[4][1]) ): print(r[0],'bets~%d'%r[1],'top',r[3],'11:',r[4],'0:',r[5],r[6])
