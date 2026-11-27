"""Red team task 2: p-value calibration of harness2, independent check of the 15 p-values, Holm,
stability of S3 F3 (halves, 2015-2020 vs 2021-2026, years) and where its small excess comes from.
Needs redteam_repro.json (python3 -I redteam_repro.py). Run: python3 -I redteam_stats.py  (writes redteam_stats.json)
"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2811')
from redteam_common import RUN, FORMULAS, setup_paths, pmf, holm, dump
setup_paths()
from harness2 import evaluate, load

R_CAL = 5000          # random-rule replicates per game through harness2.evaluate
R_MC = 10_000_000     # multinomial Monte-Carlo replicates for the null of the total hits


def exact_tail(S, n, game):
    p, N, K, T = pmf(game)
    s = np.array([1.0])
    for _ in range(n): s = np.convolve(s, p)
    return float(s[S:].sum()), float(s[:S + 1].sum())


def mc_tail(S, n, game, seed):
    p, N, K, T = pmf(game)
    rng = np.random.default_rng(seed); k = np.arange(T + 1); ge = 0; done = 0
    while done < R_MC:
        m = min(1_000_000, R_MC - done)
        c = rng.multinomial(n, p, size=m)
        ge += int(((c @ k) >= S).sum()); done += m
    return ge / R_MC


def calibration(game, seed):
    d = load(game); p, N, K, T = pmf(game)
    rng = np.random.default_rng(seed); ps = []; t0 = time.time()
    for r in range(R_CAL):
        tick = np.argsort(rng.random((len(d), N)), axis=1)[:, :T] + 1
        f = lambda past, date, tick=tick: tick[len(past)].tolist()
        ps.append(evaluate(f, game, 'random')['p_upper'])
    ps = np.array(ps)
    # discrete p-values: P(p <= a) must be <= a (conservative); KS distance to U(0,1)
    srt = np.sort(ps); ks = float(np.max(np.abs(np.arange(1, R_CAL + 1) / R_CAL - srt)))
    return {'game': game, 'replicates': R_CAL, 'seed': seed, 'share_p_le_0.05': float((ps <= 0.05).mean()),
            'share_p_le_0.01': float((ps <= 0.01).mean()), 'share_p_le_0.10': float((ps <= 0.10).mean()),
            'mean_p': float(ps.mean()), 'ks_distance': ks, 'ks_crit_5pct': 1.36 / np.sqrt(R_CAL),
            'seconds': round(time.time() - t0, 1)}


def seg_stats(h, game):
    p, N, K, T = pmf(game); mu = sum(k * q for k, q in enumerate(p)); var = sum((k - mu) ** 2 * q for k, q in enumerate(p))
    h = np.asarray(h); n = len(h)
    pu, pl = exact_tail(int(h.sum()), n, game)
    return {'n': n, 'mean': float(h.mean()), 'expected': mu, 'z': float((h.mean() - mu) / np.sqrt(var / n)), 'p_upper': pu}


def main():
    t0 = time.time()
    rep = json.load(open(os.path.join(RUN, 'redteam_repro.json')))
    agg = json.load(open(os.path.join(RUN, 'aggregate2.json')))
    out = {}
    # ---- independent check of the 15 primary p-values
    rows = []
    for i, o in enumerate(rep['formulas']):
        h = np.array(o['hits']); n = len(h); S = int(h.sum())
        pu, pl = exact_tail(S, n, o['game'])
        mc = mc_tail(S, n, o['game'], [2811, i])
        a = next(r for r in agg['rows'] if r['id'] == o['agent'] and r['rule'] == o['rule'] and r['game'] == o['game'])
        rows.append({'agent': o['agent'], 'formula': o['formula'], 'rule': o['rule'], 'game': o['game'], 'n': n, 'S': S,
                     'mean': S / n, 'p_upper_reported': a['p'], 'p_upper_recomputed': pu, 'p_upper_mc_1e7': mc,
                     'repro_matches_agent_json': o['match']})
        print(o['agent'], o['formula'], o['game'], 'S=%d n=%d p %.5f recomputed %.5f MC %.5f' % (S, n, a['p'], pu, mc), flush=True)
    hp = holm([r['p_upper_recomputed'] for r in rows])
    for r, x in zip(rows, hp): r['holm'] = x
    out['pvalues'] = rows
    out['holm_survivors'] = [(r['agent'], r['formula']) for r in rows if r['holm'] < 0.05]
    out['holm_min'] = min(hp)
    out['aggregate_holm_matches'] = all(abs(r['holm'] - next(a['holm'] for a in agg['rows'] if a['id'] == r['agent'] and a['rule'] == r['rule'])) < 1e-9 for r in rows)
    out['min_p_expected_under_H0_15_tests'] = 1 / 16
    out['P_min_p_le_0.039_under_H0_15_indep'] = 1 - (1 - 0.0392) ** 15
    # ---- calibration with random rules through the real harness
    out['calibration'] = [calibration('EM', 28111), calibration('VAN', 28112)]
    for c in out['calibration']: print('calibration', c, flush=True)
    # ---- S3 F3 stability
    o = next(x for x in rep['formulas'] if (x['agent'], x['formula']) == ('S3', 'F3'))
    h = np.array(o['hits']); dates = o['dates']; n = len(h); yrs = np.array([int(s[:4]) for s in dates])
    st = {'all': seg_stats(h, 'EM'), 'half1': seg_stats(h[:n // 2], 'EM'), 'half2': seg_stats(h[n // 2:], 'EM'),
          '2015_2020': seg_stats(h[yrs <= 2020], 'EM'), '2021_2026': seg_stats(h[yrs >= 2021], 'EM'),
          'half_dates': [dates[0], dates[n // 2 - 1], dates[n // 2], dates[-1]],
          'years': {int(y): {'n': int((yrs == y).sum()), 'mean': float(h[yrs == y].mean())} for y in sorted(set(yrs))}}
    st['years_above_expected'] = sum(v['mean'] > 1.4848 for v in st['years'].values())
    # ---- where does the excess come from? static marginal bias vs a time-specific link
    d = load('EM'); ts = o['ts']; tick = o['tickets']
    D = np.zeros((n, 33)); P = np.zeros((n, 33))
    for j, t in enumerate(ts):
        D[j, np.array(d[t]['main']) - 1] = 1; P[j, np.array(tick[j]) - 1] = 1
    q = P.mean(0); pfreq = D.mean(0)
    st['ticket_number_freq_low_1_11_vs_high_23_33'] = [float(q[:11].mean() * 33 / 7), float(q[22:].mean() * 33 / 7)]
    st['draw_number_freq_low_1_11_vs_high_23_33'] = [float(pfreq[:11].mean() * 33 / 7), float(pfreq[22:].mean() * 33 / 7)]
    st['mean_ticket_sum'] = float((P * np.arange(1, 34)).sum(1).mean())
    st['expected_hits_from_marginals_only'] = float((q * pfreq).sum())   # sum_i q_i p_i: no time link
    # circular-shift null: same tickets, draws shifted by s (keeps both marginals, breaks the time link)
    sh = np.array([(P * np.roll(D, -s, axis=0)).sum(1).mean() for s in range(1, n)])
    st['shift_null'] = {'mean': float(sh.mean()), 'sd': float(sh.std()), 'share_ge_observed': float((sh >= h.mean()).mean()),
                        'n_shifts': int(n - 1)}
    # biased-random control: same decoding as F3 but with uniform random 6-bit values instead of the BM prediction
    rng = np.random.default_rng(28113); means = []
    for r in range(2000):
        hits = 0
        for j, t in enumerate(ts):
            rem = list(range(1, 34)); s = set()
            for v in rng.integers(0, 64, 7):
                s.add(rem.pop(int(v) % len(rem)))
            hits += len(s & set(d[t]['main']))
        means.append(hits / n)
    means = np.array(means)
    st['biased_random_decode_control'] = {'replicates': 2000, 'mean_of_means': float(means.mean()), 'sd': float(means.std()),
                                          'share_ge_observed': float((means >= h.mean()).mean())}
    s3 = json.load(open(os.path.join(RUN, 'agents', 'S3.json')))
    st['F3_stream_linear_complexity'] = s3.get('linear_complexity_full_streams', {}).get('F3_EM_lehmer_bits_GF2')
    out['S3_F3_stability'] = st
    print(json.dumps(st, indent=1), flush=True)
    out['seconds'] = round(time.time() - t0, 1)
    dump(out, os.path.join(RUN, 'redteam_stats.json'))


if __name__ == '__main__':
    main()
