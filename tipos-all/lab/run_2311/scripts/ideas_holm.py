"""Subagent 5: Holm-Bonferroni over H1..H10 and the combined ../ideas.json.
python3 -I ideas_holm.py  (after ideas_ev.py, ideas_van.py, ideas_rules.py)
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ideas_common import BASE, holm

ev = json.load(open(os.path.join(BASE, 'ideas_ev_results.json')))
van = json.load(open(os.path.join(BASE, 'ideas_van_results.json')))
rules = json.load(open(os.path.join(BASE, 'ideas_rules_results.json')))
P = {h: ev[h]['p'] for h in ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H10']}
P['H9'] = van['H9']['p']
adj = holm(P)
THR = 0.5   # pp of expected return per 1 EUR (pre-registered)
names = {'H1': 'EV consecutive pairs', 'H2': 'EV slip rows/columns (generic grids)', 'H3': 'EV 1-12 clustering',
         'H4': 'EV copying recent/jackpot/hot draws', 'H5': 'EV spread (SD) of numbers',
         'H6': 'EV arithmetic progressions / multiples of 5', 'H7': 'EV Thursday-specific profile',
         'H8': 'EV premium-month profile', 'H9': 'VAN pattern tickets (windows, odd, even) over-played',
         'H10': 'EV extra number coupled to main numbers'}
table = {}
for h in sorted(P, key=lambda x: int(x[1:])):
    money = ev['money'].get(h, {})
    eff = money.get('effect_pp_per_eur')
    if h == 'H9':
        eff = 0.0
        note = ('fixed tiers; only the 100 000 EUR share can depend on popularity; for a random-looking ticket the '
                'effect is 0 and the absolute cap is %.2f pp; confirms the existing "no odd/even/half tickets" advice'
                % van['top_prize']['max_gain_pp_of_stake'])
    elif h == 'H1':
        pc = ev['money']['H1_posthoc_constrained']
        note = ('pre-registered effect %.2f pp comes from extreme fields (e.g. 18-23, 5 pairs) outside the data support '
                '(draws have 0-3 pairs); POST-HOC within support (<=2 pairs per field, no run of 3): %.2f pp. '
                'Coefficients: -1.2%% 3-match and -6.2%% 4-match winners per consecutive pair in the draw.'
                % (eff, pc['effect_pp_per_eur']))
    elif h == 'H10':
        note = 'direction: choose an extra number that is NOT in your own 6 numbers (+1 tiers share 8% more often)'
    else:
        note = ''
    surv = adj[h] < 0.05
    relevant = (eff is not None and eff >= THR and money.get('ticket_changes', h == 'H10'))
    table[h] = dict(name=names[h], p_raw=P[h], p_holm=adj[h], survives_holm=surv, effect_pp_per_eur=eff,
                    practically_relevant=bool(relevant), finding=bool(surv and relevant), note=note)
out = dict(prereg='ideas_prereg.md', alpha=0.05, k=len(P), practical_threshold_pp_per_eur=THR, tests=table,
           ev_details={h: {kk: vv for kk, vv in ev[h].items()} for h in P if h != 'H9'},
           ev_coefficients=ev['coefficients_full_sample'], ev_money=ev['money'],
           van_H9={k: v for k, v in van['H9'].items() if k != 'cells_9_10_2_1'},
           van_descriptive=dict(D3_prizes_seen=van['D3_prizes_seen'], D6_dispersion=van['D6_dispersion'],
                                top_prize=van['top_prize']),
           rules_descriptive=rules)
json.dump(out, open(os.path.join(BASE, 'ideas.json'), 'w'), indent=1, ensure_ascii=False)
for h, r in table.items():
    print(h, r['name'], 'p=%.4f holm=%.4f eff=%s finding=%s' % (r['p_raw'], r['p_holm'], r['effect_pp_per_eur'],
                                                                 r['finding']))
