"""Red team: merge the component results into redteam.json with the verdicts (python3 -I -B).
Run after redteam_harness_mc.py, redteam_leak.py, redteam_prereg.py, redteam_stats.py, redteam_ticket.py."""
import json, os
RUN = '/home/user/Mobil/tipos-all/lab/run_2511'
L = lambda f: json.load(open(os.path.join(RUN, f)))
mc, lk, pr, st, tk = (L('redteam_harness_mc.json'), L('redteam_leak.json'), L('redteam_prereg.json'),
                      L('redteam_stats.json'), L('redteam_ticket.json'))

leak_per_agent = {}
for r in lk['rules']:
    leak_per_agent.setdefault(r['agent'], []).append(r)
declared = {'A5': 'reads DRAWS[t]["date"] (date only, declared, public in advance)',
            'A6': 'reads DRAWS[t]["date"] (date only, declared); EV / Loto 5z35 rows strictly dated < VAN date',
            'A7': 'R2/R3 orientation from draws 0..29 at import (pre-registered; all < 30 <= t)',
            'A8': 'reads DRAWS[t]["date"] (date only, declared); combo search on draws 0..29 only',
            'A10': 'external tier data run_2311/data/van.json, rows < t only'}
leak = {a: {'verdict': 'LEAKAGE FOUND' if any(r['leak'] for r in rs) else 'LEAKAGE none',
            'poisoned_t_tested_per_rule': [r['poison_t_tested'] for r in rs],
            'tickets_changed_under_poison': sum(r['poison_changed_ticket'] for r in rs),
            'reproduced_reported_numbers': all(r['reproduced'] for r in rs),
            'ticket_25_11_reproduced': lk['tickets_25_11'][a]['match'],
            'note': declared.get(a, 'uses only the `past` argument')}
        for a, rs in sorted(leak_per_agent.items(), key=lambda kv: int(kv[0][1:]))}

dev = [
    'A1: R3 sampler edited after the file was first committed (u in [0,T) -> (0,T]); no parameter change, but the MC '
    'realisation changed: pre-change code gives R3 mean %.3f, p %.3f vs reported %.3f, p %.3f (R3 is MC-noise driven). '
    'Not decisive either way.' % (pr['A1_code_change']['pre_change']['mean_hits'], pr['A1_code_change']['pre_change']['p_mean_lower'],
                                  pr['A1_code_change']['reported']['mean_hits'], pr['A1_code_change']['reported']['p_mean_lower']),
    'A8: R1 and R2 selected the same generator combo (PY/UDAY/SEQ) -> one test counted twice (Holm slightly conservative).',
    'A6 R2 and A10 R2 are exact complements of R1 (hits = 11 - hits): pre-registered two-tailed pairs, not independent tests.',
    'A4: target weekday = previous date + 1 day (wrong after the two calendar gaps); pre-registered, not a leak.',
    'aggregate.py declares a survivor if Holm(p_mean) OR Holm(p_le3) < 0.05: two families, FWER up to ~0.10 (moot: none).',
    'Timing only proves prereg-before-result for the final files; earlier unsaved runs cannot be excluded by mtimes/git '
    '(committed .pyc bytecode of A4/A5/A9/A10 is identical to the final code).']

OUT = {
    'verdicts': {
        'HARNESS': mc['verdict'],
        'LEAKAGE': {a: v['verdict'] for a, v in leak.items()},
        'LEAKAGE_overall': 'none' if not lk['any_leak'] else 'found',
        'PREREG': 'ok, minor deviations (see deviations)' if pr['all_preregs_before_results'] else 'PROBLEM',
        'HOLM_survivors': st['holm']['survivors_holm_p'] + st['holm']['survivors_holm_le3'],
        'TICKET': 'ok' if tk['verdict'] == 'TICKET OK' else 'change'},
    'harness': {'pmf_chi2': mc['a_pmf_sets']['chi2'], 'pmf_df': mc['a_pmf_sets']['df'],
                'random_runs': mc['b_random_ticket_runs']['runs'],
                'p_mean_lower_calibration': mc['b_random_ticket_runs']['p_mean_lower']['calibration'],
                'p_mean_lower_ks': mc['b_random_ticket_runs']['p_mean_lower']['ks'],
                'p_le3_calibration': mc['b_random_ticket_runs']['p_le3']['calibration'],
                'tail_A7R2': mc['c_tail_A7R2'],
                'past_dependent_null': mc['d_past_dependent_null']},
    'leakage': {'per_agent': leak, 'positive_controls_flagged': lk['controls_flagged'], 'controls': lk['controls']},
    'prereg': {'timing': [{k: r[k] for k in ('agent', 'prereg_written', 'json_mtime', 'written_before_result',
                                              'prereg_committed_not_after_result', 'prereg_unchanged_after_commit',
                                              'code_unchanged_after_commit')} for r in pr['timing']],
               'pyc_forensics_identical': {a: v['code_object_identical_to_current'] for a, v in pr['pyc_forensics'].items()},
               'hashes_match': pr['hashes']['match'], 'side_data': pr['side_data'],
               'manual_prereg_vs_code': pr['manual_prereg_vs_code'], 'deviations': dev},
    'multiplicity': {'holm_recomputed_matches_aggregate': st['holm']['all_match_aggregate_json'],
                     'min_p': st['holm']['min_p'], 'min_p_holm': st['holm']['min_p_holm'],
                     'min_p_le3': st['holm']['min_p_le3'], 'min_p_le3_holm': st['holm']['min_p_le3_holm'],
                     'bh_survivors': st['holm']['survivors_bh_q_0.05'],
                     'ks_all30': st['ks_all30'], 'ks_dedup27': st['ks_dedup27'],
                     'global_minp_conditional': st['global_minp_conditional']},
    'A7_R2_stability': st['A7_R2_stability'], 'effect_meaning': st['effect_meaning'],
    'ticket': {k: tk[k] for k in ('ticket', 'complement', 'T', 'C', 'vs_last_draws', 'vs_history',
                                  'popularity_proxy', 'odds', 'problems')},
    'scripts': ['redteam_harness_mc.py', 'redteam_leak.py', 'redteam_prereg.py', 'redteam_stats.py', 'redteam_ticket.py',
                'redteam_build.py'],
    'component_files': ['redteam_harness_mc.json', 'redteam_leak.json', 'redteam_tickets.json', 'redteam_prereg.json',
                        'redteam_stats.json', 'redteam_ticket.json']}
json.dump(OUT, open(os.path.join(RUN, 'redteam.json'), 'w'), indent=1)
print(json.dumps(OUT['verdicts'], indent=1))
