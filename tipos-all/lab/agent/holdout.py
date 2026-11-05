"""Confirmatory holdout tests (2024-01-01..2026-11-04), directions fixed by train_results.json + prereg.json."""
import sys, json, math, itertools, time
sys.path.insert(0, "/tmp/claude-0/-home-user-Mobil/b5a09aa0-3ae1-547d-aca0-e9005dcfc1f6/scratchpad/agent_lab")
import numpy as np
from lab_common import load, ordered, indicator, shuffle_within, random_draws, mc_p, corr, holm, LAB, N, K
import lab_stats as S

R = 4000
rng = np.random.default_rng(42)
pre = json.load(open(LAB + "/prereg.json"))
tr = json.load(open(LAB + "/train_results.json"))["results"]
train_rows = load("train"); hold_rows = load("holdout"); all_rows = load("all")
Bt, Bh, Ba = ordered(train_rows), ordered(hold_rows), ordered(all_rows)
Xh = indicator(Bh); nh = len(Bh); nt = len(Bt)
ch = S.context(hold_rows)
t0 = time.time()


def side(sign):
    return "greater" if sign > 0 else "less"


def one_sided_normal(z, sign):
    return 0.5 * math.erfc(sign * z / math.sqrt(2))


def mcs(fn, reps=R):
    return np.array([fn(shuffle_within(Bh, rng)) for _ in range(reps)])


def mcu(fn, reps=R):
    return np.array([fn(random_draws(nh, rng)) for _ in range(reps)])


def mcp(fn, lab, reps=R):
    return np.array([fn(rng.permutation(lab)) for _ in range(reps)])


