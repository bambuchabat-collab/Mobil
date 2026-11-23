"""Red team: collect verdicts + key numbers from redteam_{a,b,c,d,e,f,g,p5}.json into ../redteam.json.
Run after the other redteam_*.py scripts.  python3 -I redteam_summary.py"""
import json, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = lambda k: json.load(open(os.path.join(BASE, f'redteam_{k}.json')))
a, b, c, d, e, f, g, p5 = (L(k) for k in ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'p5'))
A = a['results']; pe = c['point_estimates']
r = lambda x, n=3: round(x, n)
out = {
 'title': 'Red team of run_2311 claims P1-P6 and the final EV tickets for Mon 23.11.2026',
 'scripts': ['scripts/redteam_common.py', 'scripts/redteam_model.py', 'scripts/redteam_a_walkforward.py', 'scripts/redteam_b_pairs.py',
             'scripts/redteam_c_money.py', 'scripts/redteam_d_extra.py', 'scripts/redteam_e_odds.py', 'scripts/redteam_f_tickets.py',
             'scripts/redteam_g_interaction.py', 'scripts/redteam_p5_van.py', 'scripts/redteam_summary.py'],
 'P1': {'verdict': 'SURVIVES (main numbers); extra-number part WEAKENED',
        'leakage_found': 'none that matters: log-bets centred on full-sample mean (absorbed exactly by the unpenalised intercept); '
                         'lambda, tau2, extra shares fitted inside each training window; premium = calendar months. '
                         'Minor: ideas_ev.py ridge lambda=2 taken from the earlier C1 fit (data to 12.11).',
        'minimal_walk_forward_corr_3_4_5': [r(A[f'all_draws|{m}match']['corr']) for m in (3, 4, 5)],
        'minimal_walk_forward_corr_with_pair_covariate_3_4_5': [r(A[f'all_draws_with_pair_covariate|{m}match']['corr']) for m in (3, 4, 5)],
        'p_perm_3_4_5': [A[f'all_draws|{m}match']['p_perm'] for m in (3, 4, 5)],
        'robustness_corr_3_4_5': {s: [r(A[f'{s}|{m}match']['corr']) for m in (3, 4, 5)] for s in
                                  ('drop_2024_(train+eval from 2025-01-01)', 'drop_premium_months', 'monday_only', 'post_era_only_2026')},
        'robustness_p_holm15_3_4_5': {s: [r(A[f'{s}|{m}match']['p_holm_15'], 4) for m in (3, 4, 5)] for s in
                                      ('all_draws', 'drop_2024_(train+eval from 2025-01-01)', 'drop_premium_months', 'monday_only', 'post_era_only_2026')},
        'rank_corr_redteam_vs_claimed_order': r(a['ranking_stability']['3match']['corr_with_claimed_order_rank']),
        'half_split_corr_of_number_effects_3_4': [r(a['ranking_stability']['3match']['corr_half1_vs_half2']), r(a['ranking_stability']['4match']['corr_half1_vs_half2'])],
        'extra_rel_popularity': c['extra_rel_popularity'],
        'extra_issue': 'claimed 0.86 for 5/6/7 pools the 2024 era when extras were 1-4 (share ~0.25) into extras 1-4; '
                       'post-era only 0.88, 2026 0.91, 2026-H2 0.92; and among players sharing unpopular numbers extras are more uniform (see P3)'},
 'P2': {'verdict': 'SURVIVES',
        'pair_pct_per_pair_OLS_all_27_numbers_3_4_5': [r(b['joint_fits'][f'{m}match']['OLS_27_numbers']['pct_per_unit'], 1) for m in (3, 4, 5)],
        'pairs_of_unpopular_numbers_vs_other_pairs_pct': {m: [r(b['joint_fits'][f'{m}match']['split_unpopular_pairs']['pct_per_unit'], 1),
                                                              r(b['joint_fits'][f'{m}match']['split_other_pairs']['pct_per_unit'], 1)] for m in (3, 4, 5)},
        'gap2_neighbours_pct_3_4_5': [r(b['joint_fits'][f'{m}match']['with_gap2_gap3:gap2']['pct_per_unit'], 1) for m in (3, 4, 5)],
        'dummies_1_2_3_pairs_log': {m: [r(b['joint_fits'][f'{m}match'][k]['coef']) for k in ('dummy_1pair', 'dummy_2pairs', 'dummy_3pairs')] for m in (3, 4, 5)},
        'walk_forward_oos_mse_reduction_pct_3_4_5': [r(b['walk_forward_pairs'][f'{m}match']['oos_mse_reduction_pct'], 1) for m in (3, 4, 5)],
        'draws_by_npairs': b['draws_by_npairs'],
        'field1_winning_draw_npairs': b['npairs_of_winning_draws']['field1 1 2 14 15 20 21'],
        'extrapolation': 'no: winning draws of the 3-pair field have <=3 pairs (5-match: 2 pairs 80 %, 3 pairs 20 %); '
                         'saturating dummy model gives the same ticket value (+11.44 % vs +11.40 %)'},
 'P3': {'verdict': 'WEAKENED (direction holds; size ~+10 % not +13 %; CI too narrow)',
        'claimed_gain_pct': 13.2, 'claimed_CI': [12.2, 14.3],
        'redteam_gain_pct_with_claimed_extra_shares': r(pe['ridge_LOO_linear_pairs|claim_pooled_all_eras(contaminated by 1-4 era)|FINAL']['gain_vs_random_pct'], 2),
        'redteam_gain_pct_2026_extras': r(pe['ridge_LOO_linear_pairs|2026_only|FINAL']['gain_vs_random_pct'], 2),
        'redteam_gain_pct_2026_extras_bootstrap_CI95': [r(v, 2) for v in c['bootstrap']['final_gain_pct']['CI95']],
        'redteam_gain_pct_model_fit_post_era_only': r(pe['ridge_LOO_linear_pairs_post_era_only|2026_only|FINAL']['gain_vs_random_pct'], 2),
        'redteam_main_only_pct': r(pe['ridge_LOO_linear_pairs|2026_only|FINAL']['main_numbers_only_pct'], 2),
        'redteam_extra_only_pct_2026': r(pe['ridge_LOO_linear_pairs|2026_only|FINAL']['extra_only_pct'], 2),
        'extra_bonus_with_main_extra_interaction_pct': [r(g['final_fields_extra_bonus'][k]['extra_bonus_pct_with_interaction'], 2) for k in ('field1', 'field2')],
        'interaction_test': {'delta': r(g['delta']), 'p': g['p_two_sided'], 'p_without_pb_in_D': g['robust_drop_pb_in_D']['p_two_sided'],
                             'p_2026_only': g['robust_2026_only_drop_pb_in_D']['p_two_sided'],
                             'extra_rel_pop_unpopular_vs_popular_draws': [g['extra_rel_pop_unpopular_D_tercile'], g['extra_rel_pop_popular_D_tercile']]},
        'honest_split_half': {k: {'gain_eval_half_of_pair_chosen_on_other_half': r(v['gain_on_eval_half'], 2),
                                  'FINAL_on_eval_half': r(v['FINAL_gain_on_eval_half'], 2)} for k, v in c['honest_split_half'].items()},
        'tier_factors_FINAL_vs_random_3_4_5': pe['ridge_LOO_linear_pairs|2026_only|FINAL']['tier_factor_vs_random'],
        'best_estimate_gain_pct': '~+10 (plausible 8.5-12)',
        'return_per_EUR': {'population_average_3pct_PV': r(c['return_per_EUR']['population_average_3pct']),
                           'population_average_0pct_PV': r(c['return_per_EUR']['population_average_0pct']),
                           'FINAL_3pct_PV_redteam_model': r(c['return_per_EUR']['FINAL_3pct']),
                           'FINAL_0pct_PV_redteam_model': r(c['return_per_EUR']['FINAL_0pct']),
                           'best_estimate_10pct_incl_top_tier_sharing_3pct_0pct': [0.528, 0.548],
                           'best_estimate_range_incl_top_tier_sharing': [0.52, 0.55],
                           'note': 'claimed 0.53-0.55 is only slightly optimistic; the % gain is overstated more than the return'}},
 'P4': {'verdict': 'SURVIVES statistically, practically negligible (0.17 pp); final tickets already comply',
        'p_perm_D_reassignment': d['p_perm_m34'], 'pct_effect_3_4_5': {k: r(v, 1) for k, v in d['pct_effect'].items()},
        'n_draws_pb_in_D': d['n_pb_in_D'], 'implied_share_of_tickets_extra_from_own_six': [r(d['implied_phi_from_3match'], 3), r(d['implied_phi_from_4match'], 3)],
        'money_pp': r(d['money_pp_per_EUR_outside_minus_inside'], 2), 'final_tickets': d['final_tickets'],
        'identifiable': 'yes: with independent extras the +1 share of m-hit winners cannot depend on whether the drawn extra is a drawn main number'},
 'P5': {'verdict': 'SURVIVES (irrelevant to the Monday EV tickets)', 'fixed_tier_violations_410_draws': len(p5['fixed_tier_violations']),
        'odd_even_mean_z': r(p5['odd_even_mean_z'], 2), 'null_q99': r(p5['null_q99'], 2), 'p': p5['p']},
 'P6': {'verdict': 'SURVIVES', 'P_any': e['P_any_prize_2_fields'], 'P_6main_either': e['P_6main_either'], 'P_6plus1_either': e['P_6plus1_either'],
        'returns_per_EUR': {k: r(v['total_per_EUR'], 4) for k, v in e['returns'].items()}, 'low_tiers_realised_2026_normal': r(e['low_tiers_share_2026_normal'], 4),
        'low_tiers_by_rules': r(e['low_tiers_by_rules'], 4), 'november_2026_low_tier_share_range': [0.309, 0.3136],
        'herny_plan_check': 'fetched 23.11.2026 (plan 000191/2026, effective 18.03.2026): 1st tier 480 000 fixed, 2 winners 480 000/2 each, '
                            '>=3 winners 720 000/n, >=7 winners lump sum; 2nd tier 30 000 shared; tiers 3-8 1.5/4.3/4.4/10.8/6.2/27.0 % of 57.90 %; rounding down to 0.10 EUR'},
 'tickets': {'verdict': 'KEEP', 'FINAL': f['FINAL'], 'RUNNER_UP_constraints_ok': f['RUNNER_UP']['ALL_USER_CONSTRAINTS_OK'],
             'alternatives_redteam_model': {k: {kk: vv for kk, vv in v.items() if kk != 'EV_mean'} for k, v in c['alternatives'].items()},
             'final_minus_runner_up_pp': c['bootstrap']['final_minus_runner_pp'],
             'caveats': ['21 and 24 are average-popularity numbers (claimed ranks 15 and 14, rel. freq 1.00), kept for the pair value; '
                         'restricting to the 12 least popular numbers costs ~0.7 % of tier 3-5 value (not significant)',
                         'if "no equal steps" were read as "all gaps distinct", both fields fail (gaps 1,12,1,5,1 and 6,2,1,4,1); '
                         'under the stated definition (no 3-term AP) they pass',
                         'field 2 has 18 19 23 24 on one row of an 8-wide grid; 15 % of random fields have >=4 on a line; slip geometry (H2) not significant']}}
json.dump(out, open(os.path.join(BASE, 'redteam.json'), 'w'), indent=1, ensure_ascii=False, default=str)
print('wrote redteam.json')
