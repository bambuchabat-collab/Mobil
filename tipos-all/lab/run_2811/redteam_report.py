"""Red team: merge the part results into redteam.json (summary + key numbers).
Order: redteam_repro.py -> redteam_leakage.py -> redteam_stats.py -> redteam_calib2.py -> redteam_em.py -> this.
Run: python3 -I redteam_report.py
"""
import sys, os, json
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2811')
from redteam_common import RUN, dump

L = lambda n: json.load(open(os.path.join(RUN, n)))
rep, leak, st, cal2, em = L('redteam_repro.json'), L('redteam_leakage.json'), L('redteam_stats.json'), L('redteam_calib2.json'), L('redteam_em.json')

per_agent = {}
for x in leak['items']:
    if x['kind'] != 'formula':
        continue
    a = per_agent.setdefault(x['agent'], {'formulas': [], 'leak_detected': False, 'files_opened_inside_f': set()})
    a['formulas'].append({'formula': x['formula'], 'game': x['game'], 'changed_of_sampled_t': '%d/%d' % (x['n_changed'], x['n_t'])})
    a['leak_detected'] |= x['leak_detected']; a['files_opened_inside_f'] |= set(x['files_opened_inside_f'])
for a, v in per_agent.items():
    v['files_opened_inside_f'] = sorted(v['files_opened_inside_f'])
    v['static_module_level_data'] = leak['static'][a]['module_level_data']
    v['verdict'] = 'no leakage' if not v['leak_detected'] else 'LEAK'
notes = {'S1': 'CACHE_P = params() at import loads the full file but only N, K, T are used (d unused)',
         'S2': 'engine_for() calls params() inside f, i.e. re-reads em.json on every call; only N, K, T used; Engine cache checks the prefix',
         'S3': 'online BM caches check the prefix; no data access inside f',
         'S4': 'N_EM = params("EM")[1] at import (N = 33 only); Lomb-Scargle cache checks the prefix',
         'S5': '_D from params() at import is unused; Hedge and MLP caches keyed by the prefix (MLP refit point tr <= t)'}
for a in per_agent:
    per_agent[a]['note'] = notes[a]

s3 = st['S3_F3_stability']
out = {
    'leakage': {'per_agent': per_agent, 'sampled_t': leak['sampled_t'],
                'positive_controls': {x['formula']: '%d/%d caught' % (x['n_changed'], x['n_t']) for x in leak['items'] if x['kind'] == 'peek'},
                'negative_control_PC0': '%d/%d changed' % next((x['n_changed'], x['n_t']) for x in leak['items'] if x['kind'] == 'legit'),
                'control_scores': leak['control_scores'],
                'all_15_reproduced_identically': rep['all_match']},
    'pvalues': {'rows': st['pvalues'], 'holm_survivors': st['holm_survivors'], 'holm_min': st['holm_min'],
                'P_min_of_15_null_p_le_0.039': st['P_min_p_le_0.039_under_H0_15_indep'],
                'calibration_random_rule': st['calibration'] + [cal2]},
    'S3_F3_stability': {k: s3[k] for k in ('all', 'half1', 'half2', '2015_2020', '2021_2026', 'years', 'years_above_expected',
                                           'expected_hits_from_marginals_only', 'shift_null', 'biased_random_decode_control',
                                           'F3_stream_linear_complexity', 'ticket_number_freq_low_1_11_vs_high_23_33',
                                           'draw_number_freq_low_1_11_vs_high_23_33')},
    'EM_rules': {'pick': '7 of 1..33 + 1 of 1..6 (player chooses both)', 'price_eur': 1.50, 'max_bets_per_ticket': 6,
                 'joker_addon_eur': 0.50, 'draws': 'Tue, Sat 18:00', 'online_acceptance_until': '2026-11-28 17:45',
                 'prize_pool': '50 % of stakes; all 10 tiers pari-mutuel (no fixed prizes)',
                 'tier_shares': {'7+1': '20 % (+ jackpot)', '7': '3 %', '6+1': '3 %', '6': '3.5 %', '5+1': '4 %', '5': '4 %',
                                 '4+1': '6.5 %', '4': '17.5 %', '3+1': '13.5 %', '2+1': '25 %'},
                 'jackpot_guarantee_eur': 1_000_000, 'jackpot_now_eur': em['return']['jackpot_now'],
                 'source': 'TIPOS herny plan, clanok 25-26 (redteam_rules_extract.txt)'},
    'EM_odds_return': {'odds': em['odds'], 'return': {k: v for k, v in em['return'].items() if k != 'jackpot_wins_history'},
                       'jackpot_wins_history': em['return']['jackpot_wins_history']},
    'VAN_compare': em['VAN'],
    'EM_ticket': em['EM_ticket'], 'EM_popularity': em['EM_popularity'], 'VAN_ticket': em['VAN_ticket'],
}
dump(out, os.path.join(RUN, 'redteam.json'))
print('written redteam.json')
