"""One random-looking VAN ticket for 25.11.2026 whose popularity (A10 betas) and its complement's are both mid-range."""
import json, secrets, importlib.util, sys
spec = importlib.util.spec_from_file_location('vp', '/home/user/Mobil/tipos-all/lab/run_2411/van_pick_2511.py')
src = open('/home/user/Mobil/tipos-all/lab/run_2411/van_pick_2511.py').read().split('while True:')[0]  # reuse ok() filters only
ns = {}; exec(src, ns); ok, U = ns['ok'], ns['U']
b = {int(k): v for k, v in json.load(open('agents/A10.json'))['popularity_beta_0_409'].items()}
R = secrets.SystemRandom()
score = lambda t: sum(b[x] for x in t)
ref = sorted(score(R.sample(range(1, 23), 11)) for _ in range(20000))
pct = lambda s: sum(r < s for r in ref) / len(ref)
while True:
    t = set(R.sample(range(1, 23), 11))
    if all(len(t & p) <= 8 and len(t & p) >= 3 for p in ns['PREV']) and ok(t) and 0.40 <= pct(score(t)) <= 0.60 and 0.40 <= pct(score(U - t)) <= 0.60: break
print('ticket', sorted(t), 'pct %.2f' % pct(score(t)), '| complement', sorted(U - t), 'pct %.2f' % pct(score(U - t)))
old = {1, 4, 7, 8, 10, 11, 14, 16, 18, 20, 21}
print('old ticket pct %.2f, complement pct %.2f' % (pct(score(old)), pct(score(U - old))))
json.dump({'draw': '2026-11-25 18:00 CET', 'game': 'Všetko alebo nič', 'ticket': sorted(t), 'complement': sorted(U - t),
           'popularity_pct': [pct(score(t)), pct(score(U - t))]}, open('ticket_2511.json', 'w'))
