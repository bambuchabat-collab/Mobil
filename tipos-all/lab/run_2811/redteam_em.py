"""Red team tasks 3-4: Euromilióny rules/odds/return vs Všetko alebo nič, and checks of the candidate tickets.
Rules from the TIPOS herný plán (článok 25, 26, 34; extract in redteam_rules_extract.txt):
 EM: player picks 7 of 1..33 AND 1 of 1..6; 1.50 EUR per bet; prize pool 50 % of stakes, ALL 10 tiers pari-mutuel
     (shares 20/3/3/3.5/4/4/6.5/17.5/13.5/25 %), jackpot accumulates, guaranteed 1 000 000 EUR; only highest prize per bet.
 VAN: 11 of 22, 1.50 EUR, fixed 200/20/3 EUR, 100 000 EUR shared by all 11- and 0-match winners; pool 50.35 %.
Run: python3 -I redteam_em.py   (writes redteam_em.json)
"""
import sys, os, json, math
from math import comb
import numpy as np
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2811')
from redteam_common import RUN, dump

PRICE = 1.50
JACKPOT_NOW = 1_610_055.0          # EuromilionyJackpot on tipos.sk/loterie/euromiliony, 27.11.2026 (draw 28.11)
TIERS = ['7+1', '7', '6+1', '6', '5+1', '5', '4+1', '4', '3+1', '2+1']
SHARE = dict(zip(TIERS, [0.20, 0.03, 0.03, 0.035, 0.04, 0.04, 0.065, 0.175, 0.135, 0.25]))
KM = {'7+1': (7, 1), '7': (7, 0), '6+1': (6, 1), '6': (6, 0), '5+1': (5, 1), '5': (5, 0), '4+1': (4, 1), '4': (4, 0), '3+1': (3, 1), '2+1': (2, 1)}
EM_TICKET = [1, 5, 9, 16, 17, 21, 27]
VAN_TICKET = [7, 10, 11, 13, 14, 16, 17, 19, 20, 21, 22]
VAN_DATA_TIERS = '/home/user/Mobil/tipos-all/lab/run_2311/data/van.json'   # 410 VAN draws with tiers and bets


def p_main(k):
    return comb(7, k) * comb(26, 7 - k) / comb(33, 7)


def p_tier(t):
    k, b = KM[t]
    return p_main(k) * (1 / 6 if b else 5 / 6)


def os_random_extra():
    while True:                                   # rejection sampling, uniform 1..6
        b = os.urandom(1)[0]
        if b < 252:
            return b % 6 + 1


