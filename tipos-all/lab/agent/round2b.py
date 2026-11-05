"""Round 2b: (i) fix best single set as a field, rebuild others; (ii) allow overlaps with P>=6.9%."""
import sys, json, math, itertools
sys.path.insert(0, "/tmp/claude-0/-home-user-Mobil/b5a09aa0-3ae1-547d-aca0-e9005dcfc1f6/scratchpad/agent_lab")
import numpy as np
exec(open("/tmp/claude-0/-home-user-Mobil/b5a09aa0-3ae1-547d-aca0-e9005dcfc1f6/scratchpad/agent_lab/round2.py").read().split("# ---- 5 fields ----")[0])
Xall = np.zeros((len(combs), N + 1), bool); Xall[np.arange(len(combs))[:, None], combs] = True
def p_any3(fields):
    h = np.stack([Xall[:, f].sum(1) for f in fields], 1); return float((h.max(1) >= 3).mean())
def valid(f):
    f = sorted(f); dd = np.diff(f)
    return len(set(f)) == 5 and not (((dd[:-1] == 1) & (dd[1:] == 1)).any() or (dd == dd[0]).all())
sc = lambda f: float(score(np.array(sorted(f))))
r = json.load(open(LAB + "/round2.json"))
# (i) fixed field
fixed = [29, 30, 32, 34, 35]
pool = [n for n in r["pool_25_least_popular"] if n not in fixed]
bestP, bo = None, 1e9
for rs in range(80):
    perm = rng.permutation(pool).tolist(); P = [perm[i*4*0+i*5:(i+1)*5] for i in range(4)]
    o = sum(sc(f) if valid(f) else 1e9 for f in P); imp = True
    while imp:
        imp = False
        for i in range(4):
            for j in range(i+1, 4):
                for a in range(5):
                    for b in range(5):
                        Q = [f[:] for f in P]; Q[i][a], Q[j][b] = P[j][b], P[i][a]
                        oq = sum(sc(f) if valid(f) else 1e9 for f in Q)
                        if oq < o - 1e-12: P, o, imp = Q, oq, True
    if o < bo: bestP, bo = [sorted(f) for f in P], o
F1 = [fixed] + sorted(bestP)
res = {"with_fixed_29_30_32_34_35": dict(fields=F1, factors=[round(factor(f), 3) for f in F1], mean_factor=round(np.mean([factor(f) for f in F1]), 3),
       sum_log_factor=round(sum(math.log(factor(f)) for f in F1), 3), p_any_ge3=round(p_any3(F1), 5))}
# (ii) overlaps allowed: greedy single-number replacements from F1, keep P>=0.069
P = [f[:] for f in F1]; o = sum(sc(f) for f in P); imp = True
while imp:
    imp = False; cand = []
    for i in range(5):
        for a in range(5):
            for n in range(1, 36):
                if n in P[i]: continue
                Q = [f[:] for f in P]; Q[i][a] = n
                if not valid(Q[i]): continue
                d = sc(Q[i]) - sc(P[i])
                if d < -1e-9: cand.append((d, i, a, n))
    for d, i, a, n in sorted(cand):
        Q = [f[:] for f in P]; Q[i][a] = n
        if p_any3(Q) >= 0.069:
            P = [sorted(f) for f in Q]; imp = True; break
res["overlap_allowed_P_ge_6.9"] = dict(fields=P, factors=[round(factor(f), 3) for f in P], mean_factor=round(np.mean([factor(f) for f in P]), 3),
       sum_log_factor=round(sum(math.log(factor(f)) for f in P), 3), p_any_ge3=round(p_any3(P), 5), distinct_numbers=len(set(sum(P, []))))
r.update(res); json.dump(r, open(LAB + "/round2.json", "w"), indent=1, default=float)
print(json.dumps(res, indent=1))
