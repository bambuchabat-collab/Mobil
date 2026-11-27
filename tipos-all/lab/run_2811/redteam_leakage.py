"""Red team task 1: LEAKAGE audit of the 15 primary formulas (agents/S1..S5.py).
 A. static scan (ast): data access at module level / inside functions, frame inspection, file names.
 B. dynamic test per formula, in fresh processes (spawn, one task per process):
    real    - predictions for sampled t through a harness-like loop (local `d` = full history), audit hook logs
              every file opened while a formula runs;
    perturb - for each sampled t, ALL draws dated >= date_t (in em.json, van415.json, em_raw.json) are replaced by
              random draws; builtins.open / io.open are redirected to the perturbed copies BEFORE the agent module is
              imported (so module-level caches see the perturbed future), the caller's local `d` is perturbed too;
              prediction for t must equal the real one;
    poison  - same process, then f(full perturbed history) is called first (fills caches with the fake future),
              then f(d[:t]) again: must still equal the real prediction.
 C. positive controls (redteam_pc.py): PC1 module cache, PC2 direct file read by date, PC3 caller-frame peek,
    PC4 full-history frequencies, PC5 off-by-one (includes the evaluated draw); PC0 legit (must pass).
Run: python3 -I redteam_leakage.py   (writes redteam_leakage.json)
"""
import sys, os, json, time, ast, re
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2811')
from redteam_common import FORMULAS, RUN, DATA, SCRATCH, setup_paths, get_formula, dump

CONTROLS = [('PC0', 'PC0_legit', 'EM', 'legit'), ('PC1', 'PC1_modcache', 'EM', 'peek'), ('PC1', 'PC1_VAN', 'VAN', 'peek'),
            ('PC2', 'PC2_fileread', 'EM', 'peek'), ('PC3', 'PC3_frame', 'EM', 'peek'),
            ('PC4', 'PC4_fullfreq', 'EM', 'peek'), ('PC5', 'PC5_offbyone', 'EM', 'peek')]


def sample_ts(game, n):
    import numpy as np
    rng = np.random.default_rng([2811, 1 if game == 'EM' else 2])
    mid = sorted(int(x) for x in rng.choice(np.arange(32, n - 1), 4, replace=False))
    return [30, 31] + mid + [n - 1]


# ------------------------------------------------------------------ A. static scan
def static_scan(path):
    src = open(path).read(); tree = ast.parse(src)
    data_calls = {'load', 'params', 'open'}
    res = {'module_level_data': [], 'in_function_data': [], 'frame_or_gc': [], 'file_literals': []}
    for m in re.finditer(r"(em\.json|van415\.json|em_raw\.json)", src):
        res['file_literals'].append(src.count('\n', 0, m.start()) + 1)
    def callname(n):
        f = n.func
        return f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else '')
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and callname(sub) in data_calls:
                    fn = node.name
                    res['in_function_data'].append((fn, callname(sub), sub.lineno))
                if isinstance(sub, ast.Call) and callname(sub) in ('stack', '_getframe', 'currentframe', 'get_objects', 'globals'):
                    res['frame_or_gc'].append((node.name, callname(sub), sub.lineno))
        elif isinstance(node, ast.If) and 'main' in ast.unparse(node.test):
            continue
        else:
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and callname(sub) in data_calls:
                    res['module_level_data'].append((ast.unparse(node)[:90], sub.lineno))
    for nm in ('inspect', 'gc', 'ctypes', 'subprocess', 'pickle', 'urllib', 'requests'):
        if re.search(r'^\s*(import|from)\s+.*\b%s\b' % nm, src, re.M):
            res['frame_or_gc'].append(('import', nm, 0))
    return res


# ------------------------------------------------------------------ B. child processes
def _harness_like(f, d, ts):
    out = {}
    for t in ts:                      # the local name `d` (full history) mimics harness2.evaluate
        P = f(d[:t], d[t]['date'])
        out[t] = sorted(int(x) for x in P)
    return out


