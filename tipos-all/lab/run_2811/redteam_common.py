"""Red team (28.11.2026): shared registry of the 15 primary formulas + helpers.
Nothing here runs an agent's main(); agent modules are imported fresh in child processes.
"""
import os, sys, json, importlib
from math import comb

RUN = '/home/user/Mobil/tipos-all/lab/run_2811'
AGENTS = os.path.join(RUN, 'agents')
DATA = {'EM': os.path.join(RUN, 'data', 'em.json'), 'VAN': os.path.join(RUN, 'data', 'van415.json'),
        'EM_RAW': os.path.join(RUN, 'data', 'em_raw.json')}
SCRATCH = '/tmp/claude-0/-home-user-Mobil/719827ba-fdad-545b-9011-edbf1daf2521/scratchpad/redteam'

# (agent, formula, game, rule name in aggregate2.json)
FORMULAS = [
    ('S1', 'F1', 'EM', 'S1_F1'), ('S1', 'F2', 'EM', 'S1_F2'), ('S1', 'F3', 'VAN', 'S1_F3'),
    ('S2', 'F1', 'EM', 'S2_F1'), ('S2', 'F2', 'EM', 'S2_F2'), ('S2', 'F3', 'EM', 'S2_F3'),
    ('S3', 'F1', 'VAN', 'F1'), ('S3', 'F2', 'EM', 'F2'), ('S3', 'F3', 'EM', 'F3'),
    ('S4', 'F1', 'EM', 'S4_F1'), ('S4', 'F2', 'EM', 'S4_F2'), ('S4', 'F3', 'VAN', 'S4_F3'),
    ('S5', 'F1', 'EM', 'S5_F1'), ('S5', 'F2', 'EM', 'S5_F2'), ('S5', 'F3', 'EM', 'S5_F3'),
]


def setup_paths():
    sys.dont_write_bytecode = True
    for p in (RUN, AGENTS):
        if p not in sys.path:
            sys.path.insert(0, p)


def get_formula(agent, fname):
    """Fresh import of the agent module (call in a fresh process) and return f(past, date)."""
    setup_paths()
    if agent.startswith('PC'):
        m = importlib.import_module('redteam_pc')
        return getattr(m, fname)
    m = importlib.import_module(agent)
    if agent == 'S2':
        m._ENG.clear()
        return m.make_f('EM', fname)
    if agent == 'S4' and fname == 'F1':
        m._LS.clear()
    return getattr(m, fname)


def pmf(game):
    N, K, T = (22, 11, 11) if game == 'VAN' else (33, 7, 7)
    return [comb(T, k) * comb(N - T, K - k) / comb(N, K) for k in range(T + 1)], N, K, T


def holm(ps):
    m = len(ps); order = sorted(range(m), key=lambda i: ps[i]); out = [0.0] * m; run = 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (m - k) * ps[i])); out[i] = run
    return out


def dump(obj, path):
    def clean(o):
        import numpy as np
        if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)): return [clean(v) for v in o]
        if isinstance(o, np.integer): return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, np.bool_): return bool(o)
        if isinstance(o, np.ndarray): return clean(o.tolist())
        return o
    with open(path, 'w') as fh:
        json.dump(clean(obj), fh, ensure_ascii=False, indent=1)
