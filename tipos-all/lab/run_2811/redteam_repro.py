"""Red team: re-run all 15 primary formulas through harness2.evaluate in fresh processes, record per-draw hits,
compare with the agents' JSON. Run: python3 -I redteam_repro.py   (writes redteam_repro.json)
"""
import sys, os, json, time
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2811')
from redteam_common import FORMULAS, RUN, setup_paths, get_formula, dump


def job(spec):
    agent, fname, game, rule = spec
    setup_paths()
    t0 = time.time()
    from harness2 import evaluate, load
    f = get_formula(agent, fname)
    rec = {}

    def g(past, date):
        P = f(past, date)
        rec[len(past)] = sorted(int(x) for x in P)
        return P
    r = evaluate(g, game, rule)
    d = load(game)
    ts = sorted(rec)
    hits = [len(set(rec[t]) & set(d[t]['main'])) for t in ts]
    out = {'agent': agent, 'formula': fname, 'game': game, 'rule': rule,
           'eval': {k: (v.item() if hasattr(v, 'item') else v) for k, v in r.items()},
           'ts': ts, 'dates': [d[t]['date'] for t in ts], 'hits': hits, 'seconds': round(time.time() - t0, 1)}
    if (agent, fname) == ('S3', 'F3'):
        out['tickets'] = [rec[t] for t in ts]
    return out


def main():
    import concurrent.futures as cf, multiprocessing as mp
    t0 = time.time()
    res = []
    with cf.ProcessPoolExecutor(4, mp_context=mp.get_context('spawn'), max_tasks_per_child=1) as ex:
        futs = {ex.submit(job, s): s for s in sorted(FORMULAS, key=lambda s: s[:2] in (('S1', 'F1'), ('S5', 'F1'), ('S5', 'F3')), reverse=True)}
        for fu in cf.as_completed(futs):
            o = fu.result(); res.append(o)
            print(o['agent'], o['formula'], o['game'], round(o['eval']['mean_hits'], 4), '%.4f' % o['eval']['p_upper'], o['seconds'], 's', flush=True)
    # compare with agents' JSON
    for o in res:
        j = json.load(open(os.path.join(RUN, 'agents', o['agent'] + '.json')))
        a = next(r for r in j['formulas'] if r['rule'] == o['rule'] and r['game'] == o['game'])
        o['agent_json'] = {k: a[k] for k in ('n', 'mean_hits', 'p_upper', 'p_lower', 'hist')}
        o['match'] = (a['n'] == o['eval']['n'] and abs(a['mean_hits'] - o['eval']['mean_hits']) < 1e-12
                      and abs(a['p_upper'] - o['eval']['p_upper']) < 1e-12 and a['hist'] == o['eval']['hist'])
    res.sort(key=lambda o: [s[:2] for s in FORMULAS].index((o['agent'], o['formula'])))
    dump({'formulas': res, 'all_match': all(o['match'] for o in res), 'seconds': round(time.time() - t0, 1)},
         os.path.join(RUN, 'redteam_repro.json'))
    print('all match:', all(o['match'] for o in res), [(o['agent'], o['formula']) for o in res if not o['match']])


if __name__ == '__main__':
    main()