def _perturb_files(cut_date, seed, outdir):
    import numpy as np
    os.makedirs(outdir, exist_ok=True)
    rng = np.random.default_rng(seed); paths = {}
    em = json.load(open(DATA['EM'])); van = json.load(open(DATA['VAN'])); raw = json.load(open(DATA['EM_RAW']))
    for r in em:
        if r['date'] >= cut_date:
            m = sorted(int(x) for x in rng.choice(33, 7, replace=False) + 1)
            r['main'] = m; r['order'] = [int(x) for x in rng.permutation(m)]; r['extra'] = int(rng.integers(1, 7))
            r['deposits'] = float(rng.uniform(5e4, 3e5))
            r['tiers'] = {k: [float(rng.uniform(1, 2000)), int(rng.integers(0, 9000))] for k in r['tiers']}
    for r in van:
        if r['date'] >= cut_date:
            m = sorted(int(x) for x in rng.choice(22, 11, replace=False) + 1)
            r['main'] = m; r['order'] = [int(x) for x in rng.permutation(m)]
    for r in raw:
        if r['date'] >= cut_date and r.get('raw'):
            m = [str(int(x)) for x in rng.choice(33, 7, replace=False) + 1]
            r['raw']['Zrebovanie'] = m; r['raw']['ZrebovanieAdd'] = str(int(rng.integers(1, 7)))
            r['raw']['TabulkaVyhier'] = None; r['raw']['Jackpot'] = None
    for key, obj in (('EM', em), ('VAN', van), ('EM_RAW', raw)):
        p = os.path.join(outdir, os.path.basename(DATA[key])); json.dump(obj, open(p, 'w')); paths[os.path.realpath(DATA[key])] = p
    return paths


def child(spec):
    """spec = (agent, fname, game, mode, ts, seed). Fresh interpreter (spawn, max_tasks_per_child=1)."""
    agent, fname, game, mode, ts, seed = spec
    setup_paths()
    import builtins, io
    log = {'opened_during_f': [], 'unredirected_real_data': []}
    state = {'in_f': False}
    real_paths = {os.path.realpath(p) for p in DATA.values()}

    def hook(event, args):
        if event == 'open' and state['in_f'] and args and isinstance(args[0], (str, bytes)):
            p = os.path.realpath(os.fsdecode(args[0]))
            if p.endswith('.json'):
                log['opened_during_f'].append(p.replace(RUN + '/', ''))
            if mode != 'real' and p in real_paths:
                log['unredirected_real_data'].append(p)
    sys.addaudithook(hook)
    t0 = time.time()
    if mode == 'real':
        d = json.load(open(DATA[game]))
        f = get_formula(agent, fname)
        def fw(past, date):
            state['in_f'] = True
            try: return f(past, date)
            finally: state['in_f'] = False
        preds = _harness_like(fw, d, ts)
        log['opened_during_f'] = sorted(set(log['opened_during_f']))
        return {'spec': spec[:4], 'preds': preds, 'log': log, 'sec': round(time.time() - t0, 1)}
    # perturb + poison: one t per process
    t = ts[0]
    d_real = json.load(open(DATA[game]))
    cut = d_real[t]['date']
    paths = _perturb_files(cut, seed, os.path.join(SCRATCH, 'pert_%s_%s_%d' % (agent, fname, t)))
    orig = builtins.open

    def ropen(file, *a, **k):
        try:
            if isinstance(file, (str, bytes, os.PathLike)):
                p = os.path.realpath(os.fsdecode(file))
                if p in paths:
                    file = paths[p]
        except Exception:
            pass
        return orig(file, *a, **k)
    builtins.open = ropen; io.open = ropen
    d = json.load(open(DATA[game]))                   # now the perturbed history (draws >= t are random)
    assert d[:t] == d_real[:t]                         # the past is untouched
    f = get_formula(agent, fname)                      # module imported under the perturbed world
    def fw(past, date):
        state['in_f'] = True
        try: return f(past, date)
        finally: state['in_f'] = False
    p1 = _harness_like(fw, d, [t])[t]
    err = None
    try:
        fw(d, '2027-01-02')                             # poison: feed the whole (fake) future first
        p2 = _harness_like(fw, d, [t])[t]
    except Exception as e:                              # a formula may legitimately refuse len(past)==len(d)
        p2, err = None, repr(e)
    log['opened_during_f'] = sorted(set(log['opened_during_f']))
    return {'spec': spec[:4], 't': t, 'perturbed_pred': p1, 'poison_pred': p2, 'poison_error': err,
            'target_changed': d[t]['main'] != d_real[t]['main'], 'log': log, 'sec': round(time.time() - t0, 1)}


