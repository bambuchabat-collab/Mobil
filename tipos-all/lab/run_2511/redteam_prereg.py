"""Red team, part 3: pre-registration audit (python3 -I -B). Read-only git commands, no commits.
- prereg 'Written' timestamp vs prereg/code/result mtimes and first git commit of each file;
- were any agent files modified after their first commit (git log --name-status)?
- bytecode forensics: committed agents/__pycache__/*.pyc vs current sources (was an older code version imported?);
- data/harness hashes quoted in preregs; A6 side data (EV / Loto 5z35) vs run_2311 and draw-day schedule;
- A1.py was changed after its first commit (R3 sampler): re-evaluate R3 with the pre-change code.
Writes redteam_prereg.json."""
import sys, os, re, json, subprocess, hashlib, marshal, datetime as dt
sys.dont_write_bytecode = True
RUN = '/home/user/Mobil/tipos-all/lab/run_2511'
REPO = '/home/user/Mobil'
REL = 'tipos-all/lab/run_2511'
sys.path.insert(0, RUN)
import numpy as np
from harness import evaluate, DRAWS


def git(*a):
    return subprocess.run(['git', '-C', REPO] + list(a), capture_output=True, text=True, check=True).stdout


def mtime(p):
    return dt.datetime.fromtimestamp(os.stat(p).st_mtime, dt.timezone.utc)


# history of every file under run_2511
log = git('log', '--reverse', '--format=@@%h %cI', '--name-status', '--', REL)
first_commit, changes = {}, {}
cur = None
for line in log.splitlines():
    if line.startswith('@@'):
        h, ts = line[2:].split(); cur = (h, dt.datetime.fromisoformat(ts)); continue
    if not line.strip(): continue
    st, path = line.split('\t', 1)
    first_commit.setdefault(path, cur)
    changes.setdefault(path, []).append((st, cur[0], cur[1].isoformat()))