H = {}
r = np.array(tr["H01"]["resid"]); f = lambda b: corr(r, S.pos_resid(b))
o = f(Bh); H["H01"] = (o, mc_p(o, mcs(f), "greater"), f"corr resid={o:+.3f}")
r = np.array(tr["H02"]["meanpos"]) - 3; f = lambda b: corr(r, S.meanpos(b)[0] - 3)
o = f(Bh); H["H02"] = (o, mc_p(o, mcs(f), "greater"), f"corr meanpos dev={o:+.3f}")
sg = tr["H03"]["sign"]; o = S.s_early_freq(Bh); H["H03"] = (o, mc_p(o, mcs(S.s_early_freq), side(sg)), f"corr={o:+.3f}")
z = S.z_single_count(Bh); H["H04a"] = (z, one_sided_normal(z, tr["H04a"]["sign"]), f"z={z:+.2f}")
sg = tr["H04b"]["sign"]; o = S.s_single_pos(Bh); H["H04b"] = (o, mc_p(o, mcs(S.s_single_pos), side(sg)), f"mean pos={o:.3f}")
sg = tr["H05a"]["sign"]; o = S.s_ink_freq(Bh); H["H05a"] = (o, mc_p(o, mcu(S.s_ink_freq), side(sg)), f"corr={o:+.3f}")
sg = tr["H05b"]["sign"]; o = S.s_ink_pos(Bh); H["H05b"] = (o, mc_p(o, mcs(S.s_ink_pos), side(sg)), f"corr={o:+.3f}")
sg = tr["H06a"]["sign"]; o = S.s_seqdist(Bh); H["H06a"] = (o, mc_p(o, mcs(S.s_seqdist), side(sg)), f"mean dist={o:.3f}")
r = np.array(tr["H06b"]["resid"]); f = lambda b: corr(r, S.trans_resid(b))
o = f(Bh); H["H06b"] = (o, mc_p(o, mcs(f, 2000), "greater"), f"corr resid={o:+.3f}")
sg = tr["H07a"]["sign"]; o = S.s_consec(Bh); H["H07a"] = (o, mc_p(o, mcu(S.s_consec), side(sg)), f"pairs={o:.0f}")
sg = tr["H07b"]["sign"]; o = S.s_range(Bh); H["H07b"] = (o, mc_p(o, mcu(S.s_range), side(sg)), f"range={o:.3f}")
mws = np.isin(ch["wd"], [2, 6]); Bw = Bh[mws]; lw = ch["wd"][mws]; r = np.array(tr["H08"]["diff"])
f = lambda l: corr(r, S.diff2(Bw, l, 2, 6)); o = f(lw); H["H08"] = (o, mc_p(o, mcp(f, lw), "greater"), f"corr diff={o:+.3f}")
f = lambda l: S.chi2_homog(Bh, l); o = f(ch["year"]); nul = mcp(f, ch["year"]); H["H09a"] = (o, mc_p(o, nul, "greater"), f"chi2={o:.1f} (null {nul.mean():.1f})")
r = np.array(tr["H09b"]["dev"]); f = lambda b: corr(r, S.freq_dev(b)); o = f(Bh); H["H09b"] = (o, mc_p(o, mcu(f), "greater"), f"corr={o:+.3f}")
r = np.array(tr["H10"]["resid"]); f = lambda l: corr(r, S.homog_resid(Bh, l, [0, 1, 2, 3])); o = f(ch["season"])
H["H10"] = (o, mc_p(o, mcp(f, ch["season"]), "greater"), f"corr resid={o:+.3f}")
sg = tr["H11"]["sign"]; f = lambda l: S.s_temp_ink(Bh, l); o = f(ch["temp"]); H["H11"] = (o, mc_p(o, mcp(f, ch["temp"]), side(sg)), f"corr={o:+.3f}")
r = np.array(tr["H12"]["diff"]); f = lambda l: corr(r, S.diff2(Bh, l, 1, 0)); o = f(ch["hi_sales"])
H["H12"] = (o, mc_p(o, mcp(f, ch["hi_sales"]), "greater"), f"corr diff={o:+.3f}")
r = np.array(tr["H13a"]["resid"]); f = lambda l: corr(r, S.homog_resid(Bh, l, [0, 1, 2, 3])); o = f(ch["moonq"])
H["H13a"] = (o, mc_p(o, mcp(f, ch["moonq"]), "greater"), f"corr resid={o:+.3f}")
sg = tr["H13b"]["sign"]; f = lambda l: S.s_illum_sum(Bh, l); o = f(ch["illum"]); H["H13b"] = (o, mc_p(o, mcp(f, ch["illum"]), side(sg)), f"corr={o:+.3f}")
z, ex = S.z_droot(Bh, ch["droot"]); H["H14a"] = (z, one_sided_normal(z, tr["H14a"]["sign"]), f"z={z:+.2f}")
z, ex = S.z_dom(Bh, ch["dom"]); H["H14b"] = (z, one_sided_normal(z, tr["H14b"]["sign"]), f"z={z:+.2f}")
z, ex = S.z_joker(Bh, ch["joker"]); H["H15"] = (z, one_sided_normal(z, tr["H15"]["sign"]), f"z={z:+.2f}")
lt = np.array(tr["H16"]["lt"]); pi = np.array(tr["H16"]["pi"])
f = lambda b: float((S.cb_mix_logpred(indicator(b), lt, pi) - S.LOG_UNIF_SET).mean())
o = f(Bh); H["H16"] = (o, mc_p(o, mcu(f, 2000), "greater"), f"logscore gain={o:+.4f} nats/draw")


def carry(Bc):
    pp, pc = [], []
    for t in range(1, Bc.shape[0]):
        prev = {v: i + 1 for i, v in enumerate(Bc[t - 1])}
        for i, v in enumerate(Bc[t]):
            if v in prev:
                pp.append(prev[v]); pc.append(i + 1)
    return float(np.mean(pc)), corr(pp, pc)


o = carry(Bh); nul = [carry(shuffle_within(Bh, rng)) for _ in range(3000)]
H["H17a"] = (o[0], mc_p(o[0], np.array([x[0] for x in nul]), side(tr["H17a"]["sign"])), f"mean pos={o[0]:.3f}")
H["H17b"] = (o[1], mc_p(o[1], np.array([x[1] for x in nul]), side(tr["H17b"]["sign"])), f"corr={o[1]:+.3f}")
bt = np.array(tr["P1"]["beta"]); f = lambda b: corr(bt, S.freq(b)); o = f(Bh)
H["H18"] = (o, mc_p(o, mcu(f), side(tr["H18"]["sign"])), f"corr(train beta, holdout freq)={o:+.3f}")
print("hypothesis tests done", round(time.time() - t0, 1), flush=True)

