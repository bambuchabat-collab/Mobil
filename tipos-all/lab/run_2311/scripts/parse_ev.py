"""Clean Extra výplata raw history -> ev.json (list of draws, oldest first)."""
import json, sys
def eur(s): return float(s.replace('€','').replace('\xa0','').replace(' ','').replace(',','.')) if s else 0.0
raw = json.load(open(sys.argv[1])); out = []
for r in raw:
    x = r['raw']
    if not x or not x.get('Zrebovanie'): continue
    tiers = {t['PocetUhadnutych'].replace(' ', ''): [eur(t['VyskaVyhry']), int((t['PocetVyhier'] or '0').replace(' ', ''))]
             for t in x['TabulkaVyhier']['Loteria']}
    order = [int(v) for v in x['Zrebovanie']]
    out.append({'date': r['date'], 'day': x.get('SKDay'), 'main': sorted(order), 'order': order,
                'pb': int(x['ZrebovanieAdd']), 'deposits': eur(x.get('SumOfDeposits')), 'wins': eur(x.get('SumOfWins')),
                'bets': eur(x.get('SumOfDeposits')) / 1.5, 'tiers': tiers})
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0)
print(len(out), out[0]['date'], out[-1]['date'])
