"""Red team positive / negative controls for the leakage tests (EM unless named _VAN).
PC1..PC5 deliberately peek at the future in the ways the audit looks for; PC0 is a legitimate rule.
"""
import sys, os, json, inspect
import numpy as np
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2811')
from harness2 import load, params

EMPATH = '/home/user/Mobil/tipos-all/lab/run_2811/data/em.json'
_FULL_EM = load('EM')           # module-level cache built from the FULL history (as S1/S4/S5 do with params())
_FULL_VAN = load('VAN')
_CNT_FULL = np.zeros(33)
for r in _FULL_EM:
    _CNT_FULL[np.array(r['main']) - 1] += 1


def _top(score, T=7):
    score = np.asarray(score, float)
    return sorted(int(i) + 1 for i in np.lexsort((np.arange(len(score)), -score))[:T])


def PC0_legit(past, date):          # legitimate: hot numbers over past only
    c = np.zeros(33)
    for r in past:
        c[np.array(r['main']) - 1] += 1
    return _top(c)


def PC1_modcache(past, date):       # gross leak: module-level full data, returns the draw itself
    return _FULL_EM[len(past)]['main']


def PC1_VAN(past, date):
    return _FULL_VAN[len(past)]['main']


def PC2_fileread(past, date):       # reads em.json directly inside f and finds the draw by its date
    D = json.load(open(EMPATH))
    return next(r['main'] for r in D if r['date'] == date)


def PC3_frame(past, date):          # inspects the caller's frame (the harness local `d`)
    for fr in inspect.stack()[1:]:
        d = fr.frame.f_locals.get('d')
        if isinstance(d, list) and len(d) > len(past) and isinstance(d[0], dict):
            return d[len(past)]['main']
    return past[-1]['main']


def PC4_fullfreq(past, date):       # weak leak: frequencies over the full history (module cache)
    return _top(_CNT_FULL)


def PC5_offbyone(past, date):       # weak leak: frequencies over draws up to AND INCLUDING the evaluated one
    d = params('EM')[0]
    c = np.zeros(33)
    for r in d[:len(past) + 1]:
        c[np.array(r['main']) - 1] += 1
    return _top(c)
