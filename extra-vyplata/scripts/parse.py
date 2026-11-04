import json,sys,re
raw=json.load(open(sys.argv[1]))
def eur(s): return float(s.replace('€','').replace('\xa0','').replace(' ','').replace(',','.')) if s else 0.0
out=[]
for r in raw:
    d=r['raw']
    main=sorted(int(x) for x in d['Zrebovanie']); pb=int(d['ZrebovanieAdd'])
    tiers={t['PocetUhadnutych'].replace(' ',''):(eur(t['VyskaVyhry']),int(t['PocetVyhier'] or 0)) for t in d['TabulkaVyhier']['Loteria']}
    out.append(dict(date=r['date'],day=d['SKDay'],main=main,pb=pb,order=[int(x) for x in d['Zrebovanie']],deposits=eur(d['SumOfDeposits']),wins=eur(d['SumOfWins']),tiers=tiers))
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
print(len(out)); print(out[-1]); 
import collections
print(collections.Counter(o['day'] for o in out))
print('deposits',sum(o['deposits'] for o in out),'wins',sum(o['wins'] for o in out))