PAT_ISO = re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z')
PAT_DATE = re.compile(r'\w{3} \w{3} +(\d+) (\d{2}:\d{2}:\d{2}) UTC (\d{4})')
rows = []
for i in range(1, 11):
    a = f'A{i}'
    pre = os.path.join(RUN, 'agents', f'{a}_prereg.md'); py = os.path.join(RUN, 'agents', f'{a}.py')
    js = os.path.join(RUN, 'agents', f'{a}.json')
    txt = open(pre).read()
    m = PAT_DATE.search(txt)
    if m:
        written = dt.datetime.strptime(f'2026-11-{int(m.group(1)):02d} {m.group(2)}', '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc)
    else:
        written = dt.datetime.fromisoformat(PAT_ISO.search(txt).group(1)).replace(tzinfo=dt.timezone.utc)
    fc = {k: first_commit.get(f'{REL}/agents/{a}{k}') for k in ('_prereg.md', '.py', '.json')}
    r = {'agent': a, 'prereg_written': written.isoformat(), 'prereg_mtime': mtime(pre).isoformat(),
         'py_mtime': mtime(py).isoformat(), 'json_mtime': mtime(js).isoformat(),
         'git_first_commit': {k: (v[0], v[1].isoformat()) for k, v in fc.items()},
         'git_changes': {k: changes.get(f'{REL}/agents/{a}{k}') for k in ('_prereg.md', '.py', '.json')}}
    r['written_before_result'] = written < mtime(js)
    r['prereg_file_before_result'] = mtime(pre) < mtime(js)
    r['prereg_committed_not_after_result'] = fc['_prereg.md'][1] <= fc['.json'][1]
    r['prereg_unchanged_after_commit'] = len(changes[f'{REL}/agents/{a}_prereg.md']) == 1
    r['code_unchanged_after_commit'] = len(changes[f'{REL}/agents/{a}.py']) == 1
    r['seconds_prereg_to_result'] = round((mtime(js) - written).total_seconds(), 1)
    rows.append(r)

# working tree == HEAD for the study files?
dirty = git('status', '--porcelain', '--', REL)

# ---------------- bytecode forensics ----------------
pyc = {}
for a, commit in (('A5', 'e1f2beb'), ('A9', 'e1f2beb'), ('A4', 'cb6e0d0'), ('A10', '5181679')):
    raw = subprocess.run(['git', '-C', REPO, 'show', f'{commit}:{REL}/agents/__pycache__/{a}.cpython-313.pyc'],
                         capture_output=True, check=True).stdout
    flags = int.from_bytes(raw[4:8], 'little')
    src_mtime = int.from_bytes(raw[8:12], 'little'); src_size = int.from_bytes(raw[12:16], 'little')
    code = marshal.loads(raw[16:])
    path = os.path.join(RUN, 'agents', a + '.py')
    cur_src = open(path, 'rb').read()
    same_code = compile(cur_src, code.co_filename, 'exec') == code
    pyc[a] = {'commit': commit, 'pyc_flags': flags,
              'pyc_source_mtime': dt.datetime.fromtimestamp(src_mtime, dt.timezone.utc).isoformat(),
              'pyc_source_size': src_size, 'current_size': len(cur_src),
              'current_mtime_s': int(os.stat(path).st_mtime), 'code_object_identical_to_current': bool(same_code)}
raw = subprocess.run(['git', '-C', REPO, 'show', f'47550c6:{REL}/__pycache__/harness.cpython-313.pyc'],
                     capture_output=True, check=True).stdout
hcode = marshal.loads(raw[16:])
pyc['harness'] = {'code_object_identical_to_current': bool(compile(open(os.path.join(RUN, 'harness.py'), 'rb').read(),
                                                                     hcode.co_filename, 'exec') == hcode)}

# ---------------- hashes and side data ----------------
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
hashes = {'van412.json': sha(os.path.join(RUN, 'van412.json')), 'harness.py': sha(os.path.join(RUN, 'harness.py')),
          'claimed_van412_A1_A5': 'ce9a079e488f458befa620ef7695a3c9f01a2e3fbbe02f3229a4d13d807bd73e',
          'claimed_harness_A5': 'a85a1e3e57b1a3113fc0ca37e6e403f8ad3cc2111fb5f302afe98f993427aad4'}
hashes['match'] = (hashes['van412.json'] == hashes['claimed_van412_A1_A5'] and hashes['harness.py'] == hashes['claimed_harness_A5'])
van = json.load(open('/home/user/Mobil/tipos-all/lab/run_2311/data/van.json'))
van_match = all(van[i]['date'] == DRAWS[i]['date'] and sorted(van[i]['main']) == DRAWS[i]['main'] for i in range(len(van)))
ev = json.load(open(os.path.join(RUN, 'agents', 'A6_ev.json')))
ev_old = json.load(open('/home/user/Mobil/tipos-all/lab/run_2311/data/ev.json'))
ev_old_map = {d['date']: sorted(d['main']) for d in ev_old}
ev_mism = [d['date'] for d in ev if d['date'] in ev_old_map and ev_old_map[d['date']] != sorted(d['main'])]
l535 = json.load(open(os.path.join(RUN, 'agents', 'A6_l535.json')))
wd = lambda s: dt.date.fromisoformat(s).weekday()
side = {'van412_first410_equal_run2311_van_json': van_match,
        'ev_draws': len(ev), 'ev_in_run2311': sum(d['date'] in ev_old_map for d in ev), 'ev_mismatch_vs_run2311': ev_mism,
        'ev_not_in_run2311': [d['date'] for d in ev if d['date'] not in ev_old_map],
        'ev_weekdays': dict(sorted({str(k): sum(wd(d['date']) == k for d in ev) for k in range(7)}.items())),
        'ev_last': ev[-1]['date'], 'l535_draws': len(l535), 'l535_last': max(d['date'] for d in l535),
        'l535_weekdays': {str(k): sum(wd(d['date']) == k for d in l535) for k in range(7)},
        'ev_dates_on_or_after_2026-11-24': [d['date'] for d in ev if d['date'] >= '2026-11-24'],
        'l535_dates_on_or_after_2026-11-24': [d['date'] for d in l535 if d['date'] >= '2026-11-24']}

# ---------------- A1 R3 with the pre-change code (first commit e1f2beb) ----------------
old_src = git('show', f'e1f2beb:{REL}/agents/A1.py')
ns = {'__name__': 'rt_A1_old', '__file__': 'A1_old.py'}
exec(compile(old_src, 'A1_old.py', 'exec'), ns)
r_old = evaluate(ns['r3_transition'], 'A1_R3_pre_change')
a1 = json.load(open(os.path.join(RUN, 'agents', 'A1.json')))
r_new = [r for r in a1['rules'] if r['rule'] == 'R3'][0]
a1_change = {'diff': 'R3 sampler: u = rng.random()*total  ->  u = (1-rng.random())*total (open interval at 0); '
                     'removed unused variable inc. No parameter change.',
             'pre_change': {k: float(r_old[k]) for k in ('mean_hits', 'p_mean_lower', 'p_le3')},
             'reported': {k: r_new[k] for k in ('mean_hits', 'p_mean_lower', 'p_le3')}}

MANUAL = {  # line-by-line comparison of each prereg with its code (done by reading; see redteam.md)
    'A1': 'match (R1 late-ball, R2 early balls lags 1..3, R3 Markov order sim N=10000 seed 20261125+t); '
          'R3 sampler edited after first commit (bug-proofing, no parameter change; effect re-evaluated)',
    'A2': 'match (R1 lag-1 residual, R2 phi vs predicted set, R3 exhaustive 352716 partitions + lag-1 autocorr side)',
    'A3': 'match (R1/R2 Laplace Markov orders 1/2, R3 pooled signed run-length hazard cap 6, jitter seed 20251125+t)',
    'A4': 'match (features, lambda=10, IRLS 50/1e-8, refit every 10 from t=30, stumps 100x0.1, min 20, <=16 thr); '
          'target weekday = last date + 1 day (wrong for 2 draws after the 24-25.12 and 3.4 gaps) - pre-registered, not a leak',
    'A5': 'match; reads DRAWS[t]["date"] only (declared in prereg; date is public in advance)',
    'A6': 'match; reads DRAWS[t]["date"] only (declared); other-game draws strictly before the VAN date; R2 = exact complement of R1',
    'A7': 'match (88 candidates, strict-< ties; R2 m0=5.4828 -> image; R3 a0=5.6552 -> highest)',
    'A8': 'match; reads DRAWS[t]["date"] only (declared); Step-1 best-by-#>=9 and best-by-mean picked the SAME combo '
          'PY/UDAY/SEQ, so R1 == R2 (one test counted twice in Holm: conservative)',
    'A9': 'match (half-life 30 alpha0=1; BOCPD H=1/50 Beta(1,1) exact; PL MAP s=0.1 Newton)',
    'A10': 'match (ridge lambda=1 on centred indicators, tier rows < t only; R2 = complement of R1; R3 sign switch)',
}
ok_time = all(r['written_before_result'] and r['prereg_file_before_result'] and r['prereg_committed_not_after_result']
              and r['prereg_unchanged_after_commit'] for r in rows)
OUT = {'timing': rows, 'study_files_dirty_vs_HEAD': dirty.splitlines(), 'pyc_forensics': pyc, 'hashes': hashes,
       'side_data': side, 'A1_code_change': a1_change, 'manual_prereg_vs_code': MANUAL,
       'all_preregs_before_results': ok_time,
       'verdict': ('PREREG OK with minor deviations' if ok_time else 'PREREG PROBLEM')}
json.dump(OUT, open(os.path.join(RUN, 'redteam_prereg.json'), 'w'), indent=1, default=str)
print(json.dumps(OUT, indent=1, default=str))
