"""Second VAN ticket for 25.11: exactly 5 common numbers with ticket 1, random-looking, mid popularity (ticket and complement)."""
import json, secrets
src = open('/home/user/Mobil/tipos-all/lab/run_2411/van_pick_2511.py').read().split('while True:')[0]
ns = {}; exec(src, ns); ok, U, PREV = ns['ok'], ns['U'], ns['PREV']
b = {int(k): v for k, v in json.load(open('agents/A10.json'))['popularity_beta_0_409'].items()}
R = secrets.SystemRandom(); score = lambda t: sum(b[x] for x in t)
ref = sorted(score(R.sample(range(1, 23), 11)) for _ in range(20000)); pct = lambda s: sum(r < s for r in ref) / len(ref)
A = set(json.load(open('ticket_2511.json'))['ticket'])
while True:
    B = set(R.sample(sorted(A), 5)) | set(R.sample(sorted(U - A), 6))
    if ok(B) and all(3 <= len(B & p) <= 8 for p in PREV) and 0.40 <= pct(score(B)) <= 0.60 and 0.40 <= pct(score(U - B)) <= 0.60: break
print('A', sorted(A), '| B', sorted(B), '| common', sorted(A & B), '| B pct %.2f compl %.2f' % (pct(score(B)), pct(score(U - B))))
json.dump({'draw': '2026-11-25 18:00 CET', 'game': 'Všetko alebo nič', 'tickets': [sorted(A), sorted(B)], 'common': sorted(A & B)},
          open('tickets_final_2511.json', 'w'))
