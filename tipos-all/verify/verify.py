"""Re-verification: (1) old vs fresh snapshots, (2) our counts vs TIPOS official statistics.
Usage: python3 -I verify.py <old_dir> <new_dir> <official_dir> <out.json>
"""
import json, sys, os, datetime
OLD, NEW, OFF, OUT = sys.argv[1:5]
TODAY = datetime.date(2026, 11, 9)

def load(path):
    if not os.path.exists(path): return {}
    return {r['date']: r['raw'] for r in json.load(open(path)) if r['raw']}

def official(g):
    d = json.load(open(os.path.join(OFF, g + '.json')))
    return json.loads(d) if isinstance(d, str) else d

games = {  # name: (old file, new file, official id, main key, extra key)
    'Extra výplata': ('../draws_raw_ev.json', 'ev.json', 'extravyplata', 'Zrebovanie', 'ZrebovanieAdd'),
    'Loto 5 z 35': ('l535.json', 'l535.json', 'loto5z35', 'Zrebovanie', None),
    'Loto': ('loto.json', 'loto.json', 'loto', 'ZrebovanieTah1', None),
    'Euromilióny': ('em.json', 'em.json', 'euromiliony', 'Zrebovanie', 'ZrebovanieAdd'),
    'Eurojackpot': ('ej.json', 'ej.json', 'eurojackpot', 'Zrebovanie', 'ZrebovanieAdd'),
    'Všetko alebo nič': ('van.json', 'van_full.json', 'vsetkoalebonic', 'Zrebovanie', None),
}
res = {}
for name, (fo, fn, gid, mk, ek) in games.items():
    old = load(os.path.join(OLD, fo)); new = load(os.path.join(NEW, fn))
    common = sorted(set(old) & set(new))
    changed = [d for d in common if json.dumps(old[d], sort_keys=True) != json.dumps(new[d], sort_keys=True)]
    changed_numbers = [d for d in common if old[d].get(mk) != new[d].get(mk) or (ek and old[d].get(ek) != new[d].get(ek))]
    r = {'old_draws': len(old), 'new_draws': len(new), 'only_in_new': sorted(set(new) - set(old)), 'only_in_old': sorted(set(old) - set(new)),
         'records_changed_any_field': len(changed), 'records_changed_numbers': changed_numbers, 'first': min(new), 'last': max(new)}
    if changed and not changed_numbers:
        # describe which fields differ (e.g. later-filled prize counts)
        diff_keys = set()
        for d in changed[:50]:
            for k in set(old[d]) | set(new[d]):
                if json.dumps(old[d].get(k), sort_keys=True) != json.dumps(new[d].get(k), sort_keys=True): diff_keys.add(k)
        r['changed_fields'] = sorted(diff_keys)
    # official cross-check
    off = official(gid)
    def counts(dates, key):
        c = {}
        for d in dates:
            v = new[d].get(key)
            if v is None: continue
            for x in (v if isinstance(v, list) else [v]): c[int(x)] = c.get(int(x), 0) + 1
        return c
    checks = {}
    for period, days in [('DetailsAll', None), ('Details12M', 365), ('Details6M', 182), ('Details1M', 30)]:
        offd = off.get(period)
        if not offd: continue
        o = {x['Number']: x['Value'] for x in offd}
        best = None
        cand_windows = [None] if days is None else [days - 1, days, days + 1, days + 2]
        for w in cand_windows:
            dates = sorted(new) if w is None else [d for d in new if datetime.date.fromisoformat(d) > TODAY - datetime.timedelta(days=w)]
            ours = counts(dates, mk)
            diff = sum(abs(ours.get(k, 0) - v) for k, v in o.items()) + sum(v for k, v in ours.items() if k not in o)
            if best is None or diff < best[0]: best = (diff, w, len(dates), sum(o.values()), sum(ours.values()))
        checks[period] = {'abs_diff_total': best[0], 'window_days': best[1], 'our_draws_in_window': best[2], 'official_sum': best[3], 'our_sum': best[4]}
    if ek and off.get('AdditionalAll'):
        o = {x['Number']: x['Value'] for x in off['AdditionalAll']}
        ours = counts(sorted(new), ek)
        checks['AdditionalAll'] = {'abs_diff_total': sum(abs(ours.get(k, 0) - v) for k, v in o.items()), 'official_sum': sum(o.values()), 'our_sum': sum(ours.values())}
    r['official_check'] = checks
    res[name] = r
json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1)
for k, v in res.items():
    print('==', k, {kk: vv for kk, vv in v.items() if kk not in ('official_check',)})
    print('   official:', v['official_check'])