def main():
    out = {}
    em = json.load(open(os.path.join(RUN, 'data', 'em.json')))
    # ------------------------------------------------ odds (exact)
    P = {t: p_tier(t) for t in TIERS}
    out['odds'] = {
        'C(33,7)': comb(33, 7), 'p_tier': P, 'one_in': {t: 1 / P[t] for t in TIERS},
        'P_any_prize': sum(P.values()), 'P_jackpot': P['7+1'], 'jackpot_one_in': 1 / P['7+1'],
        'P_5_or_more_main': sum(p_main(k) for k in (5, 6, 7)),
    }
    # ------------------------------------------------ realised return, last 2 years
    last = em[-1]['date']; cut = '%d%s' % (int(last[:4]) - 2, last[4:])
    rec = [r for r in em if r['date'] > cut]
    dep = sum(r['deposits'] for r in rec)
    paid = {t: sum(r['tiers'][t][0] * r['tiers'][t][1] for r in rec) for t in TIERS}
    bets = np.array([r['deposits'] / PRICE for r in rec])
    sat = np.array([r['deposits'] / PRICE for r in rec if r['day'].lower() == 'sobota'])
    tiers2_10 = sum(paid[t] for t in TIERS[1:]) / dep
    # mean prize per tier when won, and the "random ticket" EV per bet: P_tier * mean prize | won
    meanprize = {t: float(np.mean([r['tiers'][t][0] for r in rec if r['tiers'][t][1] > 0])) if any(r['tiers'][t][1] > 0 for r in rec) else None for t in TIERS}
    share_won = {t: float(np.mean([r['tiers'][t][1] > 0 for r in rec])) for t in TIERS}
    # theory with Poisson co-winners (random-like ticket): return from tier t per 1 EUR = 0.5*s_t*(1-exp(-lam_t))
    lam = {t: float(sat.mean() * P[t]) for t in TIERS}
    theo = {t: 0.5 * SHARE[t] * (1 - math.exp(-lam[t])) for t in TIERS[1:]}
    l1 = lam['7+1']
    jack_ev_bet = JACKPOT_NOW * P['7+1'] * ((1 - math.exp(-l1)) / l1)
    jack_wins = [(r['date'], r['tiers']['7+1']) for r in em if r['tiers']['7+1'][1] > 0]
    exp_jack_wins = sum(r['deposits'] / PRICE * P['7+1'] for r in em)
    out['return'] = {
        'window': [rec[0]['date'], rec[-1]['date']], 'draws': len(rec), 'deposits_eur': dep,
        'bets_per_draw_mean': float(bets.mean()), 'bets_per_saturday_draw_mean': float(sat.mean()),
        'bets_last_saturday': float([r['deposits'] for r in rec if r['day'].lower() == 'sobota'][-1] / PRICE),
        'paid_share_by_tier': {t: paid[t] / dep for t in TIERS}, 'tiers_2_10_return_per_eur_realised': tiers2_10,
        'tiers_2_10_return_per_eur_theory_poisson': sum(theo.values()), 'theory_by_tier': theo, 'lambda_saturday': lam,
        'mean_prize_when_won': meanprize, 'share_of_draws_with_winner': share_won,
        'jackpot_now': JACKPOT_NOW, 'jackpot_ev_per_bet': jack_ev_bet, 'jackpot_ev_per_eur': jack_ev_bet / PRICE,
        'jackpot_share_factor_E_1_over_1plusX': (1 - math.exp(-l1)) / l1,
        'total_return_per_eur_now': tiers2_10 + jack_ev_bet / PRICE,
        'jackpot_wins_history': jack_wins, 'jackpot_wins_expected_if_random_picks': exp_jack_wins,
        'breakeven_jackpot_eur': (1 - tiers2_10) * PRICE / (P['7+1'] * ((1 - math.exp(-l1)) / l1)),
    }
    # P(prize >= stake), P(prize >= ~20 EUR) for one EM bet using mean prizes
    out['odds']['P_prize_ge_20eur_approx'] = sum(P[t] for t in TIERS if (meanprize[t] or (1e9 if t in ('7+1', '7') else 0)) >= 20)
    out['odds']['min_mean_prize_2+1'] = meanprize['2+1']
    # ------------------------------------------------ VAN for comparison
    N22 = comb(22, 11)
    pv = {k: comb(11, k) * comb(11, 11 - k) / N22 for k in range(12)}
    prize = {11: 100000, 10: 200, 9: 20, 8: 3, 3: 3, 2: 20, 1: 200, 0: 100000}
    van_any = sum(pv[k] for k in prize)
    van_ev = sum(pv[k] * prize[k] for k in prize) / PRICE
    vt = json.load(open(VAN_DATA_TIERS))
    vdep = sum(r['deposits'] for r in vt)
    van_real = sum(pz * w for r in vt for pz, w in r['tiers'].values()) / vdep        # prizes actually won
    van_wins_field = sum(r['wins'] for r in vt) / vdep                                # booked 50.35 % pool
    van_top_real = sum(r['tiers'][k][0] * r['tiers'][k][1] for r in vt for k in ('11', '0')) / vdep
    van_sat_bets = [r['bets'] for r in vt if r['day'].lower() == 'sobota'][-8:]
    out['VAN'] = {'P_any_prize': van_any, 'P_top_11_or_0': pv[11] + pv[0], 'top_one_in': 1 / (pv[11] + pv[0]),
                  'P_prize_ge_20eur': sum(pv[k] for k in (11, 10, 9, 2, 1, 0)), 'return_per_eur_rules_no_sharing': van_ev,
                  'return_per_eur_realised_410_draws': van_real, 'wins_field_ratio': van_wins_field,
                  'top_prize_paid_per_eur_realised': van_top_real, 'realised_window': [vt[0]['date'], vt[-1]['date']],
                  'top_winners_observed_vs_expected': [sum(r['tiers']['11'][1] + r['tiers']['0'][1] for r in vt), sum(r['bets'] for r in vt) * 2 / N22],
                  'bets_last_8_saturdays': van_sat_bets, 'other_top_holders_expected_random_set': float(np.mean(van_sat_bets)) * 2 / N22,
                  'top_ev_per_eur': (pv[11] + pv[0]) * 100000 / PRICE}
    # ------------------------------------------------ EM popularity of numbers / extras from winners counts
    rows = []
    for r in em:
        b = r['deposits'] / PRICE
        rows.append((r, b))
    pop = {}
    for t in ('2+1', '3+1', '4', '4+1', '5'):
        y, X = [], []
        for r, b in rows:
            W = r['tiers'][t][1]; E = b * P[t]
            if W <= 0: continue
            x = np.zeros(1 + 33 + 6); x[0] = 1; x[np.array(r['main'])] = 1.0
            if t.endswith('+1'): x[33 + r['extra']] = 1.0
            y.append(math.log(W / E)); X.append(x)
        X = np.array(X); y = np.array(y)
        lam_r = 1.0; A = X.T @ X + lam_r * np.diag([0] + [1] * 39); beta = np.linalg.solve(A, X.T @ y)
        bm = beta[1:34] - beta[1:34].mean(); be = beta[34:] - beta[34:].mean() if t.endswith('+1') else None
        # split-half stability of the number effects
        h = len(y) // 2; bb = []
        for sl in (slice(0, h), slice(h, None)):
            A2 = X[sl].T @ X[sl] + lam_r * np.diag([0] + [1] * 39); bb.append(np.linalg.solve(A2, X[sl].T @ y[sl])[1:34])
        pop[t] = {'n': len(y), 'beta_main': bm, 'beta_extra': be, 'split_half_corr': float(np.corrcoef(bb[0], bb[1])[0, 1]),
                  'resid_sd': float(np.std(y - X @ beta))}
    # pooled number popularity: standardised average over tiers
    Z = np.mean([pop[t]['beta_main'] / pop[t]['beta_main'].std() for t in pop], axis=0)
    extra_pop = np.mean([np.exp(pop[t]['beta_extra']) for t in ('2+1', '3+1', '4+1')], axis=0)
    rng = np.random.default_rng(2811)
    rand_sets = np.array([rng.choice(33, 7, replace=False) for _ in range(200000)])
    zs = Z[rand_sets].sum(1); s4 = pop['4']['beta_main'][rand_sets].sum(1)
    tk = np.array(EM_TICKET) - 1
    pick_file = os.path.join(RUN, 'redteam_extra_pick.json')      # drawn once with os.urandom, then reused
    if os.path.exists(pick_file):
        extra_pick = json.load(open(pick_file))['extra']
    else:
        extra_pick = os_random_extra(); json.dump({'extra': extra_pick, 'source': 'os.urandom, rejection sampling 1..6'}, open(pick_file, 'w'))
    sums = (rand_sets + 1).sum(1)
    res4 = rand_sets % 4; maxres = np.array([np.bincount(x, minlength=4).max() for x in res4[:50000]])
    out['EM_popularity'] = {
        'per_tier': {t: {'n': v['n'], 'split_half_corr': v['split_half_corr'], 'resid_sd': v['resid_sd']} for t, v in pop.items()},
        'pooled_number_score_z': {i + 1: float(Z[i]) for i in range(33)},
        'most_popular_numbers': [int(i) + 1 for i in np.argsort(-Z)[:10]], 'least_popular_numbers': [int(i) + 1 for i in np.argsort(Z)[:10]],
        'extra_relative_popularity_1_6': [float(x / extra_pop.mean()) for x in extra_pop],
    }
    ticket_z = float(Z[tk].sum())
    out['EM_ticket'] = {
        'numbers': EM_TICKET, 'extra_os_random': extra_pick,
        'extra_os_random_relative_popularity': float(extra_pop[extra_pick - 1] / extra_pop.mean()),
        'all_le_31': all(x <= 31 for x in EM_TICKET), 'P_random_all_le_31': comb(31, 7) / comb(33, 7),
        'n_le_12': sum(x <= 12 for x in EM_TICKET), 'sum': sum(EM_TICKET), 'sum_percentile_random': float((sums <= sum(EM_TICKET)).mean()),
        'residue_mod4_counts': np.bincount(np.array(EM_TICKET) % 4, minlength=4).tolist(),
        'P_random_ge5_same_residue_mod4': float((maxres >= 5).mean()),
        'consecutive_pairs': [[a, b] for a, b in zip(EM_TICKET, EM_TICKET[1:]) if b - a == 1],
        'popularity_score_z_sum': ticket_z, 'popularity_percentile_among_random_sets': float((zs <= ticket_z).mean()),
        'popularity_tier4_log_multiplier': float(pop['4']['beta_main'][tk].sum()),
        'popularity_tier4_percentile': float((s4 <= pop['4']['beta_main'][tk].sum()).mean()),
        'per_number_z': {int(x): float(Z[x - 1]) for x in EM_TICKET},
    }
    # ------------------------------------------------ VAN ticket and complement
    comp = sorted(set(range(1, 23)) - set(VAN_TICKET))
    def runs(s):
        s = sorted(s); best = cur = 1
        for a, b in zip(s, s[1:]):
            cur = cur + 1 if b == a + 1 else 1; best = max(best, cur)
        return best
    n19 = sum(x <= 9 for x in VAN_TICKET); n11 = sum(x <= 11 for x in VAN_TICKET)
    P19 = sum(comb(9, k) * comb(13, 11 - k) for k in range(10) if abs(k - 4.5) >= abs(n19 - 4.5)) / N22
    P11 = sum(comb(11, k) * comb(11, 11 - k) for k in range(12) if abs(k - 5.5) >= abs(n11 - 5.5)) / N22
    rr = np.array([rng.choice(22, 11, replace=False) + 1 for _ in range(100000)])
    rmax = np.array([max(runs(x), runs(sorted(set(range(1, 23)) - set(x.tolist())))) for x in rr[:30000]])
    # empirical: are lopsided partitions (many 1-9 on one side) more played? near-winner counts 10/1 and 9/2
    reg = {}
    for key, ks in (('10_or_1', ('10', '1')), ('9_or_2', ('9', '2')), ('8_or_3', ('8', '3'))):
        kk = int(ks[0]); E1 = 2 * comb(11, kk) * comb(11, 11 - kk) / N22
        y, L1, L2 = [], [], []
        for r in vt:
            W = sum(r['tiers'][k][1] for k in ks); E = r['bets'] * E1
            y.append(math.log((W + 0.5) / E)); m = set(r['main'])
            L1.append(abs(sum(x <= 9 for x in m) - 4.5)); L2.append(abs(sum(x <= 11 for x in m) - 5.5))
        y = np.array(y)
        for nm, L in (('lopsided_1_9', np.array(L1)), ('lopsided_1_11', np.array(L2))):
            X = np.c_[np.ones(len(y)), L]; b, *_ = np.linalg.lstsq(X, y, rcond=None)
            se = np.sqrt(np.sum((y - X @ b) ** 2) / (len(y) - 2) / np.sum((L - L.mean()) ** 2))
            reg.setdefault(key, {})[nm] = {'slope_log_per_unit': float(b[1]), 'se': float(se),
                                           'multiplier_at_ticket_vs_mean': float(np.exp(b[1] * ((abs(n19 - 4.5) if nm == 'lopsided_1_9' else abs(n11 - 5.5)) - L.mean())))}
    top = [(r['date'], sorted(r['main']), r['tiers']['11'], r['tiers']['0']) for r in vt if r['tiers']['11'][1] + r['tiers']['0'][1] > 0]
    out['VAN_ticket'] = {
        'ticket': VAN_TICKET, 'complement': comp,
        'n_1_9_ticket_complement': [n19, 9 - n19], 'P_random_partition_this_lopsided_1_9': P19,
        'n_le_11_ticket_complement': [n11, 11 - n11], 'P_random_partition_this_lopsided_1_11': P11,
        'longest_run_ticket_complement': [runs(VAN_TICKET), runs(comp)], 'P_random_max_run_ge_6': float((rmax >= 6).mean()),
        'even_odd_ticket': [sum(x % 2 == 0 for x in VAN_TICKET), sum(x % 2 for x in VAN_TICKET)],
        'sum_ticket': sum(VAN_TICKET), 'near_winner_regression_410_draws': reg,
        'top_prize_wins_in_data': top,
    }
    dump(out, os.path.join(RUN, 'redteam_em.json'))
    print(json.dumps({k: out[k] for k in ('odds', 'VAN', 'EM_ticket', 'VAN_ticket')}, indent=1, default=str)[:9000])
    print(json.dumps({k: v for k, v in out['return'].items() if k != 'jackpot_wins_history'}, indent=1, default=str))
    print(json.dumps(out['EM_popularity'], indent=1, default=str)[:3000])


if __name__ == '__main__':
    main()
