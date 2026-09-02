import json,math,collections
import numpy as np
from scipy.stats import chi2 as X2
rows=[r for r in json.load(open('data/draws_2014_2026.json'))
      if len(r['joker'])==6 and r.get('dep_joker') and r.get('jw2')]
n=len(rows)
print(f"=== DO OTHER PLAYERS' JOKER NUMBERS CLUSTER?  (n={n} draws) ===")
print("If joker numbers were player-CHOSEN, some endings would be held by")
print("many more people, and those draws would produce more tier-5 winners.\n")
# observed vs expected tier-5 (last-2 match) winners
y=np.array([math.log(r['jw2']/((r['dep_joker']/0.50)*0.009)) for r in rows])
print(f"log(observed/expected winners): mean={y.mean():+.4f} sd={y.std():.4f}")
feats={
 'repdigit (00,11,..)': lambda e:1.0 if e[0]==e[1] else 0.0,
 'ends in 0'          : lambda e:1.0 if e[1]=='0' else 0.0,
 'ends in 7'          : lambda e:1.0 if e[1]=='7' else 0.0,
 'contains 7'         : lambda e:1.0 if '7' in e else 0.0,
 'contains 0'         : lambda e:1.0 if '0' in e else 0.0,
 'ascending'          : lambda e:1.0 if int(e[1])-int(e[0])==1 else 0.0,
 'both digits <=3'    : lambda e:1.0 if int(e[0])<=3 and int(e[1])<=3 else 0.0,
 'numeric value'      : lambda e:float(int(e)),
}
print(f"\n{'feature':22s} {'r':>8s} {'t':>7s}  {'verdict':<22s}")
ts={}
for nm,fn in feats.items():
    x=np.array([fn(r['joker'][-2:]) for r in rows])
    if x.std()==0: continue
    c=np.corrcoef(x,y)[0,1]; t=c*math.sqrt((n-2)/(1-c*c)); ts[nm]=t
    # Bonferroni over 8 tests -> |t|>2.9
    v="significant" if abs(t)>2.9 else "no effect"
    print(f"{nm:22s} {c:+8.3f} {t:+7.2f}  {v:<22s}")

print("\n--- direct test: are the 100 endings equally held by players? ---")
g=collections.defaultdict(list)
for r,v in zip(rows,y): g[r['joker'][-2:]].append(v)
cells=[(e,np.mean(v),len(v)) for e,v in g.items() if len(v)>=5]
means=np.array([m for _,m,_ in cells]); cnts=np.array([c for _,_,c in cells])
noise=y.var()/cnts.mean()
between=means.var()
print(f"  cells with >=5 draws: {len(cells)}")
print(f"  between-ending variance {between:.6f}  vs pure sampling noise {noise:.6f}")
print(f"  ratio = {between/noise:.2f}   (1.00 = players' numbers are uniform / RNG)")
# formal test
stat=(cnts*(means-y.mean())**2).sum()/y.var()
p=1-X2.cdf(stat,len(cells)-1)
print(f"  chi2={stat:.1f} df={len(cells)-1}  p={p:.4f}  -> "
      f"{'clustering detected' if p<0.01 else 'NO clustering: uniform'}")