def main():
    import concurrent.futures as cf, multiprocessing as mp
    t0 = time.time()
    nd = {'EM': len(json.load(open(DATA['EM']))), 'VAN': len(json.load(open(DATA['VAN'])))}
    items = [(a, f, g, 'formula') for a, f, g, _ in FORMULAS] + [(a, f, g, k) for a, f, g, k in CONTROLS]
    specs = []
    for i, (a, f, g, kind) in enumerate(items):
        ts = sample_ts(g, nd[g])
        specs.append((a, f, g, 'real', ts, 0))
        for t in ts:
            specs.append((a, f, g, 'perturb', [t], [2811, 77, i, t]))
    heavy = lambda s: (s[0], s[1]) in (('S5', 'F1'), ('S5', 'F3'), ('S1', 'F1'), ('S2', 'F1'), ('S2', 'F2'), ('S2', 'F3'))
    specs.sort(key=lambda s: (not heavy(s), -s[4][-1]))
    out = []
    with cf.ProcessPoolExecutor(4, mp_context=mp.get_context('spawn'), max_tasks_per_child=1) as ex:
        for r in ex.map(child, specs):
            out.append(r)
    # assemble
    report = {'sampled_t': {g: sample_ts(g, nd[g]) for g in nd}, 'items': [], 'static': {}}
    for a in ('S1', 'S2', 'S3', 'S4', 'S5'):
        report['static'][a] = static_scan(os.path.join(RUN, 'agents', a + '.py'))
    for a, f, g, kind in items:
        real = next(r for r in out if r['spec'] == (a, f, g, 'real'))
        pert = [r for r in out if r['spec'] == (a, f, g, 'perturb')]
        rows = []
        for r in sorted(pert, key=lambda r: r['t']):
            rp = real['preds'][r['t']]
            rows.append({'t': r['t'], 'real': rp, 'perturbed': r['perturbed_pred'], 'poison': r['poison_pred'],
                         'same_perturbed': r['perturbed_pred'] == rp, 'same_poison': r['poison_pred'] == rp,
                         'poison_error': r['poison_error'], 'unredirected_real_data': r['log']['unredirected_real_data']})
        n_bad = sum((not x['same_perturbed']) or (x['poison'] is not None and not x['same_poison']) for x in rows)
        report['items'].append({'agent': a, 'formula': f, 'game': g, 'kind': kind, 'n_t': len(rows),
                                'n_changed': n_bad, 'leak_detected': n_bad > 0,
                                'files_opened_inside_f': real['log']['opened_during_f'], 'rows': rows,
                                'seconds_real': real['sec']})
        print(a, f, g, kind, 'changed %d/%d' % (n_bad, len(rows)), 'files in f:', real['log']['opened_during_f'], flush=True)
    ctrl = [x for x in report['items'] if x['kind'] == 'peek']
    report['positive_controls_all_caught'] = all(x['leak_detected'] for x in ctrl)
    report['negative_control_passed'] = not next(x for x in report['items'] if x['kind'] == 'legit')['leak_detected']
    report['formulas_with_leak'] = [(x['agent'], x['formula']) for x in report['items'] if x['kind'] == 'formula' and x['leak_detected']]
    # how the harness scores the peeking controls (shows what a leak would look like)
    setup_paths()
    from harness2 import evaluate
    import redteam_pc as pc
    report['control_scores'] = {}
    for nm, g in (('PC1_modcache', 'EM'), ('PC4_fullfreq', 'EM'), ('PC5_offbyone', 'EM'), ('PC0_legit', 'EM')):
        r = evaluate(getattr(pc, nm), g, nm)
        report['control_scores'][nm] = {'mean_hits': r['mean_hits'], 'expected': r['expected'], 'p_upper': r['p_upper']}
        print('score', nm, round(r['mean_hits'], 4), '%.3g' % r['p_upper'], flush=True)
    report['seconds'] = round(time.time() - t0, 1)
    dump(report, os.path.join(RUN, 'redteam_leakage.json'))
    print('positive controls caught:', report['positive_controls_all_caught'], ' negative passed:', report['negative_control_passed'],
          ' formulas with leak:', report['formulas_with_leak'], report['seconds'], 's')


if __name__ == '__main__':
    main()
