"""Same analysis for every TIPOS number game (except Keno) + expected value at current jackpots.
Usage: python3 -I multi.py <data_dir> <extra_vyplata_results.json> <out.json>
"""
import json, sys, math, os, datetime
import numpy as np

DD, EVR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
rng = np.random.default_rng(42)
C = math.comb

def eur(s):
    if s is None: return 0.0
    s = str(s).replace('€', '').replace('\xa0', '').replace(' ', '').replace(',', '.')
    try: return float(s)
    except ValueError: return 0.0

def load(name):
    p = os.path.join(DD, name)
    return [r for r in json.load(open(p)) if r['raw']] if os.path.exists(p) else []

# ---------------- generic number-pool analysis ----------------
def analyse_pool(draws, n, k, label, dates):
    T = len(draws)
    M = np.zeros((T, n), int)
    for i, d in enumerate(draws): M[i, np.array(d) - 1] = 1
    f = M.sum(0); E = T * k / n; sd = math.sqrt(T * (k / n) * (1 - k / n))
    chi = float(((f - E) ** 2 / E).sum())
    sims = 3000; sc = np.empty(sims); smax = np.empty(sims)
    for s in range(sims):
        picks = np.argsort(rng.random((T, n)), axis=1)[:, :k]
        ff = np.bincount(picks.ravel(), minlength=n); sc[s] = ((ff - E) ** 2 / E).sum(); smax[s] = ff.max()
    order = np.argsort(-f)
    # walk-forward backtest
    start = max(30, T // 10)
    var1 = k * (k / n) * ((n - k) / n) * ((n - k) / (n - 1))
    zf = lambda v: (v - v.mean()) / (v.std() + 1e-9)
    def tb(t): return np.random.default_rng(t).random(n) * 1e-9
    strategies = {
        'formula': lambda t: np.argsort(-(0.5 * zf(M[:t].sum(0).astype(float)) + 0.35 * zf(M[max(0, t - 52):t].sum(0).astype(float)) + 0.15 * zf(M[max(0, t - 20):t].sum(0).astype(float)) + tb(t)))[:k],
        'hot_all': lambda t: np.argsort(-(M[:t].sum(0) + tb(t)))[:k],
        'hot_52': lambda t: np.argsort(-(M[max(0, t - 52):t].sum(0) + tb(t)))[:k],
        'hot_20': lambda t: np.argsort(-(M[max(0, t - 20):t].sum(0) + tb(t)))[:k],
        'cold_all': lambda t: np.argsort(M[:t].sum(0) + tb(t))[:k],
        'repeat_last': lambda t: np.nonzero(M[t - 1])[0][:k],
    }
    # overdue needs last-seen index
    last_seen = np.full((T + 1, n), -1)
    for i in range(T):
        last_seen[i + 1] = last_seen[i]; last_seen[i + 1, M[i] == 1] = i
    strategies['overdue'] = lambda t: np.argsort(-((t - last_seen[t]) + tb(t)))[:k]
    third = start + 2 * (T - start) // 3
    bt = {}
    for name, fn in strategies.items():
        h = np.array([M[t, fn(t)].sum() for t in range(start, T)])
        nd = len(h); exp = nd * k * k / n
        z = (h.sum() - exp) / math.sqrt(nd * var1)
        hl = h[third - start:]; nl = len(hl); zl = (hl.sum() - nl * k * k / n) / math.sqrt(nl * var1)
        bt[name] = {'mean': float(h.mean()), 'z': float(z), 'p': float(0.5 * math.erfc(z / math.sqrt(2))), 'z_last_third': float(zl)}
    pick = sorted((strategies['formula'](T) + 1).tolist())
    ranking = (np.argsort(-(0.5 * zf(M.sum(0).astype(float)) + 0.35 * zf(M[-52:].sum(0).astype(float)) + 0.15 * zf(M[-20:].sum(0).astype(float)) + tb(T))) + 1).tolist()
    return {'label': label, 'draws': T, 'from': dates[0], 'to': dates[-1], 'n': n, 'k': k,
            'freq': f.tolist(), 'expected': E, 'sd': sd,
            'top': [{'n': int(i + 1), 'c': int(f[i])} for i in order[:k]],
            'bottom': [{'n': int(i + 1), 'c': int(f[i])} for i in order[::-1][:3]],
            'chi': chi, 'p_chi': float((sc >= chi).mean()), 'p_max': float((smax >= f.max()).mean()),
            'random_mean_hits': k * k / n, 'backtest_from': dates[start], 'backtest': bt,
            'last_third_from': dates[third], 'formula_pick': pick, 'ranking': ranking}

def analyse_extra(vals, m, label):
    v = np.array(vals); T = len(v)
    f = np.bincount(v.ravel(), minlength=m + 1)[1:]
    j = v.shape[1] if v.ndim > 1 else 1
    E = T * j / m
    chi = float(((f - E) ** 2 / E).sum())
    sims = 3000; sc = np.empty(sims)
    for s in range(sims):
        if j == 1: ff = np.bincount(rng.integers(0, m, T), minlength=m)
        else: ff = np.bincount(np.argsort(rng.random((T, m)), 1)[:, :j].ravel(), minlength=m)
        sc[s] = ((ff - E) ** 2 / E).sum()
    order = np.argsort(-f)
    return {'label': label, 'freq': f.tolist(), 'expected': E, 'p_chi': float((sc >= chi).mean()),
            'top': [int(i + 1) for i in order[:j]], 'top_counts': [int(f[i]) for i in order[:j]]}

def joker_digits(rows, label):
    D = np.array(rows)  # T x 6
    T = len(D); out = []
    for pos in range(6):
        f = np.bincount(D[:, pos], minlength=10); E = T / 10
        chi = float(((f - E) ** 2 / E).sum())
        sc = np.array([((np.bincount(rng.integers(0, 10, T), minlength=10) - E) ** 2 / E).sum() for _ in range(3000)])
        out.append({'pos': pos + 1, 'p': float((sc >= chi).mean()), 'top': int(np.argmax(f)), 'min': int(np.argmin(f))})
    return {'label': label, 'draws': T, 'positions': out}

def recent_avg(rows, key_amount, key_count, tiers, last=104):
    res = {}
    for t in tiers:
        v = [r[t][0] for r in rows[-last:] if t in r and r[t][0] > 0]
        res[t] = float(np.mean(v)) if v else 0.0
    return res

def share_factor(lam):
    return (1 - math.exp(-lam)) / lam if lam > 1e-9 else 1.0

R = {}

# ================= LOTO 5 z 35 + JOKER =================
raw = load('l535.json')
d535 = [r for r in raw if len(r['raw'].get('Zrebovanie', [])) == 5]
dates = [r['date'] for r in d535]
main = [sorted(int(x) for x in r['raw']['Zrebovanie']) for r in d535]
pool = analyse_pool(main, 35, 5, 'Loto 5 z 35', dates)
tiers = []
for r in d535:
    tb_ = {t['PocetUhadnutych'].strip(): (eur(t['VyskaVyhry']), int(t['PocetVyhier'] or 0)) for t in r['raw']['TabulkaVyhier']['Loteria']}
    tiers.append(tb_)
dep = np.array([eur(r['raw']['SumOfDeposits']) for r in d535])
jack = np.array([eur(r['raw']['Jackpot']) for r in d535])
avg = recent_avg(tiers, 0, 1, ['4', '3'])
tick = dep[-104:].mean() / 0.60
lower = [tiers[i].get('4', (0, 0))[0] * tiers[i].get('4', (0, 0))[1] + tiers[i].get('3', (0, 0))[0] * tiers[i].get('3', (0, 0))[1] for i in range(len(d535))]
quota = float(np.mean([0.52 * dep[i] - lower[i] for i in range(len(d535) - 104, len(d535))]))
pot535 = jack[-1] + quota
N535 = C(35, 5)
lam = tick / N535
ev535 = pot535 / N535 * share_factor(lam) + C(5, 4) * C(30, 1) / N535 * avg['4'] + C(5, 3) * C(30, 2) / N535 * avg['3']
jhits = [(dates[i], tiers[i]['5'][0], tiers[i]['5'][1]) for i in range(len(d535)) if tiers[i].get('5', (0, 0))[1] > 0]
# break-even jackpot pot for the 0.60 field alone
be535 = (0.60 - (C(5, 4) * C(30, 1) / N535 * avg['4'] + C(5, 3) * C(30, 2) / N535 * avg['3'])) * N535 / share_factor(lam)
R['loto535'] = {'pool': pool, 'price': 0.60, 'jackpot_carry': float(jack[-1]), 'pot_next_est': float(pot535), 'tickets_per_draw': float(tick),
                'avg_prizes': avg, 'ev': float(ev535), 'ev_ratio': float(ev535 / 0.60), 'p_jackpot': 1 / N535, 'break_even_pot': float(be535),
                'jackpot_hits_last': jhits[-8:], 'n_jackpot_hits': len(jhits),
                'share_jack_ge_be': float(np.mean(jack + quota >= be535)), 'max_carry': float(jack.max())}

# JOKER (shared by Loto and Loto 5 z 35) — take it from the Loto 5 z 35 rows (one row per draw)
def _jrows(rows):
    return [r for r in rows if r['raw'].get('ZrebovanieJoker') and len(r['raw']['ZrebovanieJoker']) == 6 and r['raw'].get('SumOfDepositsJoker')]
_byd = {r['date']: r for r in _jrows(load('loto.json'))}   # Joker is drawn with Loto (and Loto 5 z 35)
for r in _jrows(d535): _byd.setdefault(r['date'], r)
jk = [_byd[k] for k in sorted(_byd)]
jdig = [[int(x) for x in r['raw']['ZrebovanieJoker']] for r in jk]
jdates = [r['date'] for r in jk]
jjack = np.array([eur(r['raw'].get('JackpotJoker')) for r in jk])
jdep = np.array([eur(r['raw'].get('SumOfDepositsJoker')) for r in jk])
jwin = []
for r in jk:
    t1 = r['raw']['TabulkaVyhier'].get('Joker', [{}])[0]
    jwin.append((eur(t1.get('VyskaVyhry')), int(t1.get('PocetVyhier') or 0)))
fixed_ev = 3300 * 9e-6 + 330 * 9e-5 + 33 * 9e-4 + 3.30 * 9e-3
fixed_cost = []
RECENT = 6   # sales rise with the jackpot, so use the latest draws for sales and sharing
for r in jk[-RECENT:]:
    tt = r['raw']['TabulkaVyhier'].get('Joker', [])
    fixed_cost.append(sum(eur(x.get('VyskaVyhry')) * max(0, int(x.get('PocetVyhier') or 0)) for x in tt[1:]))
jquota = float(np.mean([0.5 * jdep[-RECENT:][i] - fixed_cost[i] for i in range(len(fixed_cost))]))
jtick = float(jdep[-RECENT:].mean() / 0.60)
jlam = jtick / 1e6
jpot = float(jjack[-1] + jquota)
evj = jpot * 1e-6 * share_factor(jlam) + fixed_ev
be_j = (0.60 - fixed_ev) / (1e-6 * share_factor(jlam))
# history of joker jackpot wins
jwins = [(jdates[i], jwin[i][0], jwin[i][1]) for i in range(len(jk)) if jwin[i][1] > 0]
ev_series = [(jdates[i], float((jjack[i] + jquota) * 1e-6 * share_factor(jlam) + fixed_ev)) for i in range(len(jk))]
R['joker'] = {'price': 0.60, 'jackpot_carry': float(jjack[-1]), 'pot_next_est': jpot, 'quota_per_draw': jquota, 'tickets_per_draw': jtick,
              'share_factor': share_factor(jlam), 'fixed_ev': fixed_ev, 'ev': evj, 'ev_ratio': evj / 0.60, 'break_even_pot': be_j,
              'wins': jwins[-12:], 'n_wins': len(jwins), 'draws': len(jk), 'from': jdates[0],
              'share_draws_ev_positive': float(np.mean([e > 0.60 for _, e in ev_series])),
              'max_carry': float(jjack.max()), 'max_carry_date': jdates[int(np.argmax(jjack))],
              'digits': joker_digits(jdig, 'JOKER'),
              'ev_series': ev_series[-400:], 'jackpot_series': [(jdates[i], float(jjack[i])) for i in range(len(jk))][-400:]}
# combined bundle: cheapest legal Joker = 1 field Loto 5 z 35 + Joker
R['bundle'] = {'cost': 1.20, 'ev': float(ev535 + evj), 'ev_ratio': float((ev535 + evj) / 1.20)}

# ================= LOTO (6/49, two draws) =================
raw = load('loto.json')
dl = [r for r in raw if len(r['raw'].get('ZrebovanieTah1', [])) == 6]
dates = [r['date'] for r in dl]
m1 = [sorted(int(x) for x in r['raw']['ZrebovanieTah1']) for r in dl]
m2 = [sorted(int(x) for x in r['raw']['ZrebovanieTah2']) for r in dl if len(r['raw'].get('ZrebovanieTah2', [])) == 6]
pool1 = analyse_pool(m1, 49, 6, 'Loto, 1. ťah', dates)
N49 = C(49, 6)
lt = []
for r in dl:
    t1 = {}; t2 = {}
    for t in r['raw']['TabulkaVyhier']['Loteria']:
        key = t['PocetUhadnutych'].replace(' ', '')
        t1[key] = (eur(t['VyskaVyhryTah1']), int(t['PocetVyhierTah1'] or 0)); t2[key] = (eur(t['VyskaVyhryTah2']), int(t['PocetVyhierTah2'] or 0))
    lt.append((t1, t2))
ldep = np.array([eur(r['raw']['SumOfDeposits']) for r in dl])
ljack = np.array([eur(r['raw']['Jackpot']) for r in dl])
P49 = {'6': 1 / N49, '5+1': 6 / N49, '5': 252 / N49, '4': C(6, 4) * C(43, 2) / N49,
       '3+1': C(6, 3) * C(42, 2) / N49, '3': C(6, 3) * C(42, 3) / N49, '2+1': C(6, 2) * C(42, 3) / N49}
a1 = {k: float(np.mean([x[0][k][0] for x in lt[-104:] if k in x[0] and x[0][k][0] > 0] or [0])) for k in ['5+1', '5', '4', '3+1', '3', '2+1']}
a2 = {k: float(np.mean([x[1][k][0] for x in lt[-104:] if k in x[1] and x[1][k][0] > 0] or [0])) for k in ['5+1', '5', '4', '3+1', '3', '2+1']}
ltick = ldep[-104:].mean() / 1.20
llam = ltick / N49
evl = (ljack[-1]) / N49 * share_factor(llam) + 500000 / N49 * share_factor(llam) + sum(P49[k] * (a1[k] + a2[k]) for k in a1)
R['loto'] = {'pool': pool1, 'price': 1.20, 'jackpot': float(ljack[-1]), 'ev': float(evl), 'ev_ratio': float(evl / 1.20), 'p_jackpot': 1 / N49,
             'avg1': a1, 'avg2': a2, 'tickets_per_draw': float(ltick)}

# ================= EUROMILIÓNY (7/33 + 1/6) =================
def do_em():
    global R
    raw = load('em.json')
    de = [r for r in raw if len(r['raw'].get('Zrebovanie', [])) == 7 and r['raw'].get('ZrebovanieAdd')
          and max(int(x) for x in r['raw']['Zrebovanie']) <= 33 and int(r['raw']['ZrebovanieAdd']) <= 6]
    dates = [r['date'] for r in de]
    poolE = analyse_pool([sorted(int(x) for x in r['raw']['Zrebovanie']) for r in de], 33, 7, 'Euromilióny', dates)
    exE = analyse_extra([[int(r['raw']['ZrebovanieAdd'])] for r in de], 6, 'Euromilióny powerball')
    N33 = C(33, 7) * 6
    et = [{t['PocetUhadnutych'].replace(' ', ''): (eur(t['VyskaVyhry']), int(t['PocetVyhier'] or 0)) for t in r['raw']['TabulkaVyhier']['Loteria']} for r in de]
    def pem(m, b):
        pm = C(7, m) * C(26, 7 - m) / C(33, 7)
        return pm * (1 / 6 if b else 5 / 6)
    keysE = {'7+1': (7, 1), '7': (7, 0), '6+1': (6, 1), '6': (6, 0), '5+1': (5, 1), '5': (5, 0), '4+1': (4, 1), '4': (4, 0), '3+1': (3, 1), '2+1': (2, 1)}
    aE = {k: float(np.mean([x[k][0] for x in et[-104:] if k in x and x[k][0] > 0] or [0])) for k in keysE if k != '7+1'}
    jE = eur(de[-1]['raw']['Jackpot'])
    evE = jE * pem(7, 1) + sum(pem(*keysE[k]) * aE[k] for k in aE)
    R['euromiliony'] = {'pool': poolE, 'extra': exE, 'price': 1.50, 'jackpot': jE, 'p_jackpot': pem(7, 1), 'ev_upper': float(evE), 'ev_ratio': float(evE / 1.5), 'avg': aE}
    R['em_joker'] = {'price': 0.50, 'ev': 20000e-6 + 500 * 9e-6 + 100 * 9e-5 + 10 * 9e-4 + 3.5 * 9e-3 + 2 * 9e-2}
    R['em_joker']['ev_ratio'] = R['em_joker']['ev'] / 0.50

if load('em.json'):
    do_em()

# ================= EUROJACKPOT (5/50 + 2/12, since 25.03.2022) =================
def do_ej():
    global R
    raw = load('ej.json')
    dj = [r for r in raw if r['date'] >= '2022-03-25' and len(r['raw'].get('Zrebovanie', [])) == 5 and len(r['raw'].get('ZrebovanieAdd', [])) == 2]
    dates = [r['date'] for r in dj]
    poolJ = analyse_pool([sorted(int(x) for x in r['raw']['Zrebovanie']) for r in dj], 50, 5, 'Eurojackpot', dates)
    exJ = analyse_extra([sorted(int(x) for x in r['raw']['ZrebovanieAdd']) for r in dj], 12, 'Eurojackpot euročísla')
    NJ = C(50, 5) * C(12, 2)
    jt = [{t['PocetUhadnutych'].replace(' ', ''): eur(t['VyskaVyhry']) for t in r['raw']['TabulkaVyhier']['Loteria']} for r in dj]
    def pj(m, b):
        return C(5, m) * C(45, 5 - m) / C(50, 5) * C(2, b) * C(10, 2 - b) / C(12, 2)
    keysJ = ['5+1', '5+0', '4+2', '4+1', '3+2', '4+0', '2+2', '3+1', '3+0', '1+2', '2+1']
    aJ = {k: float(np.mean([x[k] for x in jt[-104:] if x.get(k, 0) > 0] or [0])) for k in keysJ}
    jJ = eur(dj[-1]['raw']['Jackpot'])
    evJ = jJ * pj(5, 2) + sum(pj(int(k[0]), int(k[2])) * aJ[k] for k in keysJ)
    R['eurojackpot'] = {'pool': poolJ, 'extra': exJ, 'price': 2.00, 'jackpot': jJ, 'p_jackpot': pj(5, 2), 'ev_upper': float(evJ), 'ev_ratio': float(evJ / 2.0), 'avg': aJ}
    R['ej_joker'] = {'price': 1.00, 'ev': 50000e-6 + 5000 * 9e-6 + 500 * 9e-5 + 50 * 9e-4 + 5 * 9e-3 + 3 * 9e-2}
    R['ej_joker']['ev_ratio'] = R['ej_joker']['ev'] / 1.0

if load('ej.json'):
    do_ej()

# ================= VŠETKO ALEBO NIČ (11/22) =================
raw = load('van.json')
dv = [r for r in raw if len(r['raw'].get('Zrebovanie', [])) == 11]
dates = [r['date'] for r in dv]
poolV = analyse_pool([sorted(int(x) for x in r['raw']['Zrebovanie']) for r in dv], 22, 11, 'Všetko alebo nič', dates)
N22 = C(22, 11)
pv = {h: C(11, h) * C(11, 11 - h) / N22 for h in range(12)}
prize = {11: 100000, 10: 200, 9: 20, 8: 3, 3: 3, 2: 20, 1: 200, 0: 100000}
evV = sum(pv[h] * prize.get(h, 0) for h in range(12))
top_wins = sum(1 for r in dv for t in r['raw']['TabulkaVyhier']['Loteria'] if t['PocetUhadnutych'].strip() in ('11', '0') and int(t['PocetVyhier'] or 0) > 0)
vdep = np.array([eur(r['raw']['SumOfDeposits']) for r in dv])
R['van'] = {'pool': poolV, 'price': 1.50, 'ev': evV, 'ev_ratio': evV / 1.5, 'p_top': pv[11] + pv[0], 'top_wins': top_wins,
            'top_expected': float((vdep / 1.5).sum() * (pv[11] + pv[0])), 'draws': len(dv)}

# ================= EXTRA VÝPLATA (from earlier run) =================
ER = json.load(open(EVR))
R['extra'] = {'price': 1.50, 'ev': ER['economics']['payout_ratio'] * 1.5, 'ev_ratio': ER['economics']['payout_ratio'], 'p_jackpot': ER['odds']['6+1'],
              'p_chi_main': ER['freq']['p_chi_main']}

json.dump(R, open(OUT, 'w'), ensure_ascii=False, indent=1)
print('ok', file=sys.stderr)
