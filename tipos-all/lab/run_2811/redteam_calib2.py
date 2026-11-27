"""Red team: extra calibration of harness2 on VAN (20 000 random-rule replicates, new seed), because the first run
gave 1.24 % of p <= 0.01 (attainable level 0.975 %). Run: python3 -I redteam_calib2.py  (writes redteam_calib2.json)"""
import sys, os, time
import numpy as np
sys.path.insert(0, '/home/user/Mobil/tipos-all/lab/run_2811')
from redteam_common import RUN, setup_paths, pmf, dump
setup_paths()
from harness2 import evaluate, load
R = 20000; d = load('VAN'); p, N, K, T = pmf('VAN'); rng = np.random.default_rng(28114); ps = []; t0 = time.time()
for r in range(R):
    tick = np.argsort(rng.random((len(d), N)), axis=1)[:, :T] + 1
    ps.append(evaluate(lambda past, date, tick=tick: tick[len(past)].tolist(), 'VAN', 'random')['p_upper'])
ps = np.array(ps)
s = np.array([1.0])
for _ in range(len(d) - 30): s = np.convolve(s, p)
tail = np.cumsum(s[::-1])[::-1]
out = {'game': 'VAN', 'replicates': R, 'seed': 28114, 'seconds': round(time.time() - t0, 1)}
for a in (0.10, 0.05, 0.01):
    out['share_p_le_%g' % a] = float((ps <= a).mean()); out['attainable_%g' % a] = float(tail[tail <= a + 1e-15].max())
dump(out, os.path.join(RUN, 'redteam_calib2.json')); print(out)
