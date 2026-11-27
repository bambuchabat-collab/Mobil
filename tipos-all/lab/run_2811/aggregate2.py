"""Holm across all scientists' formulas (primary p_upper)."""
import json, glob, os
HERE = os.path.dirname(os.path.abspath(__file__))
rows = []
for f in sorted(glob.glob(os.path.join(HERE, 'agents', 'S[0-9].json'))):
    j = json.load(open(f))
    for r in j.get('formulas', []):
        rows.append({'id': j['id'], 'science': j.get('science', ''), 'rule': r['rule'], 'game': r['game'],
                     'mean': r['mean_hits'], 'exp': r['expected'], 'p': r['p_upper'], 'n': r['n']})
m = len(rows); order = sorted(range(m), key=lambda i: rows[i]['p']); run = 0
for k, i in enumerate(order):
    run = max(run, min(1, (m - k) * rows[i]['p'])); rows[i]['holm'] = run
rows.sort(key=lambda r: r['p'])
print(f'{m} formulas')
for r in rows:
    print(f"{r['id']} {r['science'][:22]:22} {r['rule'][:26]:26} {r['game']:3} n={r['n']:4} mean {r['mean']:.3f} vs {r['exp']:.3f}  p {r['p']:.4f}  Holm {r['holm']:.3f}")
surv = [r for r in rows if r['holm'] < 0.05]
print('survivors:', surv or 'none')
json.dump({'rows': rows, 'survivors': surv}, open(os.path.join(HERE, 'aggregate2.json'), 'w'), indent=1)
