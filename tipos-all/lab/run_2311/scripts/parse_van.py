"""Clean Všetko alebo nič raw history -> van.json (oldest first)."""
import json, sys
def eur(s): return float(s.replace('€','').replace('\xa0','').replace(' ','').replace(',','.')) if s else 0.0
raw = json.load(open(sys.argv[1])); out = []
for r in raw:
    x = r['raw']
    if not x or not x.get('Zrebovanie'): continue
    tiers = {t['PocetUhadnutych'].strip(): [eur(t['VyskaVyhry']), int((t['PocetVyhier'] or '0').replace(' ', ''))]
             for t in x['TabulkaVyhier']['Loteria']}
    out.append({'date': r['date'], 'day': x.get('SKDay'), 'main': sorted(int(v) for v in x['Zrebovanie']),
                'order': [int(v) for v in x['Zrebovanie']], 'deposits': eur(x.get('SumOfDeposits')),
                'wins': eur(x.get('SumOfWins')), 'bets': eur(x.get('SumOfDeposits')) / 1.5, 'tiers': tiers,
                'premium': x.get('Premium'), 'premium_text': x.get('PremiumText')})
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0)
print(len(out), out[0]['date'], out[-1]['date'])
