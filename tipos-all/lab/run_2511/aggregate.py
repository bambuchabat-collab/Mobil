"""Collect agents/A*.json, apply Holm across ALL rules (primary p_mean_lower; secondary p_le3 separately)."""
import json, glob, os
HERE = os.path.dirname(os.path.abspath(__file__))
rows = []
for f in sorted(glob.glob(os.path.join(HERE, 'agents', 'A*.json'))):
    j = json.load(open(f))
    for r in j.get('rules', []):
        rows.append({'agent': j.get('id', os.path.basename(f)), 'family': j.get('family', ''), 'rule': r['rule'],
                     'mean_hits': r['mean_hits'], 'p': r['p_mean_lower'], 'p_le3': r['p_le3'],
                     'n_zero': r['n_zero'], 'won': r['won_eur'], 'cost': r['cost_eur']})
def holm(ps):
    m = len(ps); order = sorted(range(m), key=lambda i: ps[i]); adj = [0] * m; run = 0
    for k, i in enumerate(order):
        run = max(run, min(1, (m - k) * ps[i])); adj[i] = run
    return adj
for key, out in (('p', 'holm'), ('p_le3', 'holm_le3')):
    for r, a in zip(rows, holm([r[key] for r in rows])): r[out] = a
rows.sort(key=lambda r: r['p'])
print(f"{len(rows)} rules from {len({r['agent'] for r in rows})} agents")
print(f"{'agent':5} {'rule':38} {'mean':>6} {'p':>7} {'Holm':>6} {'p<=3':>7} {'Holm':>6} {'0hit':>4} {'won':>5}")
for r in rows:
    print(f"{r['agent']:5} {r['rule'][:38]:38} {r['mean_hits']:6.3f} {r['p']:7.4f} {r['holm']:6.3f} {r['p_le3']:7.4f} {r['holm_le3']:6.3f} {r['n_zero']:4d} {r['won']:5.0f}")
surv = [r for r in rows if r['holm'] < 0.05 or r['holm_le3'] < 0.05]
print('survivors (Holm < 0.05):', [(r['agent'], r['rule']) for r in surv] or 'none')
json.dump({'rows': rows, 'survivors': surv}, open(os.path.join(HERE, 'aggregate.json'), 'w'), indent=1)