# ---- M1 walk-forward on holdout (params from train) ----
Xa = indicator(Ba)
Sc = S.disc_scores(Xa, tr["M1"]["half"])
h1 = [S.hits(S.top5(tr["M1"]["beta"] * Sc[t], rng), Ba[t]) for t in range(nt, len(Ba))]
ls1 = float((S.bern_logscore(Xa[nt:], S.tilt_probs(Sc[nt:], tr["M1"]["beta"])) - S.bern_logscore(Xa[nt:], np.full((nh, N), K / N))).mean())
z1 = S.hits_z(h1); H["M1"] = (z1, one_sided_normal(z1, 1), f"mean hits={np.mean(h1):.4f} vs 0.7143, z={z1:+.2f}, logscore gain={ls1:+.4f}")
# ---- M2 PL walk-forward ----
w = None; h2 = []; ls2 = []
for t in range(nt, len(Ba)):
    w = S.pl_fit(Ba[:t], tr["M2"]["alpha"], w, iters=60 if w is None else 15)
    h2.append(S.hits(S.top5(w, rng), Ba[t])); ls2.append(S.pl_logscore(Ba[t:t + 1], w)[0] - S.LOG_UNIF_ORD)
z2 = S.hits_z(h2); H["M2"] = (z2, one_sided_normal(z2, 1), f"mean hits={np.mean(h2):.4f} vs 0.7143, z={z2:+.2f}, ordered logscore gain={np.mean(ls2):+.4f}")
w_all = S.pl_fit(Ba, tr["M2"]["alpha"], iters=300)

# ---- P1 popularity holdout ----
def ylog(rows, key="w3"):
    return np.log(np.array([r[key] for r in rows], float) / np.array([r["deposits"] for r in rows]))


def demean_year(y, rows):
    yrs = np.array([r["date"].year for r in rows]); out = y.copy()
    for u in np.unique(yrs):
        out[yrs == u] -= out[yrs == u].mean()
    return out


yh = demean_year(ylog(hold_rows), hold_rows)
pred = Xh @ bt
o = corr(pred, yh); nul = np.array([corr(rng.permutation(pred), yh) for _ in range(R)])
H["P1"] = (o, mc_p(o, nul, "greater"), f"holdout corr(pred, actual)={o:+.3f}, R2={o*o:.3f}")
print("models done", round(time.time() - t0, 1), flush=True)

# ---- exploratory (not in Holm family): Friday heterogeneity, 4-hit prize vs popularity ----
expl = {}
lf = (ch["wd"] == 4).astype(int)
f = lambda l: S.chi2_homog(Bh, l); o = f(lf); nul = mcp(f, lf, 2000)
expl["friday_vs_other_holdout"] = f"chi2={o:.1f} df=34 (null {nul.mean():.1f}), p={mc_p(o, nul, 'greater'):.3f}, n_fri={lf.sum()}"
p4h = demean_year(np.log(np.array([r["p4"] for r in hold_rows])), hold_rows)
expl["holdout_corr(pred popularity, log 4-hit prize)"] = round(corr(pred, p4h), 3)
w4h = demean_year(ylog(hold_rows, "w4"), hold_rows)
expl["holdout_corr(pred popularity, log W4/dep)"] = round(corr(pred, w4h), 3)

# ---- assemble, Holm ----
ids = [h["id"] for h in pre["hypotheses"]]
names = {h["id"]: h["name"] for h in pre["hypotheses"]}
tp = np.array([tr[i]["p"] for i in ids]); hp = np.array([H[i][1] for i in ids])
th, hh = holm(tp), holm(hp)
table = []
for k, i in enumerate(ids):
    table.append(dict(id=i, name=names[i], train_effect=tr[i]["effect"], train_p=round(float(tp[k]), 4), train_p_holm=round(float(th[k]), 4),
                      holdout_effect=H[i][2], holdout_p=round(float(hp[k]), 4), holdout_p_holm=round(float(hh[k]), 4),
                      holdout_replicates=bool(hh[k] < 0.05), survives=bool(th[k] < 0.05 and hh[k] < 0.05)))
json.dump(dict(table=table, exploratory=expl, M1_hits=h1, M2_hits=h2, M2_w_all=w_all.tolist()), open(LAB + "/holdout_results.json", "w"), indent=1)
for t in table:
    print(f"{t['id']:5s} train p={t['train_p']:.4f} (holm {t['train_p_holm']:.3f}) | holdout p={t['holdout_p']:.4f} (holm {t['holdout_p_holm']:.3f}) {t['holdout_effect']}  survives={t['survives']}")
print(json.dumps(expl, indent=1))
